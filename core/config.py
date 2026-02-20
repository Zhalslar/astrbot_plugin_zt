from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from types import MappingProxyType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from astrbot.api import logger
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.star.context import Context

from .model import DisplayItem


class ConfigNode:
    """
    配置节点, 把 dict 变成强类型对象
    """

    _SCHEMA_CACHE: dict[type, dict[str, type]] = {}
    _FIELDS_CACHE: dict[type, set[str]] = {}

    @classmethod
    def _schema(cls) -> dict[str, type]:
        return cls._SCHEMA_CACHE.setdefault(cls, get_type_hints(cls))

    @classmethod
    def _fields(cls) -> set[str]:
        return cls._FIELDS_CACHE.setdefault(
            cls,
            {k for k in cls._schema() if not k.startswith("_")},
        )

    @staticmethod
    def _is_optional(tp: type) -> bool:
        if get_origin(tp) in (Union, UnionType):
            return type(None) in get_args(tp)
        return False

    def __init__(self, data: MutableMapping[str, Any]):
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_children", {})
        for key, tp in self._schema().items():
            if key.startswith("_"):
                continue
            if key in data:
                continue
            if hasattr(self.__class__, key):
                continue
            if self._is_optional(tp):
                continue
            logger.warning(f"[config:{self.__class__.__name__}] 缺少字段: {key}")

    def __getattr__(self, key: str) -> Any:
        if key in self._fields():
            value = self._data.get(key)
            tp = self._schema().get(key)

            if isinstance(tp, type) and issubclass(tp, ConfigNode):
                children: dict[str, ConfigNode] = self.__dict__["_children"]
                if key not in children:
                    if not isinstance(value, MutableMapping):
                        raise TypeError(
                            f"[config:{self.__class__.__name__}] "
                            f"字段 {key} 期望 dict，实际是 {type(value).__name__}"
                        )
                    children[key] = tp(value)
                return children[key]

            return value

        if key in self.__dict__:
            return self.__dict__[key]

        raise AttributeError(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self._fields():
            self._data[key] = value
            return
        object.__setattr__(self, key, value)

    def raw_data(self) -> Mapping[str, Any]:
        """
        底层配置 dict 的只读视图
        """
        return MappingProxyType(self._data)

    def save_config(self) -> None:
        """
        保存配置到磁盘（仅允许在根节点调用）
        """
        if not isinstance(self._data, AstrBotConfig):
            raise RuntimeError(
                f"{self.__class__.__name__}.save_config() 只能在根配置节点上调用"
            )
        self._data.save_config()


# ====================== 插件自定义配置 ======================


class PluginConfig(ConfigNode):
    only_admin: bool
    enable_list: list[str]

    def __init__(self, config: AstrBotConfig, context: Context):
        super().__init__(config)
        self.enable_items = self._parse_enable_items(self.enable_list)

    def _parse_enable_items(
        self, enable_items: list[str] | set[str]
    ) -> set[DisplayItem]:
        parsed_items: set[DisplayItem] = set()
        for item in enable_items:
            try:
                parsed_items.add(DisplayItem(item))
            except ValueError:
                logger.warning(
                    f"Unknown enable_items value ignored: {item}",
                )
        return parsed_items

    def is_enabled_item(self, item_name: DisplayItem) -> bool:
        return item_name in self.enable_items


from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.astr_message_event import AstrMessageEvent

from .core.config import PluginConfig
from .core.status_manager import StatusManager


class StatusPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.cfg = PluginConfig(config, context)
        self.status_manager = StatusManager(self.cfg)

    @filter.command("zt")
    async def get_zt(self, event: AstrMessageEvent):
        """获取并显示当前系统状态（精简版）"""
        if self.cfg.only_admin and not event.is_admin():
            return
        yield event.plain_result(self.status_manager.get_simple_status_text())

    @filter.command("状态")
    async def get_status(self, event: AstrMessageEvent):
        """获取并显示当前系统状态"""
        if self.cfg.only_admin and not event.is_admin():
            return
        sys_info = await self.status_manager.get_status_text()
        yield event.plain_result(sys_info)

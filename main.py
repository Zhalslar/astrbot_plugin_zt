from astrbot.api.star import Context, Star
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.astr_message_event import AstrMessageEvent
from astrbot.core.star.filter.permission import PermissionType

from .core.config import PluginConfig
from .core.status_manager import StatusManager


class StatusPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.cfg = PluginConfig(config, context)
        self.status_manager = StatusManager(self.cfg)

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("zt")
    async def get_zt(self, event: AstrMessageEvent):
        """获取并显示当前系统状态（精简版）"""
        sys_info = await self.status_manager.get_zt_text()
        yield event.plain_result(sys_info)

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("状态")
    async def get_zhuangtai(self, event: AstrMessageEvent):
        """获取并显示当前系统状态"""
        sys_info = await self.status_manager.get_zhuangtai_text()
        yield event.plain_result(sys_info)

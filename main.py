
import time

import psutil

from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.astr_message_event import AstrMessageEvent


class StatusPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.only_admin = config.get("only_admin", False)

    @filter.command("zt")
    async def get_zt(self, event: AstrMessageEvent):
        """获取并显示当前系统状态（精简版）"""
        if self.only_admin and not event.is_admin():
            return
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        sys_info = (f"CPU使用: {cpu_usage}%\n"
                    f"内存使用: {memory_info.percent}%")
        yield event.plain_result(sys_info)


    @filter.command("状态")
    async def get_status(self, event: AstrMessageEvent):
        """获取并显示当前系统状态"""
        if self.only_admin and not event.is_admin():
            return
        cpu_usage_str = self._get_average_cpu_usage(samples=3, interval=0.2)
        memory_usage_str = await self._get_memory_usage()
        disk_usage_str = self._get_disk_usage("/")
        net_info = psutil.net_io_counters()
        process_count = len(psutil.pids())
        net_connections = len(psutil.net_connections())

        sys_info = (
            f"CPU占用: {cpu_usage_str}\n"
            f"内存占用: {memory_usage_str}\n"
            f"磁盘占用: {disk_usage_str}\n"
            f"网络发送: {self._convert_to_readable(net_info.bytes_sent)}\n"
            f"网络接收: {self._convert_to_readable(net_info.bytes_recv)}\n"
            f"进程数量: {process_count}\n"
            f"连接数量: {net_connections}"
        )
        yield event.plain_result(sys_info)


    def _convert_to_readable(self, value):
        """根据数值大小动态选择合适的单位（GB、MB、KB 或 B）"""
        units = ["B", "KB", "MB", "GB"]
        unit_index = min(len(units) - 1, int(value > 0 and (value.bit_length() - 1) / 10))
        return f"{value / (1024**unit_index):.2f} {units[unit_index]}"


    async def _get_memory_usage(self):
        """获取并格式化显示内存使用情况"""
        memory_info = psutil.virtual_memory()
        used_memory_gb = memory_info.used / (1024**3)
        total_memory_gb = memory_info.total / (1024**3)
        return f"{used_memory_gb:.2f}G/{total_memory_gb:.1f}G"


    def _get_average_cpu_usage(self, samples=5, interval=0.5):
        """
        获取 CPU 使用率的平均值，并以指定格式返回。
        :param samples: 采样次数，默认为 5 次
        :param interval: 每次采样间隔时间（秒），默认为 0.5 秒
        :return: 平均 CPU 使用率（百分比）
        """
        total_usage = 0
        for _ in range(samples):
            cpu_usage = psutil.cpu_percent(interval=interval)
            total_usage += cpu_usage
            time.sleep(interval)
        average_usage = total_usage / samples
        return f"{average_usage:.2f}%"


    def _get_disk_usage(self, path="/"):
        """获取并格式化显示磁盘使用情况"""
        disk_info = psutil.disk_usage(path)
        used_disk_gb = disk_info.used / (1024**3)
        total_disk_gb = disk_info.total / (1024**3)
        return f"{used_disk_gb:.2f}G/{total_disk_gb:.1f}G"

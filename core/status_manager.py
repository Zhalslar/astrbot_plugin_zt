import datetime
import platform

import psutil

from astrbot.api import logger

from .config import PluginConfig
from .model import DisplayItem


class StatusManager:
    STATUS_GETTERS: tuple[tuple[DisplayItem, str], ...] = (
        (DisplayItem.OS_INFO, "_get_os_info"),
        (DisplayItem.HOSTNAME, "_get_hostname"),
        (DisplayItem.CPU_USAGE, "_get_cpu_usage"),
        (DisplayItem.MEMORY_USAGE, "_get_memory_usage"),
        (DisplayItem.SWAP_USAGE, "_get_swap_usage"),
        (DisplayItem.DISK_USAGE, "_get_disk_usage"),
        (DisplayItem.PROCESS_COUNT, "_get_process_count"),
        (DisplayItem.NETWORK_SENT, "_get_network_sent"),
        (DisplayItem.NETWORK_RECV, "_get_network_recv"),
        (DisplayItem.NETWORK_CONNECTIONS, "_get_network_connections"),
        (DisplayItem.UPTIME, "_get_uptime"),
    )

    def __init__(self, config: PluginConfig):
        self.cfg = config

    def get_zt_text(self) -> str:
        lines = [
            DisplayItem.CPU_USAGE.format_line(
                self._get_cpu_usage(samples=1, interval=1)
            ),
            DisplayItem.MEMORY_USAGE.format_line(
                self._get_memory_usage(as_percent=True)
            ),
        ]
        return "\n".join(lines)

    async def get_zhuangtai_text(self) -> str:
        sys_info_lines: list[str] = []
        for item, getter_name in self.STATUS_GETTERS:
            if not self.cfg.is_enabled_item(item):
                continue

            getter = getattr(self, getter_name)
            try:
                sys_info_lines.append(item.format_line(getter()))
            except Exception as err:
                logger.warning(
                    f"Failed to read status item {item.value}, skipped: {err}"
                )

        return (
            "\n".join(sys_info_lines)
            if sys_info_lines
            else DisplayItem.empty_status_text()
        )

    def _get_cpu_usage(self, samples: int = 5, interval: float = 0.5) -> str:
        total_usage = 0.0
        for _ in range(samples):
            total_usage += psutil.cpu_percent(interval=interval)
        average_usage = total_usage / samples
        return f"{average_usage:.2f}%"

    def _get_memory_usage(self, as_percent: bool = False) -> str:
        memory_info = psutil.virtual_memory()
        if as_percent:
            return f"{memory_info.percent:.2f}%"
        used_memory_gb = memory_info.used / (1024**3)
        total_memory_gb = memory_info.total / (1024**3)
        return f"{used_memory_gb:.2f}G/{total_memory_gb:.1f}G"

    def _get_swap_usage(self, as_percent: bool = False) -> str:
        swap_info = psutil.swap_memory()
        if as_percent:
            return f"{swap_info.percent:.2f}%"
        used_swap_gb = swap_info.used / (1024**3)
        total_swap_gb = swap_info.total / (1024**3)
        return f"{used_swap_gb:.2f}G/{total_swap_gb:.1f}G"

    def _get_disk_usage(self, path: str = "/") -> str:
        disk_info = psutil.disk_usage(path)
        used_disk_gb = disk_info.used / (1024**3)
        total_disk_gb = disk_info.total / (1024**3)
        return f"{used_disk_gb:.2f}G/{total_disk_gb:.1f}G"

    def _get_process_count(self) -> str:
        return str(len(psutil.pids()))

    def _get_network_sent(self) -> str:
        net_info = psutil.net_io_counters()
        return self._convert_to_readable(net_info.bytes_sent)

    def _get_network_recv(self) -> str:
        net_info = psutil.net_io_counters()
        return self._convert_to_readable(net_info.bytes_recv)

    def _get_network_connections(self) -> str:
        return str(len(psutil.net_connections()))

    def _get_os_info(self) -> str:
        return f"{platform.system()} {platform.release()}"

    def _get_hostname(self) -> str:
        return platform.node()

    def _get_uptime(self) -> str:
        seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _convert_to_readable(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        display_value = float(value)
        while display_value >= 1024 and unit_index < len(units) - 1:
            display_value /= 1024
            unit_index += 1
        return f"{display_value:.2f} {units[unit_index]}"

import datetime
import platform
import time
from collections.abc import Callable

import psutil

from astrbot.api import logger

from .config import PluginConfig
from .model import DisplayItem


class StatusManager:
    def __init__(self, config: PluginConfig):
        self.cfg = config
        self.status_getters: tuple[tuple[DisplayItem, Callable[[], str]], ...] = (
            (DisplayItem.OS_INFO, self._get_os_info),
            (DisplayItem.HOSTNAME, self._get_hostname),
            (DisplayItem.CPU_USAGE, self._get_cpu_usage),
            (DisplayItem.MEMORY_USAGE, self._get_memory_usage),
            (DisplayItem.SWAP_USAGE, self._get_swap_usage),
            (DisplayItem.DISK_USAGE, self._get_disk_usage),
            (DisplayItem.UPLOAD_USAGE, self._get_upload_usage),
            (DisplayItem.DOWNLOAD_USAGE, self._get_download_usage),
            (DisplayItem.PROCESS_COUNT, self._get_process_count),
            (DisplayItem.NETWORK_SENT, self._get_network_sent),
            (DisplayItem.NETWORK_RECV, self._get_network_recv),
            (DisplayItem.NETWORK_CONNECTIONS, self._get_network_connections),
            (DisplayItem.UPTIME, self._get_uptime),
        )

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
        dynamic_status: dict[DisplayItem, str] = {}
        dynamic_items = {
            DisplayItem.CPU_USAGE,
            DisplayItem.UPLOAD_USAGE,
            DisplayItem.DOWNLOAD_USAGE,
        }
        if any(self.cfg.is_enabled_item(item) for item in dynamic_items):
            dynamic_status = self._get_dynamic_status(samples=5, interval=0.5)

        for item, getter in self.status_getters:
            if not self.cfg.is_enabled_item(item):
                continue

            try:
                if item in dynamic_status:
                    value = dynamic_status[item]
                else:
                    value = getter()
                sys_info_lines.append(item.format_line(value))
            except Exception as err:
                logger.warning(
                    f"Failed to read status item {item.value}, skipped: {err}"
                )

        return (
            "\n".join(sys_info_lines)
            if sys_info_lines
            else DisplayItem.empty_status_text()
        )

    def _get_dynamic_status(
        self, samples: int = 1, interval: float = 1.0
    ) -> dict[DisplayItem, str]:
        net_before = psutil.net_io_counters()
        cpu_usage = self._get_cpu_usage(samples=samples, interval=interval)
        net_after = psutil.net_io_counters()
        duration = max(samples * interval, 0.001)
        bytes_sent_per_second = (
            max(net_after.bytes_sent - net_before.bytes_sent, 0) / duration
        )
        bytes_recv_per_second = (
            max(net_after.bytes_recv - net_before.bytes_recv, 0) / duration
        )
        return {
            DisplayItem.CPU_USAGE: cpu_usage,
            DisplayItem.UPLOAD_USAGE: self._format_speed(bytes_sent_per_second),
            DisplayItem.DOWNLOAD_USAGE: self._format_speed(bytes_recv_per_second),
        }

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

    def _get_upload_usage(self) -> str:
        upload_speed, _ = self._get_network_speed()
        return upload_speed

    def _get_download_usage(self) -> str:
        _, download_speed = self._get_network_speed()
        return download_speed

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

    def _get_network_speed(
        self, samples: int = 1, interval: float = 1.0
    ) -> tuple[str, str]:
        net_before = psutil.net_io_counters()
        time.sleep(samples * interval)
        net_after = psutil.net_io_counters()
        duration = max(samples * interval, 0.001)
        upload_speed = max(net_after.bytes_sent - net_before.bytes_sent, 0) / duration
        download_speed = max(net_after.bytes_recv - net_before.bytes_recv, 0) / duration
        return self._format_speed(upload_speed), self._format_speed(download_speed)

    def _convert_to_readable(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        display_value = float(value)
        while display_value >= 1024 and unit_index < len(units) - 1:
            display_value /= 1024
            unit_index += 1
        return f"{display_value:.2f} {units[unit_index]}"

    def _format_speed(self, value: float) -> str:
        return f"{self._convert_to_readable(int(value))}/s"

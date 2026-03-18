import asyncio
import datetime
import platform
import time
from collections.abc import Callable
from typing import TypeVar

import psutil

from astrbot.api import logger

from .config import PluginConfig
from .model import DisplayItem

T = TypeVar("T")


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
            (DisplayItem.NETWORK_USAGE, self._get_network_usage),
            (DisplayItem.NETWORK_TRAFFIC, self._get_network_traffic),
            (DisplayItem.PROCESS_COUNT, self._get_process_count),
            (DisplayItem.NETWORK_CONNECTIONS, self._get_network_connections),
            (DisplayItem.UPTIME, self._get_uptime),
        )

    async def get_zt_text(self) -> str:
        return await asyncio.to_thread(self._build_zt_text)

    def _build_zt_text(self) -> str:
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
        return await asyncio.to_thread(self._build_zhuangtai_text)

    def _build_zhuangtai_text(self) -> str:
        sys_info_lines: list[str] = []

        for item, getter in self.status_getters:
            if not self.cfg.is_enabled_item(item):
                continue

            try:
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

    def _get_os_info(self) -> str:
        return f"{platform.system()} {platform.release()}"

    def _get_hostname(self) -> str:
        return platform.node()

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

    def _get_network_usage(self) -> str:
        net_before = psutil.net_io_counters()
        start_time = time.monotonic()
        time.sleep(1.0)
        duration = max(time.monotonic() - start_time, 0.001)
        net_after = psutil.net_io_counters()
        bytes_sent = float(max(net_after.bytes_sent - net_before.bytes_sent, 0))
        bytes_recv = float(max(net_after.bytes_recv - net_before.bytes_recv, 0))
        upload_speed = f"{self._convert_to_readable(bytes_sent / duration, 1)}"
        download_speed = f"{self._convert_to_readable(bytes_recv / duration, 1)}"
        return f"↑{upload_speed}↓{download_speed}"

    def _get_network_traffic(self) -> str:
        net_info = psutil.net_io_counters()
        sent = self._convert_to_readable(net_info.bytes_sent, 1)
        recv = self._convert_to_readable(net_info.bytes_recv, 1)
        return f"↑{sent}↓{recv}"

    def _get_process_count(self) -> str:
        return str(len(psutil.pids()))

    def _get_network_connections(self) -> str:
        return str(len(psutil.net_connections()))

    def _get_uptime(self) -> str:
        seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        if days > 0:
            return f"{days}天{hours}时{minutes}分"
        if hours > 0:
            return f"{hours}时{minutes}分"
        return f"{minutes}分"

    def _convert_to_readable(self, value: float, decimals: int = 2) -> str:
        units = ["B", "K", "M", "G", "T"]
        unit_index = 0
        display_value = float(value)

        while display_value >= 1024 and unit_index < len(units) - 1:
            display_value /= 1024
            unit_index += 1

        formatted = f"{display_value:.{decimals}f}".rstrip("0").rstrip(".")
        return f"{formatted}{units[unit_index]}"

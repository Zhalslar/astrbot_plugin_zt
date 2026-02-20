import psutil

from astrbot.api import logger

from .config import PluginConfig
from .model import DisplayItem


class StatusManager:
    STATUS_GETTERS: tuple[tuple[DisplayItem, str], ...] = (
        (DisplayItem.CPU_USAGE, "_get_cpu_usage"),
        (DisplayItem.MEMORY_USAGE, "_get_memory_usage"),
        (DisplayItem.DISK_USAGE, "_get_disk_usage"),
        (DisplayItem.PROCESS_COUNT, "_get_process_count"),
        (DisplayItem.NETWORK_SENT, "_get_network_sent"),
        (DisplayItem.NETWORK_RECV, "_get_network_recv"),
        (DisplayItem.NETWORK_CONNECTIONS, "_get_network_connections"),
    )

    def __init__(self, config: PluginConfig):
        self.cfg = config

    def get_simple_status_text(self) -> str:
        lines = [
            DisplayItem.CPU_USAGE.format_line(
                self._get_cpu_usage(samples=1, interval=1)
            ),
            DisplayItem.MEMORY_USAGE.format_line(self._get_memory_usage()),
        ]
        return "\n".join(lines)

    async def get_status_text(self) -> str:
        sys_info_lines: list[str] = []
        for item, getter_name in self.STATUS_GETTERS:
            if not self.cfg.is_enabled_item(item):
                continue
            getter = getattr(self, getter_name)
            try:
                sys_info_lines.append(item.format_line(getter()))
            except (PermissionError, psutil.AccessDenied, OSError) as err:
                logger.warning(
                    f"Failed to read status item {item.value}, skipped: {err}"
                )
                continue

        return (
            "\n".join(sys_info_lines)
            if sys_info_lines
            else DisplayItem.empty_status_text()
        )

    def _get_cpu_usage(self, samples: int = 5, interval: float = 0.5) -> str:
        total_usage = 0.0
        for _ in range(samples):
            cpu_usage = psutil.cpu_percent(interval=interval)
            total_usage += cpu_usage
        average_usage = total_usage / samples
        return f"{average_usage:.2f}%"

    def _get_memory_usage(self) -> str:
        memory_info = psutil.virtual_memory()
        used_memory_gb = memory_info.used / (1024**3)
        total_memory_gb = memory_info.total / (1024**3)
        return f"{used_memory_gb:.2f}G/{total_memory_gb:.1f}G"

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

    def _convert_to_readable(self, value: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        unit_index = min(
            len(units) - 1,
            int(value > 0 and (value.bit_length() - 1) / 10),
        )
        return f"{value / (1024**unit_index):.2f} {units[unit_index]}"

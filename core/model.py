from enum import Enum


class DisplayItem(str, Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_SENT = "network_sent"
    NETWORK_RECV = "network_recv"
    PROCESS_COUNT = "process_count"
    NETWORK_CONNECTIONS = "network_connections"

    def label(self) -> str:
        labels = {
            self.CPU_USAGE: "CPU占用",
            self.MEMORY_USAGE: "内存占用",
            self.DISK_USAGE: "磁盘占用",
            self.NETWORK_SENT: "网络发送",
            self.NETWORK_RECV: "网络接收",
            self.PROCESS_COUNT: "进程数量",
            self.NETWORK_CONNECTIONS: "连接数量",
        }
        return labels[self]

    def format_line(self, value: str) -> str:
        return f"{self.label()}: {value}"

    @classmethod
    def empty_status_text(cls) -> str:
        return "未启用任何状态显示项"

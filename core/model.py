from enum import Enum


class DisplayItem(str, Enum):
    OS_INFO = "os_info"
    HOSTNAME = "hostname"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    SWAP_USAGE = "swap_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_SENT = "network_sent"
    NETWORK_RECV = "network_recv"
    PROCESS_COUNT = "process_count"
    NETWORK_CONNECTIONS = "network_connections"
    UPTIME = "uptime"

    def label(self) -> str:
        labels = {
            self.OS_INFO: "系统信息",
            self.HOSTNAME: "主机名称",
            self.CPU_USAGE: "CPU占用",
            self.MEMORY_USAGE: "内存占用",
            self.SWAP_USAGE: "交换内存",
            self.DISK_USAGE: "磁盘占用",
            self.NETWORK_SENT: "网络发送",
            self.NETWORK_RECV: "网络接收",
            self.PROCESS_COUNT: "进程数量",
            self.NETWORK_CONNECTIONS: "连接数量",
            self.UPTIME: "开机时长",
        }
        return labels[self]

    def format_line(self, value: str) -> str:
        return f"{self.label()}: {value}"

    @classmethod
    def empty_status_text(cls) -> str:
        return "未启用任何状态显示项"

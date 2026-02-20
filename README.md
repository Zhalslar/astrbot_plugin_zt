
<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_zt?name=astrbot_plugin_zt&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_zt

_✨ 简易版状态插件 ✨_  

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Zhalslar-blue)](https://github.com/Zhalslar)

</div>

## 🤝 介绍

简易版服务器状态插件, 因为检测过程几乎不消耗性能，所以得到的数据准确性更高

## 📦 安装

在astrbot的插件市场搜索astrbot_plugin_zt，点击安装即可

## ⌨️ 使用说明

### 命令表

|     命令      |                    说明                    |
|:-------------:|:-----------------------------------------------:|
| zt  | 只展示服务器的cpu占用、内存占用 |
| 状态   |   以文字形式显示服务器的详细参数  |

## ⚙️ 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|:-------|:-----|:-------|:-----|
| `only_admin` | bool | `false` | 仅管理员可用本插件命令 |
| `zhuangtai_show_list` | list | `["cpu_usage(CPU占用)", "memory_usage(内存占用)", "disk_usage(磁盘占用)", "swap_usage(交换内存)", "network_sent(网络发送)", "network_recv(网络接收)", "uptime(开机时长)"]` | 状态显示项，可选值见下表 |

### 可选显示项

| 值 | 说明 | 数据示例 |
|:---|:-----|:---------|
| `os_info` | 系统信息 | `Linux 5.15.0` |
| `hostname` | 主机名称 | `VM-12-4-ubuntu` |
| `cpu_usage` | CPU占用 | `12.50%` |
| `memory_usage` | 内存占用 | `3.25G/15.6G` 或 `20.80%` |
| `swap_usage` | 交换内存 | `0.50G/2.0G` 或 `25.00%` |
| `disk_usage` | 磁盘占用 | `45.20G/100.0G` |
| `network_sent` | 网络发送 | `1.25 GB` |
| `network_recv` | 网络接收 | `5.60 GB` |
| `process_count` | 进程数量 | `128` |
| `network_connections` | 连接数量 | `45` |
| `uptime` | 开机时长 | `15d 3h 24m` |


### 示例图

## 👥 贡献指南

- 🌟 Star 这个项目！（点右上角的星星，感谢支持！）
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 📌 注意事项

- 想第一时间得到反馈的可以来作者的插件反馈群（QQ群）：460973561（不点star不给进）

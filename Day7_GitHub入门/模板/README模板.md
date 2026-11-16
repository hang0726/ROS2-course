# 我的 ROS2 课程（11–12 月目标）

> 一门从零开始的 ROS2 实战课程，覆盖：安装 → 通信机制 → 工程化 → Nav2 建图导航 → 实战三节点 → GitHub。

## 课程目标（5 个）
1. 装 ROS2 Humble（WSL2 为主，虚拟机备选）
2. 官方教程跑通 publisher / subscriber 节点
3. 跑通 Nav2：建图 → 保存地图 → 导航到目标点
4. 写 3 个 Python 节点：发导航目标 / 订阅里程计 / 发速度指令
5. 注册 GitHub，建第一个仓库

## 目录结构
| 文件夹 | 内容 |
|---|---|
| `Day1_安装ROS2Humble` | 安装指南 + 环境检查脚本 |
| `Day2_PubSub节点` | 发布者/订阅者节点 + 官方风格模板 |
| `Day3_工程化ColconLaunch` | Colcon 包 / launch / 服务参数模板 |
| `Day4_Nav2建图` | SLAM Toolbox 建图 + 启动脚本 |
| `Day5_Nav2导航` | 保存地图 + AMCL + 导航到目标 |
| `Day6_实战三节点` | 三个核心 Python 节点 |
| `Day7_GitHub入门` | 注册、建仓、提交代码 |

## 快速开始
```bash
source /opt/ros/humble/setup.bash
cd /mnt/d/具身智能求职培训
# 按 Day1→Day7 顺序学习，每个 Day 里有 笔记.md 和可直接运行的 .py
```

---
*课程代码遵循：每个 Day 一份 笔记.md（目标+知识点+踩坑+跑通清单+自查3问）+ 带逐行中文注释的 .py + 模板/。*

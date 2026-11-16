# 我的 ROS2 七天速成课程

> 从零开始的 ROS2 实战课程：安装 → 通信机制 → 工程化 → Nav2 建图导航 → 实战三节点 → GitHub 存档。
> 环境：WSL2 Ubuntu 22.04 + ROS2 Humble（Gazebo / SLAM Toolbox / AMCL / Nav2）。

## 课程进度

| Day | 内容 | 状态 |
|---|---|---|
| Day1 | 安装 ROS2 Humble + 环境自检 | ✅ |
| Day2 | publisher / subscriber 节点 | ✅ |
| Day3 | Colcon 工程包 / launch / 服务与参数 | ✅ |
| Day4 | SLAM Toolbox 建图 + 保存地图 | ✅ |
| Day5 | AMCL 定位 + Nav2 导航到目标点 | ✅ |
| Day6 | 手写 3 个 Python 节点（Action / Sub / Pub） | ✅ 已实跑通过 |
| Day7 | Git + GitHub 存档 | 进行中 |

## 目录结构

| 文件夹 | 内容 |
|---|---|
| `Day1_安装ROS2Humble` | 安装指南 + 环境检查脚本 |
| `Day2_PubSub节点` | 发布者/订阅者节点 + 官方风格模板 |
| `Day3_工程化ColconLaunch` | Colcon 包 / launch / 服务参数模板 |
| `Day4_Nav2建图` | SLAM Toolbox 建图 + 启动脚本 |
| `Day5_Nav2导航` | 保存地图 + AMCL + 导航到目标 |
| `Day6_实战三节点` | 三个核心 Python 节点 + 全注释练习 + 标准答案 |
| `Day7_GitHub入门` | 注册、建仓、提交代码 |

## 快速开始

```bash
source /opt/ros/humble/setup.bash
cd /mnt/d/ROS2七天速成
# 按 Day1 -> Day7 顺序学习，每个 Day 里有 笔记.md 和可直接运行的 .py
```

> ⚠️ WSL 里跑代码务必显式带上 `source /opt/ros/humble/setup.bash` 和 `cd`，否则会 import 不到 rclpy。

---

*课程格式：每个 Day 一份 `笔记.md`（目标 + 知识点 + 踩坑 + 跑通清单 + 自查 3 问）+ 带逐行中文注释的 `.py` + `模板/`。Day6 起练习为全注释模板，讲解写在标准答案的代码注释里。*

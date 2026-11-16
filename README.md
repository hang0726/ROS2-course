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
| Day7 | Git + GitHub 存档 | ✅ 已推送到 GitHub |

## 真机阶段 Day8–13（具身智能求职 · 进阶）

> 从仿真迁移到 RK3528 真车，按卖家官方视频拆成 6 天，每天一个主题，不要一天干完。

| Day | 主题 | 状态 |
|---|---|---|
| Day8 | 真机硬件 + 网页中控台 | ⬜ |
| Day9 | 底盘通信 + 话题自检 | ⬜ |
| Day10 | TF + 雷达 + Gmapping 建图 | ⬜ |
| Day11 | AMCL + Nav2 真机导航 | ⬜ |
| Day12 | 原理强化（里程计/差速/PID，Python） | ⬜ |
| Day13 | 面试作品（demo + benchmark + GitHub） | ⬜ |

> ⏸️ C++ 话题通讯放在 `_附录_C++暂缓/`，当前主攻 Python。完整六天路线见 `Day13_面试作品/视频课程对照与学习路线.md`。

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
| `Day8_真机硬件与中控台` | 硬件认识 + SSH + ros2_web 中控台（含资料索引） |
| `Day9_底盘通信与自检` | 一键环境自检脚本 + 底盘话题打通 |
| `Day10_TF雷达与建图` | TF 树 + 雷达 + Gmapping 完整建图 |
| `Day11_真机导航` | AMCL 初始位姿 + Nav2 Goal |
| `Day12_原理强化Python` | 里程计/差速/PID 两个节点 + benchmark 采样 |
| `Day13_面试作品` | 作品 README 模板 + 六天路线总览 |
| `_附录_C++暂缓` | C++ 话题通讯实战（暂缓，先用 Python） |

## 快速开始

```bash
source /opt/ros/humble/setup.bash
cd /mnt/d/ROS2七天速成
# 按 Day1 -> Day7 顺序学习；真机阶段 Day8 -> Day13 在进阶章节
# 每个 Day 里有 笔记.md 和可直接运行的 .py
```

> ⚠️ WSL 里跑代码务必显式带上 `source /opt/ros/humble/setup.bash` 和 `cd`，否则会 import 不到 rclpy。

---

*课程格式：每个 Day 一份 `笔记.md`（目标 + 知识点 + 踩坑 + 跑通清单 + 自查 3 问）+ 带逐行中文注释的 `.py` + `模板/`。Day6 起练习为全注释模板，讲解写在标准答案的代码注释里。*

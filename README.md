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

## 昇腾机器人阶段 Day8–13（具身智能求职 · 进阶）

> 🎉 **2026-11-18 设备升级**：真机阶段从 RK3528 小车整体切换到**华为昇腾移动机器人 [探梦 JC-AR-V2]**
> （昇腾310B NPU + 6轴机械臂 + 3D相机 + 麦轮 + 雷达 + 语音）。旧小车课程已备份到 `D:\ROS2Course\backup_day8to13_rk3528_20261118`。
> 按官方 34 个实验拆成 6 天。总纲见 `Day8_昇腾平台与CANN环境/课程总纲_昇腾版.md`。

| Day | 主题 | 官方实验 | 状态 |
|---|---|---|---|
| Day8 | 昇腾平台认识 + CANN/MindSpore/ATC 环境 | 1/16-19 | ⬜ |
| Day9 | ROS2 底盘 + 麦轮运动学 + 话题/服务 | 20-23/25 | ⬜ |
| Day10 | 感知（雷达/OpenCV/目标检测）+ SLAM 建图 | 6/7/9-15/27-30 | ⬜ |
| Day11 | 路点导航 + MoveIt 机械臂 + 手眼标定 | 24/26/29/31 | ⬜ |
| Day12 | 昇腾AI部署（MindSpore→ATC→AscendCL）+ 视觉抓取 | 8/18/19/32/33 | 🔴 当前主攻 |
| Day13 | 语音交互 + 自动搬运 + 面试作品 | 2-5/34 | ⬜ |

> 🔴 手上只有设备箱，官方命令/私有路径标 `【待材料】`，等材料到了填；代码框架用公开生态写实。
> 💡 昇腾 AscendCL 是 C++ —— 学 AI 部署顺带补上 C++ 硬缺口，一举两得。

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
| `Day8_昇腾平台与CANN环境` | 平台认识 + 昇腾AI栈 + 环境自检脚本 + 课程总纲 |
| `Day9_ROS2底盘与通信` | 麦轮运动学 + 夹爪服务 + 底盘自检 |
| `Day10_感知与SLAM建图` | OpenCV三层感知 + 目标检测 + SLAM + 地图质量分析 |
| `Day11_导航与机械臂` | 路点导航 + MoveIt + 手眼标定讲透 |
| `Day12_昇腾AI部署与抓取` | MindSpore→ATC→AscendCL + 视觉引导抓取 + benchmark |
| `Day13_语音综合与作品` | 语音→意图→动作全链路 + 自动搬运 + 作品模板 |
| `_附录_C++暂缓` | 旧 C++ 话题通讯材料（昇腾 AscendCL 出来后，C++ 缺口由 Day12 补） |

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

# 项目名：基于 RK3528 移动机器人的 Sim2Real 导航链路实现与误差评估

> 这是你准备放到 GitHub 的作品仓库 README 模板。
> 用法：新建仓库，把本文件复制过去，按 `[ ]` 提示逐条替换成你自己的内容。
> 目标：让面试官 30 秒内看懂「你做了什么、结果如何、代码在哪」。

---

## 一句话简介

把一个 ROS2 Humble 的建图→定位→导航链路，从 Gazebo 仿真迁移到 RK3528 板载 Ubuntu 真机，
用同一套自写节点在两种环境各跑 5 次，量化到达误差与耗时，产出可复现的 Sim2Real 对比。

---

## 效果演示

- [ ] 贴 demo 视频链接（B 站 / 图床），30 秒：建图 → 导航 → 车走到目标
- [ ] 贴一张网页中控台截图（ros2_web）
- [ ] 贴一张仿真 vs 真机轨迹对比图（可选）

> 没有视频的作品集，说服力减半。先录再写。

---

## 硬件与软件环境

| 项 | 仿真侧 | 真机侧 |
|---|---|---|
| 平台 | WSL2 Ubuntu 22.04 + Gazebo | RK3528 四核 A53 / 2GB / Ubuntu |
| ROS 版本 | Humble | Humble |
| 建图 | slam_toolbox | slam_gmapping |
| 定位 | AMCL | AMCL |
| 导航 | nav2_bringup | xuegecar_navigation2 |
| 可视化 | RViz | ros2_web 网页中控台（Vue3 + Foxglove） |

---

## 我做了什么

1. [ ] 复现 Day1–7 完整 ROS2 链路（安装 / PubSub / Colcon / 建图 / 导航 / 三节点 / Git）
2. [ ] 把链路迁移到真机：适配话题名、TF 树、超高帧率雷达配置
3. [ ] 手写 3 个 Python 节点：导航目标客户端（Action）/ 里程计订阅 / 速度指令发布
4. [ ] 写 benchmark 采样脚本，同目标点仿真与真机各跑 5 次
5. [ ] 用网页中控台封装操作界面，录 demo

---

## Benchmark 结果

| 场景 | 次数 | 成功率 | 平均误差 (m) | 平均耗时 (s) |
|---|---|---|---|---|
| Gazebo 仿真 | 5 | [ ] | [ ] | [ ] |
| RK3528 真机 | 5 | [ ] | [ ] | [ ] |

> 数据来自 `模板/Day8_benchmark采样.py`，原始 CSV 见 `benchmark记录表.md`。
> 误差 = 目标点与 /amcl_pose 实际到达点的平面欧氏距离。

**结论**（一句话，别堆数据）：[ ] 例：真机误差比仿真高约 X cm，主要来自里程计累积误差与地面摩擦差异。

---

## 仓库结构

```
├── 笔记.md                    # 六阶段上车流程
├── 资料索引.md                # 出云开源资料全集
├── 模板/
│   ├── Day8_真机环境自检.sh    # SSH 上车一键体检
│   ├── Day8_benchmark采样.py  # 导航误差自动采样
│   └── ros_config_示例.json   # 中控台配置示例
├── benchmark记录表.md          # 原始数据
└── README.md                  # 本文件
```

---

## 怎么复现

```bash
# 1. 仿真侧（WSL2）
source /opt/ros/humble/setup.bash
# 按 Day5 起导航栈，RViz 给 2D Pose Estimate
python3 模板/Day8_benchmark采样.py 仿真 0.5 0.0 0.0

# 2. 真机侧（SSH 上车）
ssh <用户名>@<车IP>
bash 模板/Day8_真机环境自检.sh
python3 模板/Day8_benchmark采样.py 真机 0.5 0.0 0.0
```

---

## 踩过的坑

- [ ] 建图只建了一小片 → 必须走遍整个房间再存图
- [ ] 目标被拒（状态码 6 / ABORTED）→ 先给 AMCL 初始位姿，别越出地图边界
- [ ] /cmd_vel 冲突 → 自写速度节点和 Nav2 不能同时发
- [ ] ROS_DOMAIN_ID 串台 → 车和 PC 用不同 domain
- [ ] 更多见 `笔记.md` 第三节

---

## 声明

本项目基于出云科技 LEAP ROS2 开源平台，仅用于学习与交流，不作商业用途。
原始开源资料版权归原作者所有：https://github.com/czu963889306-dev

#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# Day6 模板 · 动手前的环境自检（只读，不改任何东西）
# 用法： bash "/mnt/d/ROS2七天速成/Day6_实战三节点/模板/Day6_环境自检.sh"
# 什么时候跑：Day5 导航栈已经在另一个窗口跑起来之后、写节点之前。
# ============================================================

# 故意不开 set -e / set -u：ROS2 的 setup.bash 会引用未定义变量
source /opt/ros/humble/setup.bash

echo "===== 1) ROS2 环境 ====="
echo "ROS_DISTRO = ${ROS_DISTRO:-<空，没 source 到>}"
echo
echo "===== 2) 导航 action 服务端（节点①需要）====="
if ros2 action list 2>/dev/null | grep -q "navigate_to_pose"; then
    echo "✅ /navigate_to_pose 在线"
else
    echo "❌ /navigate_to_pose 不在线 → 先用桌面 bat 选 [4] 起 Day5 导航栈"
    echo "   并在 RViz 里点 2D Pose Estimate 给 AMCL 初始位姿"
fi
echo
echo "===== 3) 里程计话题（节点②需要）====="
ros2 topic list 2>/dev/null | grep -i odom || echo "❌ 没有任何 odom 话题 → Gazebo 没起来？"
echo "   （本机 TB3 仿真是 /odom；odom_subscriber.py 默认已改成它）"
echo
echo "===== 4) 速度指令话题（节点③需要）====="
if ros2 topic list 2>/dev/null | grep -q '^/cmd_vel$'; then
    echo "✅ /cmd_vel 存在"
else
    echo "⚠️ 暂没看到 /cmd_vel（Nav2 空闲时可能还没发布，车动起来后就有）"
fi
echo
echo "===== 5) 三条运行命令（分别在 3 个终端里跑）====="
echo '  cd /mnt/d/ROS2七天速成/Day6_实战三节点'
echo '  python3 练习/my_send_nav_goal.py 0.5 0.0 0.0'
echo '  python3 odom_subscriber.py'
echo '  python3 velocity_commander.py'
echo
echo "⚠️ 节点③和正在导航的 Nav2 会抢 /cmd_vel，别同时跑。"
echo "   想看真实话题名： ros2 topic list | grep -E 'odom|cmd_vel'"

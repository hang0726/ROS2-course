#!/usr/bin/env bash
# -*- coding: utf-8 -*-
"""
Day8_真机环境自检.sh —— SSH 上车后跑的一次性体检脚本

用法：
    ssh <用户名>@<车IP>
    bash Day8_真机环境自检.sh

检查 5 项：
    1. ROS2 发行版是否 humble
    2. 底盘关键话题 /cmd_vel /odom /scan /battery 是否齐全
    3. TF 树是否生成（frames.pdf）
    4. 雷达串口 / 摄像头设备节点是否就位
    5. ROS_DOMAIN_ID 是否与你的 PC 隔离

🔴 不要加 set -u：ROS2 setup.bash 会引用未定义变量，
   nounset 会让脚本假退出（Day4 踩过这个坑）。
"""

# source ROS2 环境（车上若已写进 ~/.bashrc，这行幂等无害）
source /opt/ros/humble/setup.bash

# 车的 ROS2 工作空间若已编译，补 source 它；没有就跳过
if [ -f "$HOME/chuyun_ws/install/setup.bash" ]; then
    source "$HOME/chuyun_ws/install/setup.bash"
fi

echo "====== Day8 真机环境自检 ======"
echo "ROS_DISTRO    = ${ROS_DISTRO:-<未设置>}"
echo "ROS_DOMAIN_ID = ${ROS_DOMAIN_ID:-<未设置，默认 0>}"

# --- 检查 1：列出全部话题，先看个全貌 ---
echo ""
echo "[1/5] 当前话题清单："
ros2 topic list

# --- 检查 2：逐个探测关键话题 ---
echo ""
echo "[2/5] 关键话题探测："
for t in /cmd_vel /odom /scan /battery; do
    # 用精确匹配，避免 /odom_combined 被当成 /odom
    if ros2 topic list | grep -qx "$t"; then
        echo "  [OK]   $t"
    else
        echo "  [MISS] $t  <- 检查底盘/雷达节点是否启动"
    fi
done

# --- 检查 3：生成 TF 树，人工看 frames.pdf ---
echo ""
echo "[3/5] 生成 TF 树（当前目录 frames.pdf）："
ros2 run tf2_tools view_frames || echo "  [WARN] TF 生成失败，检查 tf2_tools 是否安装"

# --- 检查 4：设备节点 ---
echo ""
echo "[4/5] 串口 / 视频设备："
ls /dev/ttyUSB* /dev/ttyACM* /dev/video* 2>/dev/null \
    || echo "  [WARN] 没找到雷达串口或摄像头，检查接线"

# --- 检查 5：Domain 隔离提醒 ---
echo ""
echo "[5/5] Domain 隔离：车上 ROS_DOMAIN_ID = ${ROS_DOMAIN_ID:-0}"
echo "  请确认你 PC / WSL2 的 ROS_DOMAIN_ID 与上面不同，否则两边话题会串台。"

echo ""
echo "====== 自检结束 ======"
echo "下一步：对照 笔记.md 阶段 1「通底盘」继续。"

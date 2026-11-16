#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Day1 模板 · 环境检查脚本（无需 ROS2 也能跑）
# 用途：装机后一键核对 WSL2 发行版 + ROS2 环境是否就位。
# 用法：
#     bash /mnt/d/具身智能求职培训/Day1_安装ROS2Humble/模板/env_check.sh

echo "===== 1. Ubuntu 版本（应为 22.04）====="
lsb_release -a 2>/dev/null | grep "Release" || cat /etc/os-release | grep VERSION=

echo ""
echo "===== 2. ROS2 环境变量 ====="
if [ -n "$ROS_DISTRO" ]; then
    echo "ROS_DISTRO = $ROS_DISTRO   ✅ 已 source 环境"
else
    echo "ROS_DISTRO 为空 ⚠️  请先: source /opt/ros/humble/setup.bash（或重开终端）"
fi

echo ""
echo "===== 3. ros2 命令是否可用 ====="
if command -v ros2 >/dev/null 2>&1; then
    echo "ros2 存在 ✅"
    echo "ROS 发行版: $ROS_DISTRO"
    dpkg -l ros-humble-desktop 2>/dev/null | awk '/^ii/{print "  已装版本:", $3}'
else
    echo "ros2 不存在 ⚠️  ROS2 未安装或未 source"
fi

echo ""
echo "===== 4. 关键包是否存在 ====="
for p in ros-humble-desktop ros-dev-tools; do
    if dpkg -l | grep -q "$p"; then
        echo "$p ✅"
    else
        echo "$p ⚠️  未安装（sudo apt install -y $p）"
    fi
done

echo ""
echo "===== 5. locale（应为 en_US.UTF-8）====="
locale | grep LANG

echo ""
echo "===== 6. ~/.bashrc 是否自动 source ROS2 ====="
if grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc 2>/dev/null; then
    echo "已写入 ~/.bashrc ✅"
else
    echo "未写入 ~/.bashrc ⚠️  新终端不会自动加载 ROS2"
fi

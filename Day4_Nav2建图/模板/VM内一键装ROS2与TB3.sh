#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# Day4 · VM(Ubuntu 22.04 桌面) 内一键装 ROS2 Humble + TB3 建图环境
# ------------------------------------------------------------
# 为什么用 VM：现有 WSL 装了 Gazebo Garden(gz-sim7/gz-tools2)，
#   与 TB3 需要的 Gazebo Classic 11 硬冲突，所以课程单独放干净 VM。
#
# 用法（在 VM 的 Ubuntu 终端里）：
#   cd ~/具身智能求职培训/Day4_Nav2建图/模板
#   bash VM内一键装ROS2与TB3.sh
# 全程约 20~40 分钟（看网速）；跑完重开终端或 source ~/.bashrc
# ============================================================

set -e                      # 任一步失败就停，避免装出半成品
export DEBIAN_FRONTEND=noninteractive

# ---- 0. root 直接跑；普通用户用 sudo ----
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
    command -v sudo >/dev/null 2>&1 || { echo "❌ 需要 sudo，请先 apt install sudo"; exit 1; }
fi

echo "===== [1/6] 设置 locale（ROS2 强制要求 UTF-8） ====="
$SUDO apt-get update -y
$SUDO apt-get install -y locales curl gnupg lsb-release ca-certificates
$SUDO locale-gen en_US en_US.UTF-8
$SUDO update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "===== [2/6] 加入 ROS2 apt 源（中科大镜像，国内快） ====="
if [ ! -f /etc/apt/sources.list.d/ros2.list ]; then
    $SUDO curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.ustc.edu.cn/ros2/ubuntu jammy main" \
        | $SUDO tee /etc/apt/sources.list.d/ros2.list > /dev/null
    echo "ROS2 源已写入（USTC 镜像）"
else
    echo "ros2.list 已存在，跳过"
fi

echo "===== [3/6] 装 ROS2 Humble 桌面版 + 开发工具（约 1~2GB） ====="
$SUDO apt-get update -y
$SUDO apt-get install -y ros-humble-desktop ros-dev-tools

echo "===== [4/6] 装 Day4 建图全家桶（含 Gazebo Classic 11） ====="
# 干净 VM 里没有 gz-tools2，gazebo 11 能正常装上 —— 这正是换 VM 的意义。
# ⚠️ 之后别在 VM 里装任何 gz-* 新版 Gazebo，否则又会冲突。
$SUDO apt-get install -y \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-gazebo \
    ros-humble-turtlebot3-teleop \
    ros-humble-slam-toolbox \
    ros-humble-nav2-bringup \
    ros-humble-navigation2

# VMware 图形增强：3D 加速 / 自适应分辨率 / 共享文件夹 / 剪贴板
$SUDO apt-get install -y open-vm-tools open-vm-tools-desktop

echo "===== [5/6] 写 ~/.bashrc（自动 source + TB3 型号） ====="
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc <<'EOF'

# >>> ROS2 课程环境 (Day4) >>>
source /opt/ros/humble/setup.bash
export ROS_DISTRO=humble
export TURTLEBOT3_MODEL=waffle
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
# <<< ROS2 课程环境 (Day4) <<<
EOF
    echo "~/.bashrc 已追加 ROS2 环境"
else
    echo "~/.bashrc 已有 ROS2 source，跳过"
fi

echo "===== [6/6] 验证安装 ====="
source /opt/ros/humble/setup.bash
echo "ROS2:      $(ros2 --version 2>/dev/null || echo '未找到')"
echo "Gazebo:    $(gazebo --version 2>/dev/null | head -1 || echo '未找到')"
echo "TB3 世界:  $(ros2 pkg prefix turtlebot3_gazebo 2>/dev/null || echo '未找到')"
echo "SLAM:      $(ros2 pkg prefix slam_toolbox 2>/dev/null || echo '未找到')"
echo ""
echo "🎉 装完了！重开终端（或 source ~/.bashrc），然后跑 Day4 三终端："
echo "   终端1: bash 启动建图.sh"
echo "   终端2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true"
echo "   终端3: ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz"
echo "          ros2 run turtlebot3_teleop teleop_keyboard"
echo ""
echo "⚠️ 若 Gazebo 黑屏，先确认 VM 设置勾了「加速 3D 图形」；"
echo "   仍不行就 export LIBGL_ALWAYS_SOFTWARE=1 再跑。"

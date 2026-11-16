#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# ROS2 课程环境 · 一键安装（在【课程专用】Ubuntu 22.04 里跑）
# ------------------------------------------------------------
# 适用范围：干净的 Ubuntu 22.04 jammy
#   - 主路线：WSL2 发行版 ROS2Course（见 ROS2课程_长期环境方案.md）
#   - 备选：VMware VM（此脚本同样适用，VM 侧另外装 open-vm-tools 即可）
#
# ⚠️ 千万不要在「论文/研究」那个 WSL 里跑这个！
#    那里装了 Gazebo Garden(gz-tools2)，与本脚本的 Gazebo Classic 11 硬冲突。
#    两套环境物理隔离，见长期方案文档。
#
# ⚠️ 必须用【普通用户】跑，不要用 root！
#    脚本末尾会写 ~/.bashrc，root 跑会写进 /root，登录用户读不到。
#
# 用法（课程环境的终端里）：
#   cd /mnt/d/ROS2七天速成/Day4_Nav2建图/模板
#   bash 一键装ROS2课程环境.sh
# 约 20~40 分钟；跑完重开终端或 source ~/.bashrc
#
# 网络加固（2026-11-12）：WSL2 NAT 模式拿不到 Windows 的 localhost 代理，
#   所以系统源 + ROS2 源都换中科大镜像；ROS2 GPG key 下载加 20s 超时，
#   失败自动降级 trusted=yes，避免卡死在 raw.githubusercontent.com。
# ============================================================

set -e
export DEBIAN_FRONTEND=noninteractive

# ---- 0. 版本守卫：Humble 只支持 22.04 jammy ----
CODENAME=$(lsb_release -c -s 2>/dev/null || echo "unknown")
if [ "$CODENAME" != "jammy" ]; then
    echo "❌ 当前系统代号是 '$CODENAME'，不是 jammy (Ubuntu 22.04)。"
    echo "   ROS2 Humble 官方只提供 22.04 的二进制包，在这里装不上。"
    echo "   （实测过 26.04 resolute 会踩这个坑）请换到 22.04 的课程发行版。"
    exit 1
fi
echo "✅ 系统检查通过：$CODENAME"

# ---- 1. 权限：root 直接跑，普通用户用 sudo ----
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
    command -v sudo >/dev/null 2>&1 || { echo "❌ 需要 sudo，请先 apt install sudo"; exit 1; }
fi

echo "===== [预备] 系统 apt 源换国内镜像 ====="
if [ -f /etc/apt/sources.list ] && ! grep -q "mirrors.ustc.edu.cn/ubuntu" /etc/apt/sources.list; then
    $SUDO cp /etc/apt/sources.list /etc/apt/sources.list.bak.course
    $SUDO tee /etc/apt/sources.list > /dev/null <<'EOF'
deb https://mirrors.ustc.edu.cn/ubuntu jammy main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu jammy-updates main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu jammy-backports main restricted universe multiverse
deb https://mirrors.ustc.edu.cn/ubuntu jammy-security main restricted universe multiverse
EOF
    echo "系统源已换 USTC（原文件备份为 sources.list.bak.course）"
else
    echo "系统源已是 USTC 或无需处理，跳过"
fi

echo "===== [1/6] locale（ROS2 强制要求 UTF-8） ====="
$SUDO apt-get update -y
$SUDO apt-get install -y locales curl gnupg lsb-release ca-certificates
$SUDO locale-gen en_US en_US.UTF-8
$SUDO update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "===== [2/6] ROS2 apt 源（中科大镜像，国内快） ====="
if [ ! -f /etc/apt/sources.list.d/ros2.list ]; then
    KEY_OK=1
    $SUDO curl -fsSL --max-time 20 https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg || KEY_OK=0
    if [ "$KEY_OK" -eq 1 ]; then
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.ustc.edu.cn/ros2/ubuntu jammy main" \
            | $SUDO tee /etc/apt/sources.list.d/ros2.list > /dev/null
        echo "ROS2 源已写入（USTC 镜像，带 GPG 签名校验）"
    else
        echo "⚠️  ROS2 GPG key 下载失败（raw.githubusercontent.com 被墙/无代理）"
        echo "    课程沙盒降级为 trusted=yes，不影响使用；以后联网可改回签名校验。"
        echo "deb [arch=$(dpkg --print-architecture) trusted=yes] https://mirrors.ustc.edu.cn/ros2/ubuntu jammy main" \
            | $SUDO tee /etc/apt/sources.list.d/ros2.list > /dev/null
    fi
else
    echo "ros2.list 已存在，跳过"
fi

echo "===== [3/6] ROS2 Humble 桌面版 + 开发工具（约 1~2GB） ====="
$SUDO apt-get update -y
$SUDO apt-get install -y ros-humble-desktop ros-dev-tools

echo "===== [4/6] Day4 建图全家桶（含 Gazebo Classic 11） ====="
# 课程环境是干净的，没有 gz-tools2，所以 gazebo 11 能正常装上。
# ⚠️ 之后别在这个环境里装任何 gz-* 新版 Gazebo，否则又会冲突。
$SUDO apt-get install -y \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-gazebo \
    ros-humble-turtlebot3-teleop \
    ros-humble-slam-toolbox \
    ros-humble-nav2-bringup \
    ros-humble-navigation2

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

echo "===== [6/6] 验证 ====="
source /opt/ros/humble/setup.bash
echo "ROS2:      $(ros2 --version 2>/dev/null || echo '未找到')"
echo "Gazebo:    $(gazebo --version 2>/dev/null | head -1 || echo '未找到')"
echo "TB3 世界:  $(ros2 pkg prefix turtlebot3_gazebo 2>/dev/null || echo '未找到')"
echo "SLAM:      $(ros2 pkg prefix slam_toolbox 2>/dev/null || echo '未找到')"
echo "gz-tools2: $(dpkg -l gz-tools2 2>/dev/null | grep -c '^ii' || echo 0) 个（应为 0，确认隔离）"
echo ""
echo "🎉 装完了！重开终端，然后跑 Day4 四终端（RViz 与键盘遥控各占一个）："
echo "   终端1: bash 启动建图.sh"
echo "   终端2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true"
echo "   终端3: ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz"
echo "   终端4: ros2 run turtlebot3_teleop teleop_keyboard   ← 键盘在这个窗口按"
echo "          （rviz2 占住终端不返回，别把两条命令塞进同一个终端）"
echo ""
echo "图形提示：WSL2 用 Win11 自带 WSLg（echo \$DISPLAY 有值即可）；"
echo "          黑屏兜底 export LIBGL_ALWAYS_SOFTWARE=1"

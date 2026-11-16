#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# Day1 · ROS2 Humble 一键安装脚本（在 Ubuntu-22.04 里跑）
# ------------------------------------------------------------
# 前置（只需做一次，沙箱里 wsl.exe 被拦截，这步要你手动执行）：
#   在 Windows 终端(管理员) 跑：  wsl --install -d Ubuntu-22.04
#   装完首次启动会让你设用户名/密码，设好后再继续。
#
# 本脚本做的事（都在 Ubuntu 内部）：
#   1) 设置 locale 为 en_US.UTF-8（ROS2 强制要求）
#   2) 加入 ROS2 官方 apt 源 + 密钥
#   3) apt 安装 ros-humble-desktop + ros-dev-tools
#   4) 把 source /opt/ros/humble/setup.bash 写进 ~/.bashrc
#   5) 验证 ros2 --version
#
# 用法（Ubuntu 终端里）：
#   cd /mnt/d/具身智能求职培训/Day1_安装ROS2Humble/模板
#   bash day1_install_ros2.sh
#   装完重开终端，或执行： source ~/.bashrc
# ============================================================

set -e                      # 任一步失败就停下，避免半成品
export DEBIAN_FRONTEND=noninteractive

# ---- 0. 权限：WSL 默认是普通用户，用 sudo；若是 root 则直接跑 ----
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
    # 确认 sudo 可用
    command -v sudo >/dev/null 2>&1 || { echo "❌ 需要 sudo，请先: apt install sudo"; exit 1; }
fi

echo "===== [1/5] 设置 locale (en_US.UTF-8) ====="
$SUDO apt-get update -y
$SUDO apt-get install -y locales
$SUDO locale-gen en_US en_US.UTF-8
$SUDO update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
echo "locale 已设: $LANG"

echo "===== [2/5] 加入 ROS2 apt 源 + 密钥 ====="
$SUDO apt-get install -y curl gnupg lsb-release
# 下载 ROS 密钥到 keyrings
sudo_install_key() {
    if [ -x "$(command -v curl)" ]; then
        $SUDO curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
            -o /usr/share/keyrings/ros-archive-keyring.gpg
    fi
}
sudo_install_key
# 写源列表（jammy = Ubuntu 22.04）
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    | $SUDO tee /etc/apt/sources.list.d/ros2.list > /dev/null
echo "ROS2 源已写入 /etc/apt/sources.list.d/ros2.list"

echo "===== [3/5] apt 安装 ros-humble-desktop + ros-dev-tools ====="
$SUDO apt-get update -y
# ros-humble-desktop：含 ROS2 核心 + RViz + 常用库（约 1~2 GB，耐心等）
$SUDO apt-get install -y ros-humble-desktop ros-dev-tools
echo "ROS2 桌面版安装完成"

echo "===== [4/5] 写入 ~/.bashrc 自动 source ====="
# 避免重复写入
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc 2>/dev/null; then
    echo '' >> ~/.bashrc
    echo '# >>> ROS2 Humble >>>' >> ~/.bashrc
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
    echo 'export ROS_DISTRO=humble' >> ~/.bashrc
    echo '# <<< ROS2 Humble <<<' >> ~/.bashrc
    echo "~/.bashrc 已追加 ROS2 自动 source"
else
    echo "~/.bashrc 已有 ROS2 source，跳过"
fi

echo "===== [5/5] 验证安装 ====="
# 当前 shell 先 source 一次
source /opt/ros/humble/setup.bash
if command -v ros2 >/dev/null 2>&1; then
    echo "✅ ros2 可用，发行版: $ROS_DISTRO"
    dpkg -l ros-humble-desktop 2>/dev/null | awk '/^ii/{print "   版本:", $3}'
    echo ""
    echo "🎉 Day1 完成！重开终端或执行 source ~/.bashrc 即可直接用 ros2。"
    echo "   试一下： ros2 run demo_nodes_py talker   （另开终端 ros2 run demo_nodes_py listener）"
else
    echo "❌ ros2 仍不可用，请检查上面步骤的报错"
    exit 1
fi

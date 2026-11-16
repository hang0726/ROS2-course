#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# Day5 模板 · 加载已存地图 + AMCL 定位 + 导航栈（TB3 仿真）
# 用法（Day4 已存好 ~/tb3_map.pgm + ~/tb3_map.yaml）：
#     bash /mnt/d/ROS2七天速成/Day5_Nav2导航/模板/保存并导航.sh
#     bash .../保存并导航.sh /path/to/other_map.yaml   # 也可指定别的地图
#
# ⚠️ 运行前必须先关掉 Day4 的全部窗口（Gazebo / SLAM / RViz / teleop）：
#    Day4 的 slam_toolbox 和 Day5 的 AMCL 都要发布 map->odom，同时跑会抢 TF。
#
# 起完后在 RViz 里：先 2D Pose Estimate 给初始位姿，再 GoalTool 点目标。
# ============================================================

# 故意不开 set -e / set -u：ROS2 的 setup.bash 会引用未定义变量
# AMENT_TRACE_SETUP_FILES，且 launch 前台运行时 Ctrl+C 的退出码不该把脚本带崩。
export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-waffle}"
export DISPLAY="${DISPLAY:-:0}"
export GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-}:/opt/ros/humble/share/turtlebot3_gazebo/models"

# WSLg 防黑屏：Day4 实测有效的软件渲染组合，Day5 同样要带
if [ "${HARDWARE_GL:-0}" != "1" ]; then
    export LIBGL_ALWAYS_SOFTWARE=1
    export GALLIUM_DRIVER=llvmpipe
    export QT_OPENGL=software
    export QT_QUICKBACKEND=software
    echo "（默认软件渲染 llvmpipe，防 Gazebo / RViz 黑屏）"
fi

source /opt/ros/humble/setup.bash

MAP=${1:-$HOME/tb3_map.yaml}   # ★ 默认指向 Day4 实际生成的地图，可用第 1 个参数覆盖

if [ ! -f "$MAP" ]; then
    echo "❌ 找不到地图: $MAP"
    echo "   Day4 应已生成 ~/tb3_map.pgm + ~/tb3_map.yaml"
    echo "   或用参数指定：bash 保存并导航.sh /path/to/map.yaml"
    exit 1
fi

# 只读检测，不杀进程：Day4 的 SLAM 还在跑就直接拦住，避免抢 map->odom
if pgrep -f "online_async_launch.py" >/dev/null 2>&1; then
    echo "❌ 检测到 Day4 的 slam_toolbox 还在运行。"
    echo "   请先关掉 Day4 全部窗口（Ctrl+C 后关掉 Gazebo / RViz），再重跑本脚本。"
    echo "   原因：slam_toolbox 和 AMCL 都发布 map->odom，同时跑定位必乱。"
    exit 1
fi

# ★ 必须复用 Day4 建图时的同一个世界，否则激光扫描与地图对不上、AMCL 收敛不了、车不动。
# Nav2 bringup 默认是 nav2_bringup/worlds/world_only.model，跟 turtlebot3_world.world 不是一回事。
WORLD=/opt/ros/humble/share/turtlebot3_gazebo/worlds/turtlebot3_world.world
if [ ! -f "$WORLD" ]; then
    echo "❌ 找不到 Day4 建图用的世界：$WORLD"
    exit 1
fi

echo "===== 加载地图: $MAP ====="
echo "===== 仿真世界: $WORLD（与 Day4 建图时一致）====="
echo "===== bringup 会同时拉起 Gazebo + map_server + AMCL + Nav2 + RViz ====="
echo "===== RViz 里：先 2D Pose Estimate，再最右侧 GoalTool ====="
ros2 launch nav2_bringup tb3_simulation_launch.py \
    headless:=False \
    map:="$MAP" \
    world:="$WORLD"

#!/usr/bin/env bash
# ============================================================
# Day4 · 一键启动 TB3 仿真世界（建图第 1 步）
# 用法：bash 模板/启动建图.sh
# 说明：本脚本只起 Gazebo 世界（不带 AMCL！Day4 建图 map->odom 归 slam_toolbox 管）。
#       SLAM / RViz / 键盘遥控 需另开终端，命令见脚本打印。
# 退出：Ctrl+C
# ============================================================

# 故意不开 set -e：ros2 launch 被 Ctrl+C 停时返回非 0，会误报成"失败"

# ★ 机器人型号：waffle / burger / waffle_pi（决定 TURTLEBOT3_MODEL）
export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-waffle}"

# Win11 自带 WSLg，DISPLAY 一般已有值；为空才回退 :0（老 X 服务器场景）
export DISPLAY="${DISPLAY:-:0}"

# TB3 模型路径（用 :- 兜底，避免 set -u 类脚本里变量未定义报错）
export GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-}:/opt/ros/humble/share/turtlebot3_gazebo/models"

# 载入 ROS2 环境
source /opt/ros/humble/setup.bash

echo "================================================================"
echo "  TURTLEBOT3_MODEL = ${TURTLEBOT3_MODEL}"
echo "  DISPLAY          = ${DISPLAY:-<空，可能没图形!>}"
echo "  若 Gazebo 黑屏：Ctrl+C 后先 export LIBGL_ALWAYS_SOFTWARE=1 再重跑"
echo "----------------------------------------------------------------"
echo "  【终端 2】起 SLAM 建图（use_sim_time 必加）："
echo "    ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true"
echo ""
echo "  【终端 3】只看地图（RViz，不接受按键）："
echo "    ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz"
echo ""
echo "  【终端 4】键盘遥控（按键在这个窗口按）："
echo "    ros2 run turtlebot3_teleop teleop_keyboard"
echo "    w/x 增减前进速度, a/d 增减转向, s 或空格急停; 慢走一圈"
echo ""
echo "  ⚠️ RViz 与遥控必须各占一个终端（rviz2 会占住终端不返回）"
echo "  建完存图：bash 模板/保存地图.sh"
echo "================================================================"

# 前台启动 Gazebo 世界（只仿真，不含定位）
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

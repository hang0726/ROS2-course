#!/usr/bin/env bash
# ============================================================
# Day4 · 一键启动（四终端合一，只在课程专用 ROS2Course 里跑）
# ------------------------------------------------------------
# 一条命令自动起：Gazebo 世界 / SLAM 建图 / RViz（三者后台 + 日志）
# 键盘遥控留在【当前终端前台】→ 直接按 w/a/s/d 开车，不用切窗口
# Ctrl+C 退出遥控后问一句是否存图；脚本结束自动清理后台进程
#
# 用法（ROS2Course 里，必须用绝对路径）：
#   bash /mnt/d/具身智能求职培训/Day4_Nav2建图/模板/Day4_一键启动.sh
#
# 3D 窗口（Gazebo / RViz）默认走软件渲染防黑屏；想试硬件渲染：
#   HARDWARE_GL=1 bash /mnt/d/具身智能求职培训/Day4_Nav2建图/模板/Day4_一键启动.sh
# ============================================================

# 故意不开 set -u：ROS2 的 setup.bash 会引用未定义变量 AMENT_TRACE_SETUP_FILES，
# 开了 nounset 会在 source 时直接报错退出（2026-11-13 实测踩过）。
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-waffle}"
export DISPLAY="${DISPLAY:-:0}"
export GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-}:/opt/ros/humble/share/turtlebot3_gazebo/models"
# WSLg + WSL2(NAT) 下，独显 OpenGL 经常让 Gazebo / RViz 整窗全黑。
# 默认强制软件渲染（慢一点但一定出画面）；想试硬件渲染加 HARDWARE_GL=1。
if [ "${HARDWARE_GL:-0}" = "1" ]; then
    echo "（已按 HARDWARE_GL=1 走硬件渲染；若 3D 窗口全黑，去掉该变量重跑）"
else
    export LIBGL_ALWAYS_SOFTWARE=1
    export GALLIUM_DRIVER=llvmpipe
    export QT_OPENGL=software
    export QT_QUICKBACKEND=software
    echo "（默认软件渲染 llvmpipe + Qt software，防 Gazebo / RViz 黑屏）"
fi

LOG=/tmp/day4_logs
mkdir -p "$LOG"

cleanup() {
    pkill -f "turtlebot3_world.launch.py" 2>/dev/null || true
    pkill -f "online_async_launch.py" 2>/dev/null || true
    pkill -f "nav2_default_view.rviz" 2>/dev/null || true
    pkill -f "teleop_keyboard" 2>/dev/null || true
}
trap 'echo ""; echo "===== 收尾：关闭 Gazebo / SLAM / RViz 后台进程 ====="; cleanup' EXIT

echo "===== [0/5] 清理上一轮 Day4 残留 ====="
cleanup
sleep 2

echo "===== [1/5] 起 Gazebo 世界（后台） ====="
nohup ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py > "$LOG/1_gazebo.log" 2>&1 &

echo "===== [2/5] 等 Gazebo 发布 /scan（最多约 2 分钟） ====="
OK=0
for i in $(seq 1 60); do
    if ros2 topic list 2>/dev/null | grep -q '^/scan$'; then OK=1; break; fi
    sleep 2
done
if [ "$OK" -ne 1 ]; then
    echo "❌ 等不到 /scan，Gazebo 可能没起来。日志末尾："
    tail -30 "$LOG/1_gazebo.log"
    exit 1
fi
echo "✅ /scan 已就绪"

echo "===== [3/5] 起 SLAM 建图（后台，use_sim_time:=true） ====="
nohup ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true > "$LOG/2_slam.log" 2>&1 &
sleep 3

echo "===== [4/5] 起 RViz（后台） ====="
nohup ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz > "$LOG/3_rviz.log" 2>&1 &
sleep 2

echo ""
echo "================================================================"
echo "  ✅ 三个后台都起来了，应该弹出 2 个图形窗口：Gazebo + RViz"
echo "  👀 RViz 中间一片黑？先拖一下窗口触发重绘；仍黑就把左侧"
echo "     Fixed Frame 从 map 改成 odom：能看见 Grid 网格 = 渲染没问题，只是还没建图"
echo "  ⚠️ Day4 只建图，别点 RViz 最右侧 GoalTool：这里没起 Nav2，"
echo "     会报 navigate_to_pose action server is not available，反复点会把 RViz 点崩"
echo "     要导航请关掉本窗口，回桌面入口按 [4] 进 Day5"
echo "  实时日志（另开终端）：tail -f $LOG/*.log"
echo "----------------------------------------------------------------"
echo "  ⚠️  下面这几行是【按键说明】，不是命令！千万别复制粘贴到终端！"
echo "      看到这段提示后，直接用键盘敲单个字母：w / a / s / d / x"
echo "----------------------------------------------------------------"
echo "  ⌨️  键盘就在【当前这个终端】按，不用切窗口："
echo "        w / x : 增 / 减 前进速度"
echo "   a    s    d : 增 / 减 转向速度   （s 或空格急停）"
echo "  慢走、贴边绕一圈，盯 RViz 里 /map 一点点长出来"
echo "  走完按 CTRL-C 退出遥控 → 会问你要不要存图"
echo "================================================================"
echo ""

# 只拦一次 CTRL-C：信号停掉前台 teleop，但别把本脚本一起带走，
# 否则 bash 收到 SIGINT 默认直接退出，下面的存图问答根本执行不到。
trap 'echo ""; echo "（已停止遥控，接着存图）"' INT
ros2 run turtlebot3_teleop teleop_keyboard
trap - INT

echo ""
read -r -p "遥控已退出。现在把地图存到 ~/tb3_map ？[Y/n] " ans
if [ "${ans:-Y}" = "Y" ] || [ "${ans:-Y}" = "y" ]; then
    ros2 run nav2_map_server map_saver_cli -f "$HOME/tb3_map"
    if [ -s "$HOME/tb3_map.pgm" ] && [ -s "$HOME/tb3_map.yaml" ]; then
        ls -lh "$HOME/tb3_map.pgm" "$HOME/tb3_map.yaml"
        echo "🎉 Day4 通关：~/tb3_map.pgm + ~/tb3_map.yaml（Day5 导航要用）"
        exit 0
    else
        echo "❌ 地图文件没生成，别进 Day5。SLAM 日志：tail -30 $LOG/2_slam.log"
        exit 1
    fi
else
    echo "跳过存图。以后可跑：bash /mnt/d/具身智能求职培训/Day4_Nav2建图/模板/保存地图.sh"
    exit 1
fi

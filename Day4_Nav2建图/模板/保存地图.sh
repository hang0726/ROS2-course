#!/usr/bin/env bash
# ============================================================
# Day4 · 收尾：把当前 SLAM 建好的地图保存成 pgm + yaml（Day5 导航要用）
# 用法：bash 模板/保存地图.sh [输出前缀(不带扩展名)]
#   默认前缀：$HOME/tb3_map  →  生成 tb3_map.pgm + tb3_map.yaml
# 前提：Day4 的 slam_toolbox 正在跑、/map 话题有数据
# ============================================================

OUT="${1:-$HOME/tb3_map}"

source /opt/ros/humble/setup.bash

echo "保存地图到："
echo "  ${OUT}.pgm   (栅格图)"
echo "  ${OUT}.yaml  (分辨率/原点/阈值等元数据)"
echo "------------------------------------------------"

# map_saver_cli 会在 -f 指定的前缀旁生成 .pgm + .yaml
ros2 run nav2_map_server map_saver_cli -f "${OUT}"

echo "------------------------------------------------"
echo "检查是否生成："
ls -lh "${OUT}.pgm" "${OUT}.yaml" 2>/dev/null && echo "✅ 保存成功" || echo "⚠️ 没找到文件，检查 /map 是否有数据"

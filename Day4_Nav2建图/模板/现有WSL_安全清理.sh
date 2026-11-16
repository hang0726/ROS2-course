#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# 现有 WSL 环境「安全清理」（只清缓存/日志，绝不动任何已装包）
# ------------------------------------------------------------
# 🔴 红线：不要 apt remove gz-tools2 / gz-sim7 / gz-garden。
#    那是 AMCL 论文 / PX4 / 人形课室 / Aliengo 仿真的底座，
#    卸了「后面就不能用」了。
#
# 上次 Day4 装包失败发生在「依赖解析」阶段，一个包都没装进去，
# 现有环境本来就是好的 —— 这个脚本只是顺手腾点磁盘空间。
#
# 用法（在你现有 WSL 终端里）：
#   bash ~/具身智能求职培训/Day4_Nav2建图/模板/现有WSL_安全清理.sh
#
# ⚠️ 释放 RAM 不在这个脚本里：那要在 Windows PowerShell 跑
#    wsl --shutdown    （会关掉 WSL，执行前确认没在跑仿真/训练）
#    详见 VM方案_装机清单.md 第四节「分时复用」。
# ============================================================

echo "===== 清理前磁盘占用 ====="
df -h / | tail -1

echo "===== [1/3] 清 apt 下载缓存（.deb 安装包，纯缓存） ====="
sudo apt-get clean        # 清空 /var/cache/apt/archives
sudo apt-get autoclean    # 只删已过期的旧版本包

echo "===== [2/3] 清 systemd 日志（保留最近 7 天） ====="
sudo journalctl --vacuum-time=7d 2>/dev/null || echo "（WSL 无 systemd 日志，跳过）"

echo "===== [3/3] 清 pip 缓存（用 pip 官方命令，不 rm -rf 家目录） ====="
python3 -m pip cache purge 2>/dev/null || echo "（pip 缓存为空或无 pip，跳过）"

echo "===== 校验：Gazebo Garden 环境完好（下面应看到 gz-sim7 / gz-tools2） ====="
dpkg -l | grep -E "gz-(garden|sim7|tools2)" || echo "⚠️ 没查到，请确认"

echo ""
echo "===== 清理后磁盘占用 ====="
df -h / | tail -1
echo ""
echo "✅ 完成。已装包一个没动，Gazebo Garden 可继续用于论文仿真。"
echo "   要释放内存请到 Windows PowerShell 执行： wsl --shutdown"

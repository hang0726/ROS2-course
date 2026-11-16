#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# ============================================================
# Day7 模板 · 一键把课程代码初始化并提交到 GitHub
#
# 前置（只需做一次，在你自己的普通 WSL 终端里）：
#   1) 在 GitHub 网页建好【空仓库】（不要勾 Add a README / .gitignore / license）
#   2) 生成 SSH key，并把公钥贴到 GitHub：
#        ssh-keygen -t ed25519 -C "hang0726@users.noreply.github.com"
#        cat ~/.ssh/id_ed25519.pub
#        GitHub -> Settings -> SSH and GPG keys -> New SSH key
#   3) 配 git 身份（--global 或 --local 任一处配过即可）：
#        git config --global user.name  "hang0726"
#        git config --global user.email "hang0726@users.noreply.github.com"
#
# 用法（在 WSL 终端执行）：
#   bash /mnt/d/ROS2七天速成/Day7_GitHub入门/模板/一键初始化仓库.sh git@github.com:hang0726/ROS2-course.git
#
# 脚本会：检查身份 -> 进入课程根目录 -> git init(若需要) -> 拷 .gitignore
#         -> add -> commit(若有改动) -> 连远程 -> push -u
# ============================================================

set -e

REMOTE=${1:-}                                 # 第一个参数 = 仓库 SSH 地址
if [ -z "$REMOTE" ]; then
    echo "[ERROR] 缺仓库地址。用法："
    echo '  bash 一键初始化仓库.sh git@github.com:hang0726/ROS2-course.git'
    exit 1
fi

# ★★★ 课程根目录（WSL 里访问 Windows 的 D 盘）
COURSE_DIR="/mnt/d/ROS2七天速成"
if [ ! -d "$COURSE_DIR" ]; then
    echo "[ERROR] 找不到课程目录: $COURSE_DIR"
    exit 1
fi
cd "$COURSE_DIR"

# 若还没 init 就初始化（已 init 的仓库直接复用，不会重置历史）
if [ ! -d .git ]; then
    git init -b main
fi

# ★ 坑 A：commit 需要 user.name / user.email，没配会报
#   "Please tell me who you are"，而且容易被 || true 吞掉变成「假成功」。
#   这里读的是不带 --global 的"最终生效值"，
#   所以全局或仓库级(--local)任意一处配过都算数。
if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
    echo "[ERROR] git 身份没配，先执行这两行（换成你自己的）："
    echo '  git config --global user.name  "hang0726"'
    echo '  git config --global user.email "hang0726@users.noreply.github.com"'
    exit 1
fi

# 放一份 .gitignore（忽略 ROS2 编译产物和缓存）
GITIGNORE_TPL="Day7_GitHub入门/模板/.gitignore"
if [ ! -f "$GITIGNORE_TPL" ]; then
    echo "[ERROR] 找不到 .gitignore 模板: $GITIGNORE_TPL"
    exit 1
fi
cp "$GITIGNORE_TPL" .gitignore

# 暂存全部；有改动才提交（不用 || 吞错误，避免"提交了个空历史"却报成功）
git add -A
if git diff --cached --quiet; then
    echo "（没有新改动，跳过提交）"
else
    git commit -m "初始化：我的 ROS2 课程（Day1-7 全套代码与笔记）"
fi

# 连接远程并推送
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git branch -M main

# ★ 坑 B：若建仓时勾了 Add a README file，远程仓库会有一个初始提交，
#   本地历史与它无关，首次 push 必被拒（non-fast-forward）。
#   这里自动合并一次远程历史再重试，避免用户手动查资料。
if ! git push -u origin main; then
    echo "（首次 push 被拒，多半是远程仓库不为空；合并后重试）"
    git fetch origin
    git merge --allow-unrelated-histories --no-edit -m "合并远程初始提交" origin/main
    git push -u origin main
fi

echo "已推送到 $REMOTE ，去 GitHub 网页看看吧！"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day8 · 实例代码：昇腾开发环境自检（把官网安装步骤变成一键体检）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  昇腾环境装起来坑多：驱动、CANN、环境变量、MindSpore、ROS2 缺一样，
  Day12 的 ATC 转换和 AscendCL 推理就全卡住。本脚本用纯 Python 逐项检查：
  哪些装好了、哪些缺、缺了该怎么补——把"环境到底通没通"变成一句话能答。

【心智模型：昇腾环境的四层依赖（缺一层后面全废）】
  ① 驱动层     npu-smi 能看到 310B 芯片        ← 最底层，没了后面免谈
  ② 工具链层   CANN（含 atc / AscendCL 头文件） ← 模型转换和推理靠它
  ③ 框架层     MindSpore / PyTorch             ← 训练侧用
  ④ 机器人层   ROS2（rclpy）                    ← 和车通信、发控制

【为什么用 subprocess 查命令而不是直接 import】
  ★ 环境自检要"即使某样没装也能继续查下一项"。直接 import mindspore
    会在缺包时 ImportError 中断整个脚本；用 subprocess 跑 `cmd --version`
    并捕获异常，才能一次性把四层全查完、列出完整清单。

【诚实边界】
  本脚本只查"命令在不在、包能不能 import"，属于静态自检。
  真正能不能跑推理，要 Day12 用 .om 模型在车上实测。【待材料】部分以学校指导书为准。

【用法】python3 ascend_env_check.py
【输出】逐项 [通]/[缺] + 缺失项的修复提示，末尾给总结论。
════════════════════════════════════════════════════════════════════
"""

import shutil                                       # 查命令在不在 PATH 里（which 的 Python 版）
import subprocess                                   # 跑 `cmd --version` 探测版本
import sys                                          # 判断平台、退出码

# ── 可配置项集中在这里 ─────────────────────────────────────────
SOC_VERSION = 'Ascend310B'                          # 你的芯片型号，ATC 转换要用
CHECKS = [                                          # 每项：(名字, 探测方式, 缺失提示)
    ('驱动 npu-smi', 'cmd:npu-smi', '装昇腾驱动；source ~/Ascend/ascend-toolkit/set_env.sh'),
    ('ATC 工具', 'cmd:atc', '装 Ascend-cann-toolkit；source set_env.sh'),
    ('MindSpore', 'py:mindspore', '装昇腾版 MindSpore wheel（不是普通 x86 版）'),
    ('ROS2 rclpy', 'py:rclpy', 'source /opt/ros/humble/setup.bash'),
    ('atc 配置文件', 'env:ASCEND_HOME_PATH', '环境变量没设；source set_env.sh'),
]


def check_cmd(name: str) -> tuple:
    """探测一个命令行工具在不在 PATH 里。返回 (是否找到, 版本信息)。"""
    path = shutil.which(name)
    if path is None:
        return False, '命令不在 PATH'
    # 找到了就跑一下 --version，拿到版本（失败也不算错，命令在就行）
    try:
        out = subprocess.run([name, '--version'], capture_output=True,
                             text=True, timeout=5)
        ver = (out.stdout or out.stderr).strip().splitlines()
        return True, ver[0][:60] if ver else '（无版本输出）'
    except Exception:
        return True, '（命令在，版本查询失败）'


def check_py(module: str) -> tuple:
    """探测一个 Python 包能不能 import。用子进程隔离，缺包不影响主流程。"""
    try:
        out = subprocess.run(
            [sys.executable, '-c', f'import {module}; print(getattr({module}, "__version__", "ok"))'],
            capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return True, out.stdout.strip()[:60]
        return False, 'import 失败（包未装或版本不匹配）'
    except Exception as exc:
        return False, f'探测异常 {type(exc).__name__}'


def check_env(name: str) -> tuple:
    """探测一个环境变量有没有设置。"""
    import os
    val = os.environ.get(name)
    return (True, val[:60]) if val else (False, '环境变量未设置')


def probe(spec: str) -> tuple:
    """按 spec 前缀分派到三种探测方式：cmd: / py: / env:。"""
    kind, _, target = spec.partition(':')
    if kind == 'cmd':
        return check_cmd(target)
    if kind == 'py':
        return check_py(target)
    if kind == 'env':
        return check_env(target)
    return False, f'未知探测类型 {kind}'


def main() -> None:
    print('===== 昇腾开发环境自检 =====')
    print(f'目标芯片: {SOC_VERSION}')
    ok_count = 0
    for name, spec, fix in CHECKS:
        ok, info = probe(spec)
        tag = '通' if ok else '缺'
        print(f'[{tag}] {name:<16} {info}')
        if not ok:
            print(f'        → 修复：{fix}')
        else:
            ok_count += 1
    print('\n============================')
    if ok_count == len(CHECKS):
        print('结论：环境齐全，可以进 Day12 做 ATC 转换 / AscendCL 推理')
    else:
        print(f'结论：{len(CHECKS) - ok_count} 项缺失，按上面的提示补完再往下走')
    print('提示：这是静态自检，真正能否推理要 Day12 用 .om 模型实测')


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 昇腾环境四层依赖是哪四层？ → 驱动(npu-smi) / 工具链(CANN/atc) / 框架(MindSpore) / 机器人(ROS2)
# Q2 为什么用 subprocess 而不用直接 import？ → 缺包时 import 会中断，subprocess 能一次查完所有项
# Q3 soc_version 为什么写 Ascend310B？ → 写错芯片型号，转出的 .om 车上加载失败
# ─────────────────────────────────────────────────────────────────────

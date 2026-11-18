#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day10 · 实例代码 2：地图质量分析 + 空地目标点查找（纯 Python，不依赖 ROS）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  你 Day4 建图只建了一小片，Day6 导航报 "goal off the global costmap"——
  根因是地图大部分 unknown、目标点越界。本脚本把"地图好不好"量化：
    ① 统计三色像素比例（空地/障碍/未知），一句话判定地图合不合格
    ② 自动找出地图内、周围空旷的安全目标点，直接拿去 Day11 导航
  这是岗位 JD 里"导航失败问题复现与初步分析"的程序化证据，
  也是你 benchmark 表里"定位误差/建图完整度"数字的数据来源。

【心智模型：pgm 地图 + yaml 元数据】
  gmapping/cartographer 存图产出两个文件：
    xxx.pgm  —— 栅格图，每个像素一个格子。三色取值：
                 254/255 = 白 = 空地(free)
                   0     = 黑 = 障碍(occupied)
                 205     = 灰 = 未知(unknown，车没走到过)
    xxx.yaml —— 元数据，关键是 resolution(米/格) 和 origin[原点 x,y,yaw]
  ★ 世界坐标 ↔ 像素坐标 换算（面试常考）：
     像素 i = round((世界x - origin_x) / resolution)
     像素 j = round((世界y - origin_y) / resolution)
     反过来：世界x = origin_x + i * resolution
  目标点越界 = 算出的像素 i/j 超出 [0,宽) / [0,高)，planner 直接拒。

【为什么要有"周围空旷"检查】
  目标点本身是空地不够——它紧挨着墙也会让 planner 规划失败。
  所以查目标点周围 r 格范围（默认 2 格 = 5x5）必须全是空地，
  这就是 clear() 函数干的事。

【前置】已完成 Day10 建图，拿到 .pgm + .yaml。
【用法】python3 map_quality_check.py                       # 自动找同目录的 pgm/yaml
        python3 map_quality_check.py my_room.pgm my_room.yaml
        python3 map_quality_check.py my_room.pgm my_room.yaml 3   # 空旷半径改 3 格
【输出】地图尺寸/世界范围/三色比例/合格判定 + 6 个安全目标点世界坐标。
════════════════════════════════════════════════════════════════════
"""

import os                                           # 处理路径、自动找同目录文件
import re                                           # 解析 pgm 头 + yaml 关键字段
import sys                                          # 命令行参数、退出码

# ── 可配置项集中在这里 ─────────────────────────────────────────
UNKNOWN_VALUE = 205                                 # pgm 里 unknown 的灰度值
FREE_MIN = 220                                      # ≥ 此值视为空地（兼容 254/255）
CLEAR_RADIUS = 2                                    # 目标点周围空旷检查半径（格）
UNKNOWN_WARN_RATIO = 0.30                           # unknown 占比超 30% 判"地图不完整"
MAX_CANDIDATES = 6                                  # 最多列几个候选目标点


def parse_yaml(path: str) -> tuple:
    """
    从 yaml 里读 resolution 和 origin，不依赖 pyyaml（车上未必装）。
    返回 (resolution, origin_x, origin_y)。
    ★ 用正则抓数字，避免引入第三方依赖——机器人环境保持最小依赖是好习惯。
    """
    text = open(path, encoding='utf-8').read()
    res_m = re.search(r'resolution:\s*([0-9.]+)', text)
    org_m = re.search(r'origin:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)', text)
    if not res_m or not org_m:
        raise ValueError(f'yaml 解析失败，找不到 resolution/origin：{path}')
    return float(res_m.group(1)), float(org_m.group(1)), float(org_m.group(2))


def parse_pgm(path: str) -> tuple:
    """
    读 P5 二进制 pgm，返回 (宽, 高, 像素字节串)。
    P5 格式：头是 'P5 宽 高 最大值 '，后面紧跟 w*h 个字节的灰度。
    ★ 注意头后面只有一个空白字符就进入数据，用 m.end() 精确定位，别用 split。
    """
    data = open(path, 'rb').read()
    m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', data)
    if not m:
        raise ValueError(f'pgm 头解析失败（只支持 P5 二进制）：{path}')
    w, h, _maxv = map(int, m.groups())
    pixels = data[m.end():m.end() + w * h]
    if len(pixels) < w * h:
        raise ValueError(f'pgm 像素数据不足：{path}')
    return w, h, pixels


def main() -> None:
    # ── 解析命令行：支持显式传 pgm/yaml，也支持自动找同目录 ──
    if len(sys.argv) > 1:
        pgm_path = sys.argv[1]
    else:
        cands = [f for f in os.listdir('.') if f.endswith('.pgm')]
        if not cands:
            print('当前目录没有 .pgm，用法：python3 map_quality_check.py <地图.pgm> [地图.yaml]')
            sys.exit(1)
        pgm_path = cands[0]
    yaml_path = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(pgm_path)[0] + '.yaml'
    clear_r = int(sys.argv[3]) if len(sys.argv) > 3 else CLEAR_RADIUS

    res, ox, oy = parse_yaml(yaml_path)
    w, h, px = parse_pgm(pgm_path)

    # ① 基本参数 + 世界范围（越界判定就是拿这个范围卡）
    print(f'地图: {w} x {h} 格 | resolution={res} m/格')
    print(f'世界范围: x ∈ [{ox:.2f}, {ox + w * res:.2f}]  y ∈ [{oy:.2f}, {oy + h * res:.2f}]')

    def value(i: int, j: int) -> int:
        """取像素灰度；越界返回 -1（专门用来识别"目标点出界"）。"""
        if not (0 <= i < w and 0 <= j < h):
            return -1
        return px[j * w + i]

    # ② 三色统计：遍历全部像素，数空地/障碍/未知
    free = occ = unk = 0
    for j in range(h):
        row = px[j * w:(j + 1) * w]             # 取一行，避免逐个索引慢
        free += sum(1 for v in row if v >= FREE_MIN)
        occ += sum(1 for v in row if v == 0)
        unk += sum(1 for v in row if v == UNKNOWN_VALUE)
    total = w * h
    unk_ratio = unk / total
    print(f'\n像素统计: 空地 {free/total:.1%} | 障碍 {occ/total:.1%} | 未知 {unk_ratio:.1%}')

    # ③ 合格判定：unknown 太多 = 没走遍全屋（Day4 的坑）
    if unk_ratio > UNKNOWN_WARN_RATIO:
        print(f'判定: 不合格 — unknown 占 {unk_ratio:.1%} > {UNKNOWN_WARN_RATIO:.0%}，')
        print('      地图不完整，回 Day10 遥控走遍全屋重建（否则导航目标会越界）')
    else:
        print('判定: 合格 — 未知区域少，可用于 Day11 导航')

    def clear(i: int, j: int, r: int) -> bool:
        """目标点周围 r 格全空才安全（planner 才规划得出来）。"""
        return all(value(i + di, j + dj) >= FREE_MIN
                   for dj in range(-r, r + 1) for di in range(-r, r + 1))

    # ④ 找安全目标点：全图扫一遍，收集"本身空 + 周围空"的格子，
    #    按离地图几何中心近的优先排序（中心点通常最实用）。
    ci, cj = w // 2, h // 2
    good = []
    for j in range(clear_r, h - clear_r):
        for i in range(clear_r, w - clear_r):
            if value(i, j) >= FREE_MIN and clear(i, j, clear_r):
                wx, wy = ox + i * res, oy + j * res    # 像素 → 世界坐标
                good.append(((i - ci) ** 2 + (j - cj) ** 2, wx, wy))
    good.sort()
    print(f'\n安全空地 {len(good)} 格；最靠近中心的 {min(MAX_CANDIDATES, len(good))} 个目标点（世界坐标 x y yaw）:')
    for _, wx, wy in good[:MAX_CANDIDATES]:
        print(f'  {wx:.2f}  {wy:.2f}  0.00')
    if not good:
        print('  没找到——地图可能太小或全是 unknown，先重建地图')


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 世界坐标怎么换像素？      → i=(x-ox)/res, j=(y-oy)/res；反算 x=ox+i*res
# Q2 为什么目标点要查周围空旷？→ 紧挨墙 planner 也规划失败，不是空地就行
# Q3 unknown 占比高说明什么？  → 没走遍全屋，地图不完整，导航目标会越界
# ─────────────────────────────────────────────────────────────────────

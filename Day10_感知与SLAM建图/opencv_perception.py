#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day10 · 实例代码：OpenCV 三层感知入门（边缘 / 特征 / 颜色）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  官方实验 9-15 是一串 OpenCV 实验（缩放/仿射/边缘/特征/人脸/光流/前景背景）。
  本文件挑三个最实用、最能在面试讲清楚的——边缘检测、角点特征、颜色分割，
  给一套"读图 → 处理 → 输出"的通用框架。你可以在 PC 上先拿图片跑通，
  再换成车的摄像头 / 3D 相机数据流（【待材料】厂商相机 SDK 的取流方式）。

【心智模型：图像处理三步走】
  读图(BGR) → 预处理(灰度/模糊) → 算法(边缘/角点/颜色) → 输出结果
  ★ OpenCV 图像是 BGR 顺序，不是 RGB——颜色通道搞反，红蓝就互换了。

【三个算法分别在干什么】
  ① Canny 边缘检测：找亮度突变的地方 → 墙角、物体轮廓（建图/避障用）
  ② Harris/Shi-Tomasi 角点：找"角"这种稳定特征点 → 视觉定位、光流跟踪的基础
  ③ HSV 颜色分割：在 HSV 空间按颜色阈值抠图 → 比 RGB 抗光照变化（识别标牌用）

【为什么先做传统视觉，再做 AI 检测】
  ★ 传统视觉不依赖模型、CPU 就能跑、结果可解释——是理解"图像怎么变成坐标"的地基。
    Day11 手眼标定的"像素坐标→世界坐标"就建立在这些基础上。AI 检测(Day12)是上层。

【前置】pip install opencv-python numpy（PC 或车上都行）
【用法】python3 opencv_perception.py                    # 用自带测试图
        python3 opencv_perception.py your_image.jpg     # 用你的图
        python3 opencv_perception.py cam                # 用笔记本摄像头（车上换厂商SDK取流）
【输出】窗口显示原图 + 三种处理结果；无 GUI 环境则存成文件。
════════════════════════════════════════════════════════════════════
"""

import sys                                          # 读命令行参数（图片路径 / cam）
import cv2                                          # OpenCV：读图、图像处理、显示
import numpy as np                                  # 数组运算，颜色阈值/矩阵操作要用

# ── 可配置项集中在这里 ─────────────────────────────────────────
CANNY_LOW, CANNY_HIGH = 100, 200                    # Canny 双阈值：低/高，调大=边缘更少更粗
CORNER_COUNT = 30                                   # 最多画多少个角点
CORNER_QUALITY = 0.01                               # 角点质量阈值：调小=角点更多
BLUR_KERNEL = (5, 5)                                # 高斯模糊核：降噪，越大越糊
# HSV 红色阈值（OpenCV H 范围 0-179；红色跨 0 边界，所以要两段）
RED_LOWER1, RED_UPPER1 = np.array([0, 100, 100]), np.array([10, 255, 255])
RED_LOWER2, RED_UPPER2 = np.array([160, 100, 100]), np.array([179, 255, 255])


def canny_edges(img: np.ndarray) -> np.ndarray:
    """Canny 边缘检测：灰度→模糊→找边缘。返回单通道边缘图。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # 彩色转灰度，边缘检测不需要颜色
    blur = cv2.GaussianBlur(gray, BLUR_KERNEL, 0)   # 模糊去噪，否则噪点被当边缘
    edges = cv2.Canny(blur, CANNY_LOW, CANNY_HIGH)  # 双阈值：低于 low 丢弃、高于 high 保留
    return edges


def detect_corners(img: np.ndarray) -> np.ndarray:
    """Shi-Tomasi 角点检测：在图上画出最显著的角点（绿点）。"""
    vis = img.copy()                                # 复制一份，别改原图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(
        gray, maxCorners=CORNER_COUNT, qualityLevel=CORNER_QUALITY, minDistance=10)
    if corners is not None:
        for c in corners:                           # 每个角点画个绿圈
            x, y = int(c[0][0]), int(c[0][1])
            cv2.circle(vis, (x, y), 4, (0, 255, 0), -1)
    return vis


def color_segment(img: np.ndarray) -> np.ndarray:
    """HSV 红色分割：把红色区域抠出来（白=红，黑=其它）。"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)      # BGR→HSV：颜色和结构分开，抗光照
    mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)  # 红色第一段（H≈0）
    mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)  # 红色第二段（H≈179）
    return cv2.bitwise_or(mask1, mask2)             # 两段合起来 = 完整红色


def _load_image(src: str):
    """按参数加载图像：cam=摄像头，否则当文件路径；都失败则用内置测试图。"""
    if src == 'cam':
        cap = cv2.VideoCapture(0)                   # 0=默认摄像头；车上换厂商SDK取流
        if cap.isOpened():
            ok, frame = cap.read()
            cap.release()
            if ok:
                return frame
        print('摄像头打不开，回退到内置测试图')
    img = cv2.imread(src) if src else None
    if img is None:
        # 内置测试图：渐变 + 一个红方块 + 几条线，保证三个算法都有东西可测
        img = np.full((240, 320, 3), 180, dtype=np.uint8)
        cv2.rectangle(img, (60, 60), (160, 160), (0, 0, 220), -1)  # BGR 红块
        cv2.line(img, (10, 10), (300, 200), (50, 50, 50), 3)
        print('用内置测试图（没传路径或路径无效）')
    return img


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else ''
    img = _load_image(src)

    edges = canny_edges(img)
    corners = detect_corners(img)
    mask = color_segment(img)

    # 有 GUI 就显示；无 GUI（纯 SSH / Windows 无显示服务）直接存文件。
    # ★ 用环境变量判断而不是 try/except：imshow 在无 GUI 环境会【挂起】不抛异常，
    #   try/except 接不住，会卡死。先判 DISPLAY 才是可靠做法。
    import os
    has_gui = bool(os.environ.get('DISPLAY')) and sys.platform.startswith('linux')
    if has_gui:
        cv2.imshow('1 original', img)
        cv2.imshow('2 canny edges', edges)
        cv2.imshow('3 corners', corners)
        cv2.imshow('4 red mask', mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        cv2.imwrite('out_edges.png', edges)
        cv2.imwrite('out_corners.png', corners)
        cv2.imwrite('out_redmask.png', mask)
        print('无 GUI，结果已存为 out_edges.png / out_corners.png / out_redmask.png')

    # 打印量化信息——benchmark 表要的数字
    print(f'图像尺寸: {img.shape[1]}x{img.shape[0]}')
    print(f'边缘像素: {int(np.count_nonzero(edges))}（Canny 找到的边缘点）')
    print(f'红色像素: {int(np.count_nonzero(mask))}（HSV 分割出的红色区域）')


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 OpenCV 图像是什么颜色顺序？ → BGR，不是 RGB，搞反红蓝互换
# Q2 为什么 Canny 前要高斯模糊？ → 去噪，否则噪点被当成边缘
# Q3 为什么颜色分割用 HSV 不用 RGB？ → HSV 把颜色和结构分开，抗光照变化
# ─────────────────────────────────────────────────────────────────────

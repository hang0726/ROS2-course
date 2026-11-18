#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day9 · 实例代码：麦克纳姆轮运动学解算节点（全向底盘核心）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  旧小车是两驱/差速，只会"前后 + 转向"；这台车的麦轮底盘能"横着走"。
  上层（Nav2 / 你的键盘）只发一个 Twist（vx, vy, ω），底盘要的是四个轮子的转速。
  本节点就是中间的"翻译官"：订阅 /cmd_vel → 按麦轮逆运动学解算 → 发四轮速度。

【心智模型：麦轮逆运动学】
  给定 chassis 速度 (vx 前后, vy 左右, ω 转向角速度)，四个轮速：
    v_FL = vx - vy - ω·(L+W)/2      # 左前
    v_FR = vx + vy + ω·(L+W)/2      # 右前
    v_RL = vx + vy - ω·(L+W)/2      # 左后
    v_RR = vx - vy + ω·(L+W)/2      # 右后
  其中 L = 前后轮距的一半，W = 左右轮距的一半。
  ★ 符号正负取决于电机安装方向和轮子排列（X型/O型），实机要逐轮校准——
    这就是为什么【待材料：核对实机轮序】。公式是骨架，符号要按实机调。

【为什么µ要归一化 / 限幅】
  ★ 解算出的轮速可能超过电机最大值。直接发会饱和、车走歪。
    正确做法：找最大绝对值，若超限则四个轮子等比缩放（保持方向比例不变）。

【和差速小车的区别（面试会问）】
  差速：v_left = vx - ω·L/2，v_right = vx + ω·L/2（只有两个轮，无 vy）
  麦轮：多一个 vy 横向自由度，四轮解算，能原地横移。

【前置】ROS2 Humble；底盘订阅的四轮话题名【待材料】。
【用法】ros2 run <包> mecanum_cmd  或  python3 mecanum_cmd.py
        然后 ros2 topic pub /cmd_vel ... 用 linear.y 试横移（架空轮子！）
【输出】日志打印每次解算的四轮速度，便于核对方向。
════════════════════════════════════════════════════════════════════
"""

import math                                         # 算轮距系数用（这里保留，扩展时有用）
import rclpy                                        # ROS2 Python 总入口
from rclpy.node import Node                         # 节点基类
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist                 # 上层发来的 chassis 速度 (vx, vy, ω)

# 麦轮底盘订阅的四轮速度话题（【待材料】以实机为准；这里用占位名）
TOPIC_FL = '/wheel_fl_cmd'                          # 左前轮速度
TOPIC_FR = '/wheel_fr_cmd'                          # 右前轮速度
TOPIC_RL = '/wheel_rl_cmd'                          # 左后轮速度
TOPIC_RR = '/wheel_rr_cmd'                          # 右后轮速度
TOPIC_CMD_VEL = '/cmd_vel'                          # 上层输入：chassis 速度
HALF_L = 0.15                                       # 前后轮距的一半（米）【待材料：实测】
HALF_W = 0.13                                       # 左右轮距的一半（米）【待材料：实测】
MAX_WHEEL_SPEED = 1.0                               # 单轮最大速度（m/s）【待材料】
QOS_DEPTH = 10


class MecanumCommander(Node):
    """麦轮运动学节点：/cmd_vel → 四轮速度。"""

    def __init__(self) -> None:
        super().__init__('mecanum_commander')
        # 订阅上层速度指令
        self._cmd_sub = self.create_subscription(
            Twist, TOPIC_CMD_VEL, self.on_cmd_vel, QOS_DEPTH)
        # 发布四个轮子的速度（这里用 Twist.linear.x 承载单轮速度，
        # 【待材料】实机可能用 Float32 / 私有消息，按指导书改类型）
        from std_msgs.msg import Float32
        self._pubs = [
            self.create_publisher(Float32, t, QOS_DEPTH)
            for t in (TOPIC_FL, TOPIC_FR, TOPIC_RL, TOPIC_RR)
        ]
        self.get_logger().info('麦轮运动学节点已启动，等待 /cmd_vel')

    def inverse_kinematics(self, vx: float, vy: float, wz: float) -> tuple:
        """
        麦轮逆运动学：chassis 速度 → 四轮速度。
        返回 (fl, fr, rl, rr)，并做等比限幅。
        """
        coef = HALF_L + HALF_W
        fl = vx - vy - wz * coef                    # 左前
        fr = vx + vy + wz * coef                    # 右前
        rl = vx + vy - wz * coef                    # 左后
        rr = vx - vy + wz * coef                    # 右后
        # 等比限幅：任一超限时，四个一起缩放，保持方向比例
        speeds = [fl, fr, rl, rr]
        peak = max(abs(s) for s in speeds)
        if peak > MAX_WHEEL_SPEED:
            scale = MAX_WHEEL_SPEED / peak
            speeds = [s * scale for s in speeds]
        return tuple(speeds)

    def on_cmd_vel(self, msg: Twist) -> None:
        """收到 chassis 速度：解算四轮 → 发布。回调里只做轻量计算，不 sleep。"""
        vx, vy, wz = msg.linear.x, msg.linear.y, msg.angular.z
        fl, fr, rl, rr = self.inverse_kinematics(vx, vy, wz)
        for pub, speed in zip(self._pubs, (fl, fr, rl, rr)):
            from std_msgs.msg import Float32
            pub.publish(Float32(data=float(speed)))
        self.get_logger().info(
            f'vx={vx:.2f} vy={vy:.2f} wz={wz:.2f} → '
            f'FL={fl:.2f} FR={fr:.2f} RL={rl:.2f} RR={rr:.2f}',
            throttle_duration_sec=0.5,             # 限流，避免刷屏
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MecanumCommander()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 麦轮比差速多哪个自由度？ → vy 横向平移，四轮解算
# Q2 解算轮速后为什么要等比限幅？ → 防止电机饱和、车走歪；等比保持方向比例
# Q3 为什么公式符号要按实机校准？ → 电机安装方向/轮子排列(X型O型)不同，符号会变
# ─────────────────────────────────────────────────────────────────────

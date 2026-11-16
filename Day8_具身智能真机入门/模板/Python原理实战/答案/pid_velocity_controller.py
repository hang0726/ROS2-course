#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pid_velocity_controller.py —— PID 速度闭环（标准范本，逐行注释）

【这是第 2 课：PID 三个参数到底管什么】
你听过 PID 但没写过。这里写一个完整的 PID 控制器，
再用一个「一阶惯性模型」模拟电机，让实际速度在 PID 作用下追上目标速度。
跑起来盯着数字看：改 Kp/Ki/Kd 分别会发生什么，比背定义强十倍。

对应视频：图传版 [1-17] 服务通讯实战：PID 参数获取与调试（16min）。
面试价值：能讲清 P/I/D 各自作用、会调参、知道积分饱和和微分噪声。

【核心原理】
  e = 目标值 - 实际值
  u = Kp·e + Ki·∫e·dt + Kd·(e - e_prev)/dt
  - Kp（比例）：误差越大输出越大，管「快」；太大超调震荡
  - Ki（积分）：累积历史误差，管「消除稳态误差」；太大积分饱和
  - Kd（微分）：误差变化趋势，管「提前刹车抑制震荡」；对噪声敏感

【被控对象：一阶惯性模型】
  真实电机不会瞬间到目标速度，这里用 dv = (u - v)/τ · dt 模拟，
  u 是 PID 输出（可以理解成油门/电压），τ 是惯性时间常数。

【用法】
  source /opt/ros/humble/setup.bash
  python3 答案/pid_velocity_controller.py
  跑起来看 actual 从 0 逐步逼近 target=0.5；改下面常量重跑对比。

【对照练习】练习/my_pid_velocity_controller.py，按 # TODO(n) 编号填。
"""

import rclpy                                         # ROS2 Python 客户端库
from rclpy.node import Node                          # 节点基类

# ---- 可配置项提常量 ----
TARGET_SPEED = 0.5                                   # 目标速度 m/s
KP = 1.2                                             # 比例增益：调大响应快，过大超调
KI = 0.4                                             # 积分增益：消除稳态误差，过大饱和
KD = 0.05                                            # 微分增益：抑制震荡，过大对噪声敏感
TAU = 0.3                                            # 电机惯性时间常数（被控对象参数）
TIMER_PERIOD = 0.1                                   # 控制周期 0.1 秒（10Hz）
OUTPUT_LIMIT = 1.0                                   # 输出限幅（模拟油门上限）
INTEGRAL_LIMIT = 2.0                                 # 积分限幅，防积分饱和（面试高频）


class PID:
    """一个独立的 PID 控制器类——和 ROS2 无关，纯算法，方便单元测试。"""

    def __init__(self, kp, ki, kd, out_limit, integral_limit):
        self.kp = kp                                 # ← 练习 TODO(1)：比例增益
        self.ki = ki                                 # ← 练习 TODO(2)：积分增益
        self.kd = kd                                 # ← 练习 TODO(3)：微分增益
        self.out_limit = out_limit                   # ← 练习 TODO(4)：输出限幅
        self.integral_limit = integral_limit         # ← 练习 TODO(5)：积分限幅（防饱和）
        self.integral = 0.0                          # ← 练习 TODO(6)：积分累积量
        self.prev_error = 0.0                        # ← 练习 TODO(7)：上一拍误差（算微分用）

    def update(self, target, actual, dt):
        """输入目标值、实际值、时间步长，返回 PID 输出 u。"""
        error = target - actual                      # ← 练习 TODO(8)：当前误差 = 目标 - 实际

        # I 项：累积误差 + 限幅（★ 不限幅会积分饱和，超调后迟迟退不回来）
        self.integral += error * dt                  # ← 练习 TODO(9)：积分累加
        self.integral = max(-self.integral_limit,    # ← 练习 TODO(10)：负向限幅
                            min(self.integral_limit, self.integral))  # ← 练习 TODO(11)：正向限幅

        # D 项：误差变化率
        derivative = (error - self.prev_error) / dt  # ← 练习 TODO(12)：微分 = 误差变化 / dt

        # 三项相加
        u = (self.kp * error                         # ← 练习 TODO(13)：P 项
             + self.ki * self.integral               # ← 练习 TODO(14)：I 项
             + self.kd * derivative)                 # ← 练习 TODO(15)：D 项

        # 输出限幅（模拟执行器饱和）
        u = max(-self.out_limit, min(self.out_limit, u))  # ← 练习 TODO(16)

        self.prev_error = error                      # ← 练习 TODO(17)：存下本拍误差给下拍算微分
        return u                                     # ← 练习 TODO(18)


class PIDControllerNode(Node):
    """10Hz 循环：PID 算输出 → 一阶模型更新实际速度 → 打印跟踪过程。"""

    def __init__(self):
        super().__init__('pid_velocity_controller')  # ← 练习 TODO(19)：节点名
        self.pid = PID(KP, KI, KD, OUTPUT_LIMIT, INTEGRAL_LIMIT)  # ← 练习 TODO(20)：建 PID 实例
        self.actual = 0.0                            # ← 练习 TODO(21)：实际速度，初始 0
        self.elapsed = 0.0                           # ← 练习 TODO(22)：计时，用于打印

        # 定时器：每 TIMER_PERIOD 跑一次控制循环
        self.timer = self.create_timer(              # ← 练习 TODO(23)
            TIMER_PERIOD, self.on_timer)

        self.get_logger().info(
            f'PID speed loop start: target={TARGET_SPEED} Kp={KP} Ki={KI} Kd={KD}')

    def on_timer(self):
        """一个控制周期：算 PID → 更新被控对象 → 打印。"""
        dt = TIMER_PERIOD                            # ← 练习 TODO(24)：控制步长

        u = self.pid.update(TARGET_SPEED, self.actual, dt)  # ← 练习 TODO(25)：PID 输出

        # 一阶惯性模型：实际速度往 u 靠拢，不会突变
        dv = (u - self.actual) / TAU * dt            # ← 练习 TODO(26)：速度变化量
        self.actual += dv                            # ← 练习 TODO(27)：更新实际速度

        self.elapsed += dt                           # ← 练习 TODO(28)：累加时间

        # 打印跟踪过程：看 actual 怎么从 0 逼近 target
        self.get_logger().info(                      # ← 练习 TODO(29)
            f't={self.elapsed:.1f}s target={TARGET_SPEED:.3f} '
            f'actual={self.actual:.3f} u={u:.3f} err={TARGET_SPEED - self.actual:+.3f}',
            throttle_duration_sec=0.0,               # 这里想每拍都看，就不限流
        )


def main():
    rclpy.init()                                     # ← 练习 TODO(30)：初始化
    node = PIDControllerNode()                       # ← 练习 TODO(31)：建节点
    try:
        rclpy.spin(node)                             # ← 练习 TODO(32)：事件循环
    finally:
        node.destroy_node()                          # ← 练习 TODO(33)
        if rclpy.ok():
            rclpy.shutdown()                         # ← 练习 TODO(34)


if __name__ == '__main__':
    main()

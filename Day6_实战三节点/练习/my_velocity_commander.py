#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 3 课 / 我的实现：发速度指令（Twist → /cmd_vel）
════════════════════════════════════════════════════════════════════
【状态】练习已完成，可直接运行。对照 ../velocity_commander.py 里的
        `# ← 练习 TODO(n)` 锚点逐条核对自己写的版本。
⚠️ 安全红线：`stop()` 发全 0 速度那一步永远别删；跑之前确认 Nav2 没有正在导航。
【用法】python3 练习/my_velocity_commander.py
【进阶练习】把循环改成走正方形：前进一段、转 90 度，循环四次。
════════════════════════════════════════════════════════════════════
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist

CMD_VEL_TOPIC = '/cmd_vel'
QOS_DEPTH = 10
TIMER_PERIOD_SEC = 0.1
FORWARD_END_SEC = 2.0                            # 第一阶段阈值
TURN_END_SEC = 4.0                               # 第二阶段阈值
FORWARD_SPEED = 0.2
TURN_SPEED = 0.5


class MyVelocityCommander(Node):
    """速度指令发布者：定时下发 Twist，做出「前进→转向→停车」的简单动作。"""

    def __init__(self) -> None:
        super().__init__('my_velocity_commander')   # 与答案节点名区分，可同时跑
        self.pub = self.create_publisher(Twist, CMD_VEL_TOPIC, QOS_DEPTH)
        self.timer = self.create_timer(TIMER_PERIOD_SEC, self.loop)
        self.start = time.time()
        self._stopped = False
        self.get_logger().info(f'开始发速度指令到话题: {CMD_VEL_TOPIC}')

    def _cmd(self, vx: float, wz: float) -> None:
        """构造并发布一条速度消息（差速车只用 linear.x / angular.z）。"""
        msg = Twist()
        msg.linear.x = vx
        msg.angular.z = wz
        self.pub.publish(msg)

    def stop(self) -> None:
        """★ 安全红线：发全 0 速度并停掉定时器；幂等，重复调用无害。"""
        if self._stopped or not rclpy.ok():
            return
        self._stopped = True
        self.timer.cancel()
        self._cmd(0.0, 0.0)
        self.get_logger().info('已发全 0 速度，停车')

    def loop(self) -> None:
        """定时回调：按时间切三个阶段（回调里绝不能 time.sleep）。"""
        t = time.time() - self.start
        if t < FORWARD_END_SEC:
            self._cmd(vx=FORWARD_SPEED, wz=0.0)       # 阶段1：前进 2 秒
        elif t < TURN_END_SEC:
            self._cmd(vx=0.0, wz=TURN_SPEED)          # 阶段2：原地左转 2 秒
        else:
            self.stop()                               # 阶段3：停车
            self.get_logger().info('动作完成（前进→左转→停车）')
            rclpy.shutdown()                          # 让 main 里的 spin 退出


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MyVelocityCommander()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        node.stop()                                   # ★ 安全红线：补发停车
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

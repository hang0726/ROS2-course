#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 2 课 / 我的实现：订阅里程计（Odometry）
════════════════════════════════════════════════════════════════════
【状态】练习已完成，可直接运行。对照 ../odom_subscriber.py 里的
        `# ← 练习 TODO(n)` 锚点逐条核对自己写的版本。
【前置】Day5 导航栈在另一个窗口跑着（Gazebo 才会发里程计）。
【用法】python3 练习/my_odom_subscriber.py              # 默认 /odom
        python3 练习/my_odom_subscriber.py /odometry    # 命令行换话题
【进阶练习】观察车转向和静止时 yaw 的差别。
════════════════════════════════════════════════════════════════════
"""

import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from nav_msgs.msg import Odometry

DEFAULT_TOPIC = '/odom'
QOS_DEPTH = 10
HINT_DELAY_SEC = 5.0
LOG_THROTTLE_SEC = 0.5


class MyOdomSubscriber(Node):
    """里程计订阅者：每收到一条里程计就打印位置、速度与朝向。"""

    def __init__(self, topic: str) -> None:
        super().__init__('my_odom_subscriber')       # 与答案节点名区分，可同时跑
        self.topic = topic
        self.count = 0
        self.sub = self.create_subscription(
            Odometry, topic, self.on_odom, QOS_DEPTH)
        self.hint_timer = self.create_timer(HINT_DELAY_SEC, self.no_data_hint)
        self.get_logger().info(f'开始订阅里程计话题: {topic}')

    def no_data_hint(self) -> None:
        """启动 5 秒还没数据就提醒一次（然后取消定时器，不再刷屏）。"""
        self.hint_timer.cancel()
        if self.count == 0:
            self.get_logger().warn(
                f'5 秒内没收到 {self.topic} 的任何消息。\n'
                '   先跑 ros2 topic list | grep odom 看真实话题名，\n'
                '   再用 python3 练习/my_odom_subscriber.py /<真实话题名> 重跑。\n'
                '   （Day5 的 TB3 仿真是 /odom，不是 /odometry）'
            )

    def on_odom(self, msg: Odometry) -> None:
        """订阅回调：打印位置 / 速度 / 朝向（限流，避免刷屏）。"""
        self.count += 1
        # ★ 两层：外层带协方差，内层才是真值
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation
        v = msg.twist.twist
        # 四元数 → 绕 z 的偏航角（只绕 z 时的标准换算）
        yaw = math.atan2(
            2.0 * (o.w * o.z + o.x * o.y),
            1.0 - 2.0 * (o.y * o.y + o.z * o.z),
        )
        self.get_logger().info(
            f'位置 x={p.x:.3f} y={p.y:.3f} | '
            f'线速度={v.linear.x:.3f} m/s | '
            f'角速度(z)={v.angular.z:.3f} rad/s | '
            f'yaw={yaw:.3f} rad',
            throttle_duration_sec=LOG_THROTTLE_SEC,
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    topic = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC
    node = MyOdomSubscriber(topic)
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

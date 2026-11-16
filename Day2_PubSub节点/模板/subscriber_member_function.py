#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day2 模板 · 订阅者（官方教程风格，复制填空）
==========================================
把下面 TODO 补全，就是一个标准 ROS2 订阅者节点。
注意：话题名和消息类型必须和发布者一致，否则静默收不到。
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String                 # ① 必须和发布者用同一个消息类型


class MinimalSubscriber(Node):
    """最小订阅者：收 /topic 并打印。"""

    def __init__(self):
        super().__init__('minimal_subscriber')
        # TODO ★★★：创建订阅者（消息类型, 话题名, 回调, QoS）
        #   话题名 'topic' 和发布者保持一致
        self.subscription_ = self.create_subscription(
            String, 'topic', self.listener_callback, 10)
        # 在 ROS2 里 subscription 变量要"被引用"以防被垃圾回收，下面这行是官方惯例
        self.subscription_  # 保留引用

    # TODO ★★★：实现订阅回调——msg 里就是收到的数据
    def listener_callback(self, msg):
        self.get_logger().info(f'收到: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = MinimalSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

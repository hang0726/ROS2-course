#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 · 订阅者节点（注册名: listener）
==================================
从话题 'topic' 收消息并打印。运行：
    ros2 run my_robot_course listener
"""

import rclpy                                    # ROS2 的 Python 客户端库
from rclpy.node import Node                     # 节点都继承 Node 基类
from std_msgs.msg import String                 # 标准字符串消息


class Listener(Node):
    """订阅者：从 'topic' 收消息并打印。"""

    def __init__(self):
        super().__init__('mini_subscriber')      # 节点名（全局唯一）
        # 创建订阅者：消息类型、话题名、回调、QoS 队列深度
        # 只要 'topic' 上有新消息，ROS2 就自动调用 listener_callback(msg)
        self.subscription_ = self.create_subscription(
            String, 'topic', self.listener_callback, 10)

    def listener_callback(self, msg):
        """订阅回调：每收到一条消息触发一次，msg 里是发来的数据。"""
        self.get_logger().info(f'收:"{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

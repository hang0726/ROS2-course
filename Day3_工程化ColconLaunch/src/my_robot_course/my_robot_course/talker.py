#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 · 发布者节点（注册名: talker）
==================================
把 Day2 写的发布者收进正式 ROS2 包。每 0.5 秒往话题 'topic' 发一条 std_msgs/String。

运行：
    ros2 run my_robot_course talker
（或用 launch 一条命令起 talker+listener：ros2 launch my_robot_course pubsub.launch.py）
"""

import rclpy                                    # ROS2 的 Python 客户端库
from rclpy.node import Node                     # 节点都继承 Node 基类
from std_msgs.msg import String                 # 标准字符串消息


class Talker(Node):
    """发布者：每 0.5 秒往 'topic' 发一条 Hello World:N。"""

    def __init__(self):
        super().__init__('mini_publisher')       # 节点名（全局唯一）
        # 创建发布者：消息类型、话题名、QoS 队列深度
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        # 定时器：每 0.5 秒自动调用一次 timer_callback
        self.timer_ = self.create_timer(0.5, self.timer_callback)
        self.i = 0                               # 计数器，让每条消息不同

    def timer_callback(self):
        """定时回调：每 0.5 秒被自动调用一次。"""
        msg = String()                           # 新建一条空消息
        msg.data = f'Hello World:{self.i}'        # 填内容
        self.publisher_.publish(msg)             # 真正发出去
        self.get_logger().info(f'发布:"{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    rclpy.spin(node)                             # 常驻处理回调
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

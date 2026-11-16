#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day2 模板 · 发布者（官方教程风格，复制填空）
==========================================
把下面 TODO 补全，就是一个标准 ROS2 发布者节点。
用法：放进 Colcon 包后 `ros2 run 包名 publisher_member_function`
      （Day3 会教你建包；今天先看懂骨架、填空即可）
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String                 # ① 换成你想要的"消息类型"


class MinimalPublisher(Node):
    """最小发布者：定时往 /topic 发消息。"""

    def __init__(self):
        super().__init__('minimal_publisher')   # 节点名（全局唯一）
        # TODO ★★★：创建发布者（消息类型, 话题名, QoS）
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        # TODO ★★：创建定时器，每 0.5 秒调一次 timer_callback
        self.timer_ = self.create_timer(0.5, self.timer_callback)
        self.i = 0                              # 计数，让每条消息不一样

    # TODO ★★★：实现定时回调——造消息、填字段、发布
    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)            # 发出去
        self.get_logger().info(f'发布: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

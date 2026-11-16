#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 练习 · 订阅者节点（请你自己敲！）
===================================
目标：从话题 'topic' 收 std_msgs/String 并打印。
用到：
  - 继承 Node：class Listener(Node): super().__init__('mini_subscriber')
  - self.create_subscription(String, 'topic', self.listener_callback, 10)
  - 回调 listener_callback(self, msg): self.get_logger().info(f'收:"{msg.data}"')
  - main(): rclpy.init(); rclpy.spin(Listener()); rclpy.shutdown()
编译运行：ros2 run my_practice listener（另开终端和 talker 配对）
卡住时对照答案：src/my_robot_course/listener.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


# ===== 在这里写你的 Listener 节点 =====
class Listener(Node):

    def __init__ (self):
        super().__init__('mini_subscription')
        self.subscription_ = self.create_subscription(
            String,'topic',self.listener_callback,10
        )

    def listener_callback(self,msg):
        self.get_logger().info(f"收到:“{msg.data}”")

def main(args=None):
    rclpy.init(args=args)
    node = Listener()                       # 必须加括号实例化，否则 node 是类不是对象
    rclpy.spin(node)#让节点转起来
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

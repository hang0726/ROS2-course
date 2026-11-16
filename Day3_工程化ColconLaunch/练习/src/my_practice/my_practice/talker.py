#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 练习 · 发布者节点（请你自己敲！）
===================================
目标：写一个节点，每隔 0.5 秒往话题 'topic' 发一条 std_msgs/String。
用到：
  - 继承 Node：class Talker(Node): super().__init__('mini_publisher')
  - self.create_publisher(String, 'topic', 10)
  - self.create_timer(0.5, self.timer_callback)
  - 回调里：msg = String(); msg.data = ...; self.publisher_.publish(msg)
  - 打印：self.get_logger().info(f'发布:"{msg.data}"')
  - main(): rclpy.init(); node=Talker(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
编译运行：在 练习/ 目录 colcon build 后 → ros2 run my_practice talker
卡住时对照答案：src/my_robot_course/talker.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


# ===== 在这里写你的 Talker 节点（类名随意，但 main 里要实例化它） =====
class Publisher(Node):
    def __init__(self):
        super().__init__('mini_publisher')
        self.publisher_ = self.create_publisher(String,'topic',10)
        self.timer_ = self.create_timer(0.5,self.timer_callback)#加上_是为了避开冲突
        self.i = 0

    def timer_callback(self):
        msg = String()                     # 实例化一条消息（注意是 String() 不是 String）
        msg.data = f'Hello World{self.i}'
        self.publisher_.publish(msg)        # publish 是动词（发送），publisher_ 是名词（发布者对象）
        self.get_logger().info(f'发布:"{msg.data}"')   # 补上结尾的引号
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    node = Publisher()
    rclpy.spin(node)
    node.destroy_node()                     # 正确方法是 destroy_node()，不是 destroy()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

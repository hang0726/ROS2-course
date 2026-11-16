#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day2 · 发布者/订阅者 演示（你改过的简化版，已修复 3 个 bug）
==========================================================
保留你的命名：发布者节点 mini_publisher / 订阅者节点 mini_subscriber
话题名：topic   消息类型：std_msgs/String   内容：Hello World:N

用法（先在 WSL 里 source 环境，再开两个终端分别跑）：
    source /opt/ros/humble/setup.bash
    cd /mnt/d/具身智能求职培训/Day2_PubSub节点

    终端1：python3 pub_sub_demo.py pub     # 发布者，每 0.5s 发一条
    终端2：python3 pub_sub_demo.py sub     # 订阅者，打印收到的消息
"""

import sys                                      # 读命令行参数，决定启动发布者还是订阅者
import rclpy                                    # ROS2 的 Python 客户端库
from rclpy.node import Node                     # 所有节点都继承 Node 这个基类
from std_msgs.msg import String                 # 标准消息类型：字符串（话题用）


# ============ 订阅者（Subscriber） ============
class Subscriber(Node):
    """订阅者：从 'topic' 收消息并打印。"""

    def __init__(self):
        super().__init__('mini_subscriber')     # 节点名 mini_subscriber（全局唯一）
        # 创建订阅者：消息类型、话题名、回调函数、QoS 队列深度
        # 只要有新消息，ROS2 就自动调用 self.listener_callback(msg)
        self.subscription_ = self.create_subscription(
            String, 'topic', self.listener_callback, 10)

    def listener_callback(self, msg):
        """订阅回调：每收到一条消息触发一次。"""
        self.get_logger().info(f'收:"{msg.data}"')


# ============ 发布者（Publisher） ============
class Publisher(Node):
    """发布者：每 0.5 秒往 'topic' 发一条 Hello World:N。"""

    def __init__(self):
        super().__init__('mini_publisher')       # 节点名 mini_publisher
        # 创建发布者：消息类型、话题名、QoS 队列深度
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        # 创建定时器：每 0.5 秒自动调用一次 self.timer_callback
        self.timer_ = self.create_timer(0.5, self.timer_callback)
        self.i = 0                               # 计数器，让每条消息内容不同

    def timer_callback(self):
        """定时回调：每 0.5 秒被自动调用一次。"""
        msg = String()                           # 新建一条空消息
        msg.data = f'Hello World:{self.i}'        # 填内容
        self.publisher_.publish(msg)             # 真正把消息发出去（修复原 publisher_publisher 笔误）
        self.get_logger().info(f'发布:"{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    # ---- 读取命令行参数，决定启动发布者(pub)还是订阅者(sub) ----
    # sys.argv 是"运行脚本时你敲的参数列表"。比如你输入：python3 pub_sub_demo.py pub
    #   sys.argv[0] = 'pub_sub_demo.py'   ← 脚本名本身，永远占第 0 位
    #   sys.argv[1] = 'pub'              ← 你传的第一个参数
    if len(sys.argv) > 1:        # len>1 表示除了脚本名，你还传了东西
        mode = sys.argv[1]       # 传了 → 用你写的（pub 或 sub）
    else:
        mode = 'pub'            # 没传 → 默认当发布者
    nodes = {'pub': Publisher, 'sub': Subscriber}
    if mode not in nodes:                      # 参数打错给友好提示
        print(f'未知模式: {mode}，可选: {sorted(nodes.keys())}')
        rclpy.shutdown()
        return
    node = nodes[mode]()                        # 实例化对应节点（每个终端只跑一个）
    rclpy.spin(node)                           # 常驻运行，处理该节点的回调
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

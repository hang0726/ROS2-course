#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 · 服务(Service) + 参数(Parameter) 示例
==========================================
1) 加法服务：服务端 /add_two_ints 收到 (a,b) 返回 a+b；客户端请求 2+3。
2) 参数节点：声明 speed 参数，每秒打印当前值，可运行时改。

运行：
    ros2 run my_robot_course add_server      # 服务端（先起）
    ros2 run my_robot_course add_client      # 客户端（请求 2+3）
    ros2 run my_robot_course param_node      # 参数节点
另开终端改参数：ros2 param set /param_node speed 1.5
"""

import rclpy                                    # ROS2 的 Python 客户端库
from rclpy.node import Node                     # 节点都继承 Node 基类
from example_interfaces.srv import AddTwoInts   # 标准服务：两个整数相加


# ============ 服务服务端 ============
class AddServer(Node):
    """加法服务端：收到 (a,b) 返回 (a+b)。"""

    def __init__(self):
        super().__init__('add_server')
        # 创建服务：服务类型、服务名、处理回调
        self.srv = self.create_service(AddTwoInts, '/add_two_ints', self.add_callback)

    def add_callback(self, request, response):
        """服务回调：request 含 a,b；把结果写进 response 并返回。"""
        response.sum = request.a + request.b
        self.get_logger().info(f'收到请求 {request.a}+{request.b}={response.sum}')
        return response


# ============ 服务客户端 ============
class AddClient(Node):
    """加法客户端：请求 2+3 并打印，跑完即退。"""

    def __init__(self):
        super().__init__('add_client')
        self.cli = self.create_client(AddTwoInts, '/add_two_ints')
        # 等服务端上线（每 1s 查一次），否则直接 call 会失败
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等服务端上线...')
        self.req = AddTwoInts.Request()
        self.req.a = 2
        self.req.b = 3

    def run(self):
        future = self.cli.call_async(self.req)               # 异步请求
        rclpy.spin_until_future_complete(self, future)       # 阻塞等结果
        self.get_logger().info(f'结果: 2+3={future.result().sum}')


# ============ 参数示例 ============
class ParamNode(Node):
    """参数节点：声明 speed 参数，每秒打印当前值（可运行时改）。"""

    def __init__(self):
        super().__init__('param_node')
        self.declare_parameter('speed', 0.5)                 # 默认值 0.5
        self.timer = self.create_timer(1.0, self.report)

    def report(self):
        speed = self.get_parameter('speed').value
        self.get_logger().info(f'当前 speed = {speed}')


def main_server(args=None):
    rclpy.init(args=args)
    rclpy.spin(AddServer())
    rclpy.shutdown()


def main_client(args=None):
    rclpy.init(args=args)
    node = AddClient()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


def main_param(args=None):
    rclpy.init(args=args)
    rclpy.spin(ParamNode())
    rclpy.shutdown()


if __name__ == '__main__':
    main_server()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day8_benchmark采样.py —— 导航到达精度自动采样（Sim2Real 对比数据源）

用法：
    # 场景 A：Gazebo 仿真（Day5 那套栈）
    python3 Day8_benchmark采样.py 仿真 0.5 0.0 0.0
    # 场景 B：真车（先把本文件 scp 到车上）
    python3 Day8_benchmark采样.py 真机 0.5 0.0 0.0

它做什么：
    复用 Day6 节点①的 Action 客户端逻辑，发一个导航目标，
    导航结束后从 /amcl_pose 读取真实到达位姿，
    算出「目标点 vs 实际到达点」的误差（米）和耗时（秒），
    以一行 CSV 打印，方便你跑 5 次填进 benchmark 表。

为什么面试加分：
    面试官要的是「数字」，不是「我跑通了」。
    这个脚本让仿真/真机用同一套代码、同一组目标点采样，
    直接产出可对比的误差数据 —— 这就是 Sim2Real 闭环的证据。

依赖：Nav2 导航栈在跑 + 已给 AMCL 初始位姿（见 Day5/阶段 4）。
安全红线：真机第一次跑架空轮子；目标别越出地图边界。
"""

import sys                                          # 命令行参数：场景 + 目标 x y yaw
import time                                         # 记录导航耗时

import rclpy                                        # ROS2 Python 客户端库
from rclpy.node import Node                         # 所有节点都要继承 Node
from rclpy.action import ActionClient               # 导航是 Action，不是 Topic/Service

from nav2_msgs.action import NavigateToPose         # 导航动作类型
from geometry_msgs.msg import PoseStamped           # 目标位姿消息
from geometry_msgs.msg import PoseWithCovarianceStamped  # AMCL 定位消息

ACTION_NAME = 'navigate_to_pose'                    # 导航 Action 名（和 Day6 一致）
SERVER_WAIT_SEC = 10.0                              # 等 Action 服务器的最长时间
GOAL_WAIT_SEC = 60.0                                # 单次导航最长等待，超时记失败
MAP_FRAME = 'map'                                   # 目标坐标系


class BenchmarkNode(Node):
    """发导航目标 → 等结果 → 读 /amcl_pose → 输出误差 CSV 的节点。"""

    def __init__(self, scene, tx, ty, tyaw):
        super().__init__('day8_benchmark')           # 节点名
        self.scene = scene                          # '仿真' 或 '真机'，仅用于 CSV 标签
        self.target = (tx, ty, tyaw)                # 目标 (x, y, yaw)
        self._client = ActionClient(self, NavigateToPose, ACTION_NAME)  # 创建 Action 客户端
        self._actual = None                         # 到达后的真实位姿，回调里填
        self._start = 0.0                           # 导航起始时间（time.time 秒）
        # 订阅 AMCL 定位，只留最后一次位姿作为「实际到达点」
        self._sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._on_pose,
            10,                                     # QoS 队列深度
        )

    def _on_pose(self, msg):
        """AMCL 每来一帧就更新实际位置；导航结束后读最后一次即可。"""
        p = msg.pose.pose.position                  # 取两层结构里的位置
        self._actual = (p.x, p.y)                   # 只存 x/y，误差按平面距离算

    def run(self):
        """完整跑一次采样，返回一行 CSV 字符串。"""
        # 1) 等服务器
        if not self._client.wait_for_server(timeout_sec=SERVER_WAIT_SEC):
            return self._csv('失败', '', '', '无导航服务器')

        # 2) 组目标（四元数由 yaw 换算，公式同 Day6）
        import math                                 # 放在函数内，避免导入顺序干扰讲解
        goal = NavigateToPose.Goal()                # 空目标对象
        pose = PoseStamped()                        # 目标位姿
        pose.header.frame_id = MAP_FRAME            # 坐标系必须是 map
        pose.header.stamp = self.get_clock().now().to_msg()  # 时间戳
        pose.pose.position.x = self.target[0]       # 目标 x
        pose.pose.position.y = self.target[1]       # 目标 y
        pose.pose.orientation.z = math.sin(self.target[2] / 2.0)  # 四元数 z
        pose.pose.orientation.w = math.cos(self.target[2] / 2.0)  # 四元数 w
        goal.pose = pose                            # 塞进 Action 目标

        # 3) 发目标 + 等结果
        self._start = time.time()                   # 开始计时
        future = self._client.send_goal_async(goal)  # 异步发送
        # 用 rclpy.spin_until_future_complete 驱动回调，等到「目标被接受/拒绝」
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVER_WAIT_SEC)
        if not future.done() or not future.result().accepted:
            return self._csv('失败', '', '', '目标被拒')

        # 4) 等导航结束（拿到 result）
        result_future = future.result().get_result_async()  # 结果 future
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=GOAL_WAIT_SEC)
        elapsed = time.time() - self._start         # 耗时（秒）
        if not result_future.done():
            return self._csv('失败', f'{elapsed:.2f}', '', '超时')

        status = result_future.result().result      # 导航结果
        # 状态码：4 = SUCCEEDED，其他（如 6 ABORTED）都算失败
        code = getattr(status, 'error_code', -1)
        if code != 4:
            return self._csv('失败', f'{elapsed:.2f}', '', f'状态码{code}')

        # 5) 算到达误差
        if self._actual is None:                    # 没收到定位 = 数据无效
            return self._csv('成功', f'{elapsed:.2f}', '', '无/amcl_pose')
        dx = self._actual[0] - self.target[0]       # x 方向偏差
        dy = self._actual[1] - self.target[1]       # y 方向偏差
        err = math.sqrt(dx * dx + dy * dy)          # 平面欧氏误差（米）
        return self._csv('成功', f'{elapsed:.2f}', f'{err:.3f}', '')

    def _csv(self, result, elapsed, err_m, note):
        """拼一行 CSV：场景,结果,耗时s,误差m,备注。"""
        return f'{self.scene},{result},{elapsed},{err_m},{note}'


def main():
    if len(sys.argv) != 5:                          # 检查参数个数
        print('用法: python3 Day8_benchmark采样.py <仿真|真机> <x> <y> <yaw>')
        sys.exit(1)
    scene = sys.argv[1]                             # 场景标签
    tx, ty, tyaw = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])  # 目标

    rclpy.init()                                    # 初始化 ROS2
    node = BenchmarkNode(scene, tx, ty, tyaw)       # 建节点
    try:
        line = node.run()                           # 跑一次采样
        print('场景,结果,耗时s,误差m,备注')          # CSV 表头
        print(line)                                 # 数据行（复制这个填 benchmark 表）
    finally:
        node.destroy_node()                         # 销毁节点
        if rclpy.ok():
            rclpy.shutdown()                        # 关闭 ROS2


if __name__ == '__main__':
    main()

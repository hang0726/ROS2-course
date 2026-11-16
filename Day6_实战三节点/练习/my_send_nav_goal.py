#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 1 课 / 我的实现：发导航目标（Action 客户端）
════════════════════════════════════════════════════════════════════
【状态】练习已完成，可直接运行。对照 ../send_nav_goal.py 里的
        `# ← 练习 TODO(n)` 锚点逐条核对自己写的版本。
【前置】Day5 导航栈在另一个窗口跑着（桌面 bat 选 [4]），
        RViz 里点过 2D Pose Estimate 给 AMCL 初始位姿。
【用法】python3 练习/my_send_nav_goal.py                # 默认 (0.5, 0.0, 0.0)
        python3 练习/my_send_nav_goal.py 2.0 1.0 1.57   # x y yaw(弧度)
【进阶练习】把目标改成 (2.0, 1.0)，再连发第二个点让车走折线。先观察会发生什么。
════════════════════════════════════════════════════════════════════
"""

import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Quaternion
from action_msgs.msg import GoalStatus

ACTION_NAME = 'navigate_to_pose'
SERVER_WAIT_SEC = 10.0
MAP_FRAME = 'map'
DEFAULT_X = 0.5                                  # 地图内（x 上限 1.01，别写 1.0）
DEFAULT_Y = 0.0
DEFAULT_YAW = 0.0
FEEDBACK_THROTTLE_SEC = 1.0


class MyNavGoalClient(Node):
    """导航目标客户端：连 Nav2 的 /navigate_to_pose，发一个目标位姿。"""

    def __init__(self):
        super().__init__('my_nav_goal_client')       # 与答案节点名区分，可同时跑
        self.client = ActionClient(self, NavigateToPose, ACTION_NAME)

    def send_goal(self, x: float, y: float, yaw: float) -> bool:
        """发一个导航目标；连不上服务端返回 False。"""
        self.client.wait_for_server(timeout_sec=SERVER_WAIT_SEC)
        if not self.client.server_is_ready():
            self.get_logger().error(
                '10 秒内没等到 /navigate_to_pose 服务端。\n'
                '   先按 Day5 起导航栈（桌面 bat 选 [4]），RViz 里再给 2D Pose Estimate。\n'
                '   自查命令： ros2 action list | grep navigate_to_pose'
            )
            return False
        self.get_logger().info('已连上 /navigate_to_pose 服务端')

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = MAP_FRAME
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation = self._yaw_to_quat(yaw)

        self.get_logger().info(f'发送导航目标 (x={x:.2f}, y={y:.2f}, yaw={yaw:.2f})')
        self._send_future = self.client.send_goal_async(
            goal, feedback_callback=self.feedback_cb)
        self._send_future.add_done_callback(self.goal_response_cb)
        return True

    def goal_response_cb(self, future) -> None:
        """① 接受 / 拒绝，只来一次。"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('目标被拒绝（多半没给 AMCL 初始位姿 / 没地图）')
            # 被拒不会再有 result_cb，必须主动关上下文，让 spin 退出
            rclpy.shutdown()
            return
        self.get_logger().info('目标被接受，开始规划与导航')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_cb)

    def feedback_cb(self, feedback_msg) -> None:
        """② 导航进度，反复来。"""
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'  剩余距离 {fb.distance_remaining:.2f} m',
            throttle_duration_sec=FEEDBACK_THROTTLE_SEC,
        )

    def result_cb(self, future) -> None:
        """③ 最终状态，只来一次。"""
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('导航成功到达目标')
        else:
            self.get_logger().warn(
                f'导航结束，状态码 {status}（4=成功，其它=失败/取消）')
        rclpy.shutdown()

    @staticmethod
    def _yaw_to_quat(yaw: float) -> Quaternion:
        """绕 z 轴偏航角 → 四元数：q = (0, 0, sin(θ/2), cos(θ/2))。"""
        q = Quaternion()
        q.z = math.sin(yaw / 2.0)
        q.w = math.cos(yaw / 2.0)
        return q


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MyNavGoalClient()
    x = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_X
    y = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_Y
    yaw = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_YAW
    try:
        if node.send_goal(x, y, yaw):
            rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

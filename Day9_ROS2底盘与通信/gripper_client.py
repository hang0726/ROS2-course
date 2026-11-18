#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day9 · 实例代码：夹爪服务客户端（ROS2 Service 实战，官方实验23/25）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  控制夹爪"张开/闭合"是典型的 service 场景——一问一答、要结果。
  这是你 Day3 学的 service 在真机上的落地，也是 Day12 机械臂抓取的最后一步。

【心智模型：Service vs Topic（面试高频）】
  Topic   = 广播：连续、无应答、发完不管  → 速度指令 /cmd_vel
  Service = 点餐：一问一答、有返回结果    → "开夹爪" 这种一次性指令
  Action  = 下单+物流：请求/进度/结果      → 导航 /navigate_to_pose（Day11）

【为什么夹爪用 service 不用 topic】
  ★ 你只关心"开还是关、开成功了没"，不需要 10Hz 连续发。service 一次调用拿返回值，
    正好。真要"夹多紧"这种连续量，才用 topic。

【前置】夹爪服务已由厂商节点提供（【待材料】服务名与消息类型）。
【用法】python3 gripper_client.py open      # 张开
        python3 gripper_client.py close     # 闭合
        python3 gripper_client.py           # 查服务在不在
════════════════════════════════════════════════════════════════════
"""

import sys                                          # 读命令行参数 open/close
import rclpy                                        # ROS2 Python 总入口
from rclpy.node import Node                         # 节点基类
from rclpy.executors import ExternalShutdownException

# 【待材料】以学校指导书为准：服务名、消息类型、字段
SERVICE_NAME = '/gripper_control'                   # 夹爪服务名（占位，待核对）
SERVER_WAIT_SEC = 5.0                               # 等服务上线超时


class GripperClient(Node):
    """夹爪 service 客户端：发开/关请求，等返回结果。"""

    def __init__(self) -> None:
        super().__init__('gripper_client')
        # 【待材料】消息类型换成厂商提供的（这里用 std_srvs/SetBool 做通用示例：
        #   data=True 张开，False 闭合——很多夹爪服务就是这个结构）
        from std_srvs.srv import SetBool
        self._cli = self.create_client(SetBool, SERVICE_NAME)

    def call(self, open_gripper: bool) -> bool:
        """调用夹爪服务；成功返回 True。"""
        from std_srvs.srv import SetBool
        if not self._cli.wait_for_service(timeout_sec=SERVER_WAIT_SEC):
            self.get_logger().error(
                f'{SERVER_WAIT_SEC}s 没等到服务 {SERVICE_NAME}。'
                '自查：ros2 service list | grep gripper；确认机械臂节点已起。')
            return False
        req = SetBool.Request()
        req.data = open_gripper                     # True=张开，False=闭合
        future = self._cli.call_async(req)
        # ★ service 是同步语义：发完等结果。用 spin_until_future_complete 阻塞等返回。
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVER_WAIT_SEC)
        if future.done():
            resp = future.result()
            self.get_logger().info(
                f'夹爪{"张开" if open_gripper else "闭合"}：'
                f'success={resp.success}, message={resp.message}')
            return bool(resp.success)
        self.get_logger().warn('服务调用超时，没拿到返回结果')
        return False


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GripperClient()
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        open_gripper = action == 'open'
        try:
            node.call(open_gripper)
        except (KeyboardInterrupt, ExternalShutdownException):
            node.get_logger().info('用户中断，退出')
        finally:
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
    else:
        node.get_logger().info('用法：gripper_client.py open | close')


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 夹爪为什么用 service 不用 topic？ → 一问一答要结果，不需连续发
# Q2 service 和 action 区别？ → service 无进度；action 有请求/进度/结果/可取消
# Q3 spin_until_future_complete 在等什么？ → 等服务端的返回结果（service 同步语义）
# ─────────────────────────────────────────────────────────────────────

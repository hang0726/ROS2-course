#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 1 课 / 标准参考答案：发导航目标（NavigateToPose Action 客户端）
════════════════════════════════════════════════════════════════════
★ 这份文件是【对照基准】，练习在 练习/my_send_nav_goal.py（11 个 TODO）。
  答案里每个关键行都标了 `# ← 练习 TODO(n)`，编号与练习里的 # TODO(n)
  一一对应，填完可以按编号逐条核对。

【本文件遵守的标准写法（三份答案一致，可照抄这个习惯）】
  ① 可配置项一律提成模块常量，代码里不散落魔法数字；
  ② 方法名 / 参数 / 顺序与练习骨架完全一致，方便并排对照；
  ③ 公开方法带类型注解与 docstring；
  ④ main() 统一收尾：destroy_node → 判断 rclpy.ok() → shutdown，不用 pass；
  ⑤ 日志纯文本（WSL 终端不依赖 emoji 字体），讲解只写进注释。
  ⚠️ 练习里直接写字符串 / 数字就是对的；答案用常量是工程习惯，不是硬要求。

【心智模型】ROS2 三种通信方式，Day6 一天全碰到：
  Topic   话题 = 广播电台：单向、发完不管、无状态      → 节点②③
  Service 服务 = 点餐问答：一问一答、无状态            → Day3 add_two_ints
  Action  动作 = 下单+物流跟踪：请求/进度/结果、有状态  → 本文件

  导航为什么非得用 Action？四个理由，缺一个写出来的导航就是残废：
    ① 要知道目标「被没被接受」（没定位时 Nav2 会拒）
    ② 要知道「走到哪了」（剩余距离）
    ③ 要知道最后是「成功 / 失败 / 被取消」
    ④ 要能「中途取消」（撞人前刹车）
  话题只告诉你「发出去了」，后面全盲。

  三段回调时序（记住谁先谁后）：
    你的节点                        Nav2 action server
       |---- send_goal_async ------>|
       |<--- goal_response_cb ------|  ① 接受/拒绝，只来一次
       |<--- feedback_cb -----------|  ② 剩余距离，反复来
       |<--- result_cb -------------|  ③ 最终状态，只来一次

【两个最容易卡住的原理】
  ★ rclpy.spin() 不是「启动 ROS2」，它是【事件循环】，负责把消息派发给回调。
    所以三套回调必须等 spin() 转起来才触发 → main() 里先 send_goal、再 spin。
    而 wait_for_server() 只是同步轮询 server_is_ready()（Humble
    action/client.py:587），不依赖回调，放在 spin 之前完全合法。
  ★ 绕 z 轴转 θ 的四元数：q = (0, 0, sin(θ/2), cos(θ/2))，只填 z/w。
    把 sin 填进 x 是绕 x 轴翻车，车会当场躺下。

【前置】Day5 导航栈在另一个窗口跑着（桌面 bat 选 [4]），
        RViz 里点过 2D Pose Estimate 给 AMCL 初始位姿。
【用法】python3 send_nav_goal.py                # 默认 (0.5, 0.0, 0.0)
        python3 send_nav_goal.py 2.0 1.0 1.57   # x y yaw(弧度)
════════════════════════════════════════════════════════════════════
"""

import sys                                        # 读命令行参数 x / y / yaw
import math                                       # sin / cos，四元数公式要用
import rclpy                                      # ROS2 Python 总入口：init / spin / shutdown
from rclpy.node import Node                       # 节点基类，提供 create_* / get_logger / get_clock
from rclpy.action import ActionClient             # Action【客户端】；服务端在 Nav2 那边
from rclpy.executors import ExternalShutdownException
# ↑ 上下文被 shutdown 时 spin() 会抛这个异常；接住它才不会打印一串 traceback
from nav2_msgs.action import NavigateToPose       # 目标消息类型，核心字段是 .pose（PoseStamped）
from geometry_msgs.msg import PoseStamped, Quaternion
# ↑ PoseStamped = 坐标系(frame_id) + 时间戳(stamp) + 位置(position) + 朝向(orientation)
from action_msgs.msg import GoalStatus            # 状态码常量，STATUS_SUCCEEDED == 4

# ── 可配置项集中在这里（练习里的空位直接写对应值即可）──────────────
ACTION_NAME = 'navigate_to_pose'                  # ← 练习 TODO(1)：action 名
SERVER_WAIT_SEC = 10.0                           # ← 练习 TODO(2)：等待超时
MAP_FRAME = 'map'                                # ← 练习 TODO(3)：坐标系
DEFAULT_X = 0.5                                  # 默认目标（★ 地图 x 上限 1.01，别写 1.0 越界）
DEFAULT_Y = 0.0
DEFAULT_YAW = 0.0
FEEDBACK_THROTTLE_SEC = 1.0                      # 进度日志限流，避免刷屏


class NavGoalClient(Node):
    """导航目标客户端：连 Nav2 的 /navigate_to_pose，发一个目标位姿。"""

    def __init__(self) -> None:
        super().__init__('nav_goal_client')          # 节点名，ros2 node list 里能看到
        # ActionClient 三要素，缺一不可：
        #   ① 节点自己 self  ② 消息类型 NavigateToPose  ③ action 名
        # 写错类型 → 服务端不认这个客户端（连不上）；写错名字 → wait_for_server 超时。
        self.client = ActionClient(self, NavigateToPose, ACTION_NAME)   # ← 练习 TODO(1)

    def send_goal(self, x: float, y: float, yaw: float) -> bool:
        """发一个导航目标（x/y 单位米，yaw 单位弧度）；成功发出返回 True。"""
        # 最多等 10 秒服务端上线。★ 不加超时的话，没起 Day5 栈就永久干等。
        self.client.wait_for_server(timeout_sec=SERVER_WAIT_SEC)         # ← 练习 TODO(2)
        # ★ 用 server_is_ready() 判定，不依赖 wait_for_server 的返回值（各 rclpy 版本不一致）
        if not self.client.server_is_ready():
            self.get_logger().error(
                '10 秒内没等到 /navigate_to_pose 服务端。\n'
                '   先按 Day5 起导航栈（桌面 bat 选 [4]），RViz 里再给 2D Pose Estimate。\n'
                '   自查命令： ros2 action list | grep navigate_to_pose'
            )
            return False
        self.get_logger().info('已连上 /navigate_to_pose 服务端')

        goal = NavigateToPose.Goal()                  # 构造目标；字段只有一个 .pose
        goal.pose = PoseStamped()
        # ① 坐标系：目标坐标是相对【地图原点】说的。写 'odom' 或 'base_link' 会让目标
        #    跟着车漂移，Nav2 直接算错。
        goal.pose.header.frame_id = MAP_FRAME                            # ← 练习 TODO(3)
        # ② 时间戳：TF 变换按时间查，别填 0 或过期时间，否则报 extrapolation。
        goal.pose.header.stamp = self.get_clock().now().to_msg()        # ← 练习 TODO(4)
        # ③ 位置：单位米，坐标来自 Day4 建的 tb3_map。
        goal.pose.pose.position.x = x                                   # ← 练习 TODO(5)
        goal.pose.pose.position.y = y                                   # ← 练习 TODO(5)
        # ④ 朝向：ROS2 姿态一律用四元数，不能直接把 yaw 塞进去。
        goal.pose.pose.orientation = self._yaw_to_quat(yaw)

        self.get_logger().info(f'发送导航目标 (x={x:.2f}, y={y:.2f}, yaw={yaw:.2f})')
        # 异步发目标 + 挂【反馈回调】；注意这只是注册，回调要等 spin() 才真正触发
        self._send_future = self.client.send_goal_async(
            goal, feedback_callback=self.feedback_cb)                    # ← 练习 TODO(6)
        # 再挂【接受/拒绝回调】：send_goal_async 返回的 Future 完成时触发
        self._send_future.add_done_callback(self.goal_response_cb)
        return True

    def goal_response_cb(self, future) -> None:
        """①【接受 / 拒绝】三段回调第一段，只来一次。"""
        goal_handle = future.result()                 # 拿回 goal handle
        if not goal_handle.accepted:
            self.get_logger().error('目标被拒绝（多半没给 AMCL 初始位姿 / 没地图）')
            # ★ 被拒时不会再有 result_cb，spin() 会永远空转（现象：终端不动、只能 Ctrl+C）。
            #   必须主动关上下文，让 main 里的 spin 退出。
            rclpy.shutdown()                                             # ← 练习 TODO(7)
            return
        self.get_logger().info('目标被接受，开始规划与导航')
        # 拿「最终结果」的 Future，再挂第三段回调（两行，对应练习 TODO(8)）
        self._get_result_future = goal_handle.get_result_async()        # ← 练习 TODO(8)
        self._get_result_future.add_done_callback(self.result_cb)       # ← 练习 TODO(8)

    def feedback_cb(self, feedback_msg) -> None:
        """②【进度】三段回调第二段，导航途中反复来。"""
        fb = feedback_msg.feedback
        # throttle_duration_sec：同一条日志 1 秒最多打印一次，否则刷屏看不清
        self.get_logger().info(
            f'  剩余距离 {fb.distance_remaining:.2f} m',
            throttle_duration_sec=FEEDBACK_THROTTLE_SEC,
        )

    def result_cb(self, future) -> None:
        """③【最终结果】三段回调第三段，只来一次。"""
        status = future.result().status               # 拿状态码
        if status == GoalStatus.STATUS_SUCCEEDED:    # ← 练习 TODO(9)：成功对应的状态码
            self.get_logger().info('导航成功到达目标')
        else:
            self.get_logger().warn(
                f'导航结束，状态码 {status}（4=成功，其它=失败/取消）')
        rclpy.shutdown()                              # 导航结束，让 main 里的 spin 退出

    @staticmethod
    def _yaw_to_quat(yaw: float) -> Quaternion:
        """
        绕 z 轴偏航角 yaw → 四元数（平面导航只绕 z 转）。

        公式：q = (x, y, z, w) = (0, 0, sin(θ/2), cos(θ/2))
        验算：θ=0 → (0,0,0,1) 单位四元数；θ=π → (0,0,1,0) 转 180°。
        ⚠️ 只填 z/w，别把 sin 填进 x（那是绕 x 轴翻车）。
        """
        q = Quaternion()
        q.z = math.sin(yaw / 2.0)                                       # ← 练习 TODO(10)
        q.w = math.cos(yaw / 2.0)                                       # ← 练习 TODO(10)
        return q


def main(args=None) -> None:
    rclpy.init(args=args)                             # 初始化 ROS2 上下文
    node = NavGoalClient()
    # 从命令行取目标，缺省 (0.5, 0.0, 0.0)。生产代码建议换 argparse / ROS2 参数，
    # 这里保持与练习骨架一致的写法，方便并排对照。
    x = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_X
    y = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_Y
    yaw = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_YAW
    try:
        if node.send_goal(x, y, yaw):                 # 连不上服务端就跳过 spin
            # ★ 顺序不能反：先注册三套回调，再让事件循环转起来。
            #   spin() 不负责「启动 ROS2」，它只把消息派发给已注册的回调。
            rclpy.spin(node)                                             # ← 练习 TODO(11)
    except (KeyboardInterrupt, ExternalShutdownException):
        # ★ 标准写法：不用 pass，明确记一句退出原因（Ctrl+C / 上下文被关都算正常退出）
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        # 固定收尾三件套，三份答案顺序一致
        node.destroy_node()
        if rclpy.ok():                               # 避免重复 shutdown 报错
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 导航为什么不用话题？    → 要「接受/反馈/结果/可取消」，action 自带
# Q2 rclpy.spin() 在干什么？ → 事件循环，派发消息给回调；不负责启动 ROS2
# Q3 frame_id 为什么是 map？ → 目标相对地图原点；写 base_link 会跟着车漂移
# ─────────────────────────────────────────────────────────────────────

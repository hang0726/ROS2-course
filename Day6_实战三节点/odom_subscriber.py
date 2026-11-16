#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 2 课 / 标准参考答案：订阅里程计（Odometry）
════════════════════════════════════════════════════════════════════
★ 这份文件是【对照基准】，练习在 练习/my_odom_subscriber.py（9 个 TODO）。
  答案里每个关键行都标了 `# ← 练习 TODO(n)`，编号与练习里的 # TODO(n)
  一一对应，填完可以按编号逐条核对。

【本文件遵守的标准写法（三份答案一致，可照抄这个习惯）】
  ① 可配置项一律提成模块常量，代码里不散落魔法数字；
  ② 方法名 / 参数 / 顺序与练习骨架完全一致（`__init__(self, topic)` 不带默认值）；
  ③ 公开方法带类型注解与 docstring；
  ④ main() 统一收尾：destroy_node → 判断 rclpy.ok() → shutdown，不用 pass；
  ⑤ 日志纯文本，且输出格式与练习骨架里那几行 f-string 完全一致，方便比对。
  ⚠️ 练习里直接写字符串 / 数字就是对的；答案用常量是工程习惯，不是硬要求。

【★ 最容易踩的坑：为什么是两层 pose】
  nav_msgs/Odometry 的结构：
    Odometry
    ├── header / child_frame_id
    ├── pose                    ← 外层：PoseWithCovariance（带协方差，是个容器）
    │   └── pose                ← 内层：真正的 Pose
    │       ├── position    (x, y, z)
    │       └── orientation (x, y, z, w)
    └── twist                   ← 外层：TwistWithCovariance
        └── twist               ← 内层：真正的 Twist
            ├── linear  (x, y, z)
            └── angular (x, y, z)
  写成 msg.pose.position 会直接 AttributeError。

【QoS 10 是什么】回调来不及处理时最多缓存 10 条，超了丢【旧帧】。
  里程计 20~50Hz，10 条只够 0.2~0.5 秒 —— 对「看当前位置」正是我们要的：
  宁可丢旧的，也别拿过期数据。
  ⚠️ 别写 0：ROS2 里 0 不是「无限」，要传感器语义得用 qos_profile_sensor_data。

【为什么加 throttle】里程计 20~50Hz，不限流一秒刷几十行，位置变化全被冲走。
  throttle_duration_sec=0.5 → 限到 2Hz。同一个 logger 还支持 once=True。

【为什么只做「5 秒没数据」提醒，不自动探测话题】
  DDS 节点发现需要时间，刚启动查 get_publishers_info_by_topic() 大概率返回空，
  自动换话题反而误判成「这个话题不存在」。等 5 秒看有没有真收到消息最可靠，
  而且只提醒、不替你做决定（自己跑 ros2 topic list 确认）。

【练习 TODO(6)：四元数怎么换成 yaw】
  只绕 z 轴时，yaw = atan2(2*(w*z + x*y), 1 - 2*(y² + z²))。
  标准库 math 就够，不必装 tf_transformations（Humble 里不一定有）。
  验算：静止朝 x 轴 (0,0,0,1) → yaw=0；转 180° (0,0,1,0) → yaw=π。

【★ /odom 是查出来的，不是背的】
  /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf
      <odometry_topic>odom</odometry_topic>
  Gazebo 差速驱动插件按这行发布话题。旧版默认 /odometry 会静默零输出、不报错。
  换机器人就跑： ros2 topic list | grep -i odom

【用法】python3 odom_subscriber.py            # 默认 /odom
        python3 odom_subscriber.py /odometry  # 命令行覆盖话题名
════════════════════════════════════════════════════════════════════
"""

import sys
import math                                       # atan2：四元数 → yaw
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException   # 上下文被关时 spin 会抛它
from nav_msgs.msg import Odometry                        # 里程计消息（含 pose + twist）

# ── 可配置项集中在这里（练习里的空位直接写对应值即可）──────────────
DEFAULT_TOPIC = '/odom'                          # ← 练习 TODO(1)：默认话题名
QOS_DEPTH = 10                                   # ← 练习 TODO(2)：QoS 队列深度
HINT_DELAY_SEC = 5.0                            # ← 练习 TODO(8)：体检定时器周期
LOG_THROTTLE_SEC = 0.5                          # ← 练习 TODO(7)：日志限流周期


class OdomSubscriber(Node):
    """里程计订阅者：每收到一条里程计就打印位置、速度与朝向。"""

    def __init__(self, topic: str) -> None:
        super().__init__('odom_subscriber')       # 节点名
        self.topic = topic                        # 记下来，告警里要显示
        self.count = 0                           # 已收到的消息条数（判断「有没有数据」）
        # create_subscription 四个参数：消息类型 / 话题名 / 回调函数 / QoS 队列深度
        # QoS=10 见模块 docstring；这里的 self.on_odom 是【函数对象】，别写成 self.on_odom()
        self.sub = self.create_subscription(
            Odometry, topic, self.on_odom, QOS_DEPTH)                   # ← 练习 TODO(2)
        # 一次性体检定时器：5 秒后若一条都没收到，提示话题名可能不对
        self.hint_timer = self.create_timer(
            HINT_DELAY_SEC, self.no_data_hint)                          # ← 练习 TODO(8)
        self.get_logger().info(f'开始订阅里程计话题: {topic}')

    def no_data_hint(self) -> None:
        """启动 5 秒还没数据就提醒一次（然后取消定时器，不再刷屏）。"""
        self.hint_timer.cancel()                  # cancel() 只提醒一次，不然每 5 秒刷一遍
        if self.count == 0:
            self.get_logger().warn(
                f'5 秒内没收到 {self.topic} 的任何消息。\n'
                '   先跑 ros2 topic list | grep odom 看真实话题名，\n'
                '   再用 python3 odom_subscriber.py /<真实话题名> 重跑。\n'
                '   （Day5 的 TB3 仿真是 /odom，不是 /odometry）'
            )

    def on_odom(self, msg: Odometry) -> None:
        """订阅回调：msg 里是机器人的位姿 (pose) 和速度 (twist)。"""
        self.count += 1
        # ★ 两层：外层带协方差，内层才是真值。下面三行都不能少一层。
        p = msg.pose.pose.position                # ← 练习 TODO(3)：位置
        o = msg.pose.pose.orientation            # ← 练习 TODO(4)：姿态四元数
        v = msg.twist.twist                      # ← 练习 TODO(5)：速度
        # 四元数 → 绕 z 的偏航角（公式见模块 docstring）；练习 TODO(6) 的进阶题
        yaw = math.atan2(
            2.0 * (o.w * o.z + o.x * o.y),
            1.0 - 2.0 * (o.y * o.y + o.z * o.z),
        )                                                                # ← 练习 TODO(6)
        # throttle_duration_sec：里程计 20~50Hz，限流到 2Hz，免得刷屏看不清
        # ★ 这五行 f-string 与练习骨架逐字一致，填完可以直接比对输出
        self.get_logger().info(
            f'位置 x={p.x:.3f} y={p.y:.3f} | '
            f'线速度={v.linear.x:.3f} m/s | '
            f'角速度(z)={v.angular.z:.3f} rad/s | '
            f'yaw={yaw:.3f} rad',
            throttle_duration_sec=LOG_THROTTLE_SEC,                     # ← 练习 TODO(7)
        )


def main(args=None) -> None:
    rclpy.init(args=args)                        # 初始化 ROS2 上下文
    topic = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC         # ← 练习 TODO(1)
    node = OdomSubscriber(topic)
    try:
        # ★ spin() 是事件循环：订阅回调靠它驱动，不加就一条消息都收不到
        rclpy.spin(node)                                                 # ← 练习 TODO(9)
    except (KeyboardInterrupt, ExternalShutdownException):
        # ★ 标准写法：不用 pass，明确记一句退出原因
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        # 固定收尾三件套，三份答案顺序一致
        node.destroy_node()
        if rclpy.ok():                           # 避免重复 shutdown 报错
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 为什么要写 msg.pose.pose.position？ → 外层是带协方差的容器，内层才是 Pose
# Q2 QoS 那个 10 是什么？                 → 队列深度，超了丢旧帧；0 不是无限
# Q3 本机里程计话题是哪个？怎么确认？      → /odom；ros2 topic list | grep -i odom
# ─────────────────────────────────────────────────────────────────────

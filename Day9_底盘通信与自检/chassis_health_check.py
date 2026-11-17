#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day9 · 实例代码：底盘通信健康检查节点（把命令行自检变成一个节点）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  笔记 Day9 的步骤 2 是手动敲三条命令：topic list / echo / hz。
  但真机调试时你要反复敲、还要盯着"有没有数据、多久没来了"。
  本节点把这件事自动化：一次订阅 4 个关键话题，按周期打印一份体检报告，
  直接告诉你哪个话题"通/不通/多久没来"——这就是岗位 JD 里反复写的
  "故障排查：通信异常 / 传感器无数据"的实战雏形。

【心智模型：判断"话题通不通"的三个层次】
  ① 话题在不在     —— ros2 topic list 能看到名字（本节点不管这层，交给自检 shell）
  ② 有没有数据     —— 订阅后回调被触发过（本节点用 msg_count > 0 判定）
  ③ 数据新不新鲜   —— 最后一条消息距今多久（★ 最关键：有数据但卡住=假通）
     比如 /odom 曾经来过、现在 10 秒不动了 = 编码器线松了或底盘节点挂了，
     只看"有没有"会误判成正常，必须看"新鲜度"。

【为什么用定时器而不是在回调里 sleep】
  ★ 回调里禁止 time.sleep()/死循环——那会阻塞整个单线程执行器，
    其它话题的回调全被卡住（Day6 讲过）。正确做法：
    回调只做"记数 + 存最新值 + 打时间戳"（微秒级），
    另开一个 create_timer 周期打印报告。这是 ROS2 的标准状态机写法。

【电池话题名的坑】
  旧笔记写 /battery，但 ros2_web 真实配置用的是 /battery_state
  （sensor_msgs/BatteryState）。本节点两个都订阅：哪个有数据认哪个，
  兼容不同镜像。这就是"以真实仓库为准、别信旧文档"的具体落地。

【前置】车已上电、底盘/雷达节点已起（中控台或卖家 launch）。
【用法】python3 chassis_health_check.py
        python3 chassis_health_check.py 2.0        # 报告周期改成 2 秒
        ros2 run <你的包> chassis_health_check     # 放进 colcon 包后
【输出】每周期一行：[通] /odom  计数=123  距今=0.03s | [断] /scan  计数=0  从未收到
════════════════════════════════════════════════════════════════════
"""

import sys                                          # 读命令行参数（报告周期）
import rclpy                                        # ROS2 Python 总入口：init / spin / shutdown
from rclpy.node import Node                         # 节点基类：create_subscription / create_timer / get_logger
from rclpy.executors import ExternalShutdownException  # 上下文被关时 spin 抛的异常，接住避免 traceback

from nav_msgs.msg import Odometry                   # /odom 里程计消息类型
from sensor_msgs.msg import LaserScan               # /scan 雷达点云
from sensor_msgs.msg import BatteryState            # /battery_state 电池（新版话题名）
from std_msgs.msg import Float32                    # /battery 电池电压（旧版话题名，兼容用）

# ── 可配置项集中在这里（工程习惯：不散落魔法数字）──────────────
REPORT_PERIOD_SEC = 1.0                             # 默认每 1 秒打印一次体检报告
STALE_THRESHOLD_SEC = 1.0                           # 超过这么久没数据 = 判"陈旧"（假通）
TOPIC_ODOM = '/odom'                                # 里程计话题
TOPIC_SCAN = '/scan'                                # 雷达话题
TOPIC_BATT_NEW = '/battery_state'                   # 电池话题（新版，BatteryState）
TOPIC_BATT_OLD = '/battery'                         # 电池话题（旧版，Float32 电压）
QOS_DEPTH = 10                                      # 订阅队列深度：够用即可，别开太大吃内存


class ChassisHealthNode(Node):
    """底盘健康巡检：订阅 4 类话题，按周期输出"通/断/陈旧"报告。"""

    def __init__(self) -> None:
        super().__init__('chassis_health_check')     # 节点名，ros2 node list 里能看到
        # 每个话题三个状态：收过几条、最后一条的时间戳(秒)、是否收到过
        # 用字典统一存，省得为每个话题写三份成员变量
        self._stats = {
            TOPIC_ODOM: {'count': 0, 'last': 0.0},
            TOPIC_SCAN: {'count': 0, 'last': 0.0},
            TOPIC_BATT_NEW: {'count': 0, 'last': 0.0},
            TOPIC_BATT_OLD: {'count': 0, 'last': 0.0},
        }
        # 订阅四个话题：回调只做"记数 + 打时间戳"，不做耗时操作
        self._odom_sub = self.create_subscription(
            Odometry, TOPIC_ODOM, self.on_odom, QOS_DEPTH)
        self._scan_sub = self.create_subscription(
            LaserScan, TOPIC_SCAN, self.on_scan, QOS_DEPTH)
        # 电池两个名字都订阅：哪个先来数据就认哪个（兼容新旧镜像）
        self._batt_new_sub = self.create_subscription(
            BatteryState, TOPIC_BATT_NEW, self.on_battery_new, QOS_DEPTH)
        self._batt_old_sub = self.create_subscription(
            Float32, TOPIC_BATT_OLD, self.on_battery_old, QOS_DEPTH)
        # 周期报告定时器：★ 状态机写法，回调里绝不 sleep
        period = float(sys.argv[1]) if len(sys.argv) > 1 else REPORT_PERIOD_SEC
        self._timer = self.create_timer(period, self.report)

    def _now_sec(self) -> float:
        """返回 ROS 时钟的当前秒数（用 ROS 时钟，和仿真/真机时间基准一致）。"""
        return self.get_clock().now().nanoseconds / 1e9

    def _touch(self, topic: str) -> None:
        """收到一条消息：计数 +1，刷新最后时间戳。所有回调共用这一句。"""
        self._stats[topic]['count'] += 1
        self._stats[topic]['last'] = self._now_sec()

    # ── 四个回调：只记数、不判定、不打印（判定统一放 report）──────
    def on_odom(self, msg: Odometry) -> None:
        """里程计回调：只要收到就记一次；位置值本例不细看，Day12 讲原理。"""
        self._touch(TOPIC_ODOM)

    def on_scan(self, msg: LaserScan) -> None:
        """雷达回调：收到一帧点云记一次。ranges 长度可在 report 里扩展检查。"""
        self._touch(TOPIC_SCAN)

    def on_battery_new(self, msg: BatteryState) -> None:
        """新版电池回调：/battery_state 用 percentage 或 voltage 字段。"""
        self._touch(TOPIC_BATT_NEW)

    def on_battery_old(self, msg: Float32) -> None:
        """旧版电池回调：/battery 只有一个电压数（Float32.data）。"""
        self._touch(TOPIC_BATT_OLD)

    def _judge(self, topic: str) -> str:
        """
        判定单个话题状态，返回可直接打印的一行文本。
        三段判定：从未收到=断 / 距今超时=陈旧 / 否则=通。
        """
        st = self._stats[topic]
        count = st['count']
        if count == 0:
            return f'[断] {topic:<16} 计数=0      从未收到 → 查节点是否启动/话题名'
        age = self._now_sec() - st['last'] if st['last'] > 0 else float('inf')
        if age > STALE_THRESHOLD_SEC:
            return f'[陈旧] {topic:<14} 计数={count:<5} 距今={age:.2f}s → 数据卡住'
        return f'[通] {topic:<16} 计数={count:<5} 距今={age:.2f}s'

    def report(self) -> None:
        """定时体检：打印四个话题状态 + 电池二选一的汇总结论。"""
        lines = [self._judge(t) for t in (
            TOPIC_ODOM, TOPIC_SCAN, TOPIC_BATT_NEW, TOPIC_BATT_OLD)]
        self.get_logger().info('===== 底盘通信体检 =====\n' + '\n'.join(lines))
        # 电池两个话题只要有一个"通"就算电池链路 OK
        batt_ok = (self._stats[TOPIC_BATT_NEW]['count'] > 0 or
                   self._stats[TOPIC_BATT_OLD]['count'] > 0)
        odom_ok = self._stats[TOPIC_ODOM]['count'] > 0
        scan_ok = self._stats[TOPIC_SCAN]['count'] > 0
        if odom_ok and scan_ok:
            self.get_logger().info('结论：里程计 + 雷达都通，底盘通信合格，可进 Day10 建图')
        else:
            self.get_logger().warn(
                '结论：还有话题不通 → 回 Day9 笔记"今天踩坑"逐条查（架空轮子！）')
        if not batt_ok:
            self.get_logger().warn('提示：电池话题无数据——部分镜像不带电池话题，属正常')


def main(args=None) -> None:
    rclpy.init(args=args)                             # 初始化 ROS2 上下文
    node = ChassisHealthNode()
    try:
        rclpy.spin(node)                              # 事件循环：驱动定时器和四个订阅回调
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('用户中断或上下文关闭，退出体检')
    finally:
        node.destroy_node()                           # 固定收尾三件套
        if rclpy.ok():                                # 避免重复 shutdown 报错
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 为什么说"有数据"不等于"通"？ → 可能卡住；要看距今多久（新鲜度）
# Q2 回调里为什么不能 sleep？       → 会阻塞单线程执行器，其它话题全卡
# Q3 为什么电池订阅两个话题名？     → 新版 /battery_state、旧版 /battery，镜像不同
# ─────────────────────────────────────────────────────────────────────

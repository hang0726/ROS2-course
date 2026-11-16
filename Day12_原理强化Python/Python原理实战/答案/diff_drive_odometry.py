#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diff_drive_odometry.py —— 差速运动学 + 里程计积分（标准范本，逐行注释）

【这是第 1 课：/odom 到底怎么来的】
你 Day6 用 odom_subscriber.py 订阅过 /odom，但那是别人算好发给你的。
这一课你自己算一遍：订阅速度指令 /cmd_vel，用差速运动学推出整车运动，
再按时间积分出机器人位姿 (x, y, yaw)，发布到 /odom_custom。

对应视频：图传版 [1-15] 什么是里程计（29min）+ [1-16] 两轮差速运动学（18min）。
面试价值：能讲清「编码器 → 轮速 → 差速运动学 → 积分 → /odom」整条链路。

【核心原理】
两轮差速车，轮距 L，左右轮线速度 v_l / v_r：
  正运动学：v = (v_l + v_r)/2      ω = (v_r - v_l)/L
  逆运动学：v_l = v - ω·L/2        v_r = v + ω·L/2
航迹推演（每 dt 秒）：
  x   += v · cos(yaw) · dt
  y   += v · sin(yaw) · dt
  yaw += ω · dt

【为什么 /odom 会漂】
积分是累加，每步的小误差会累积——这就是里程计漂移。
所以才需要 AMCL（你 Day5 学的）用雷达地图校正它。串起来了。

【用法】
  source /opt/ros/humble/setup.bash
  python3 答案/diff_drive_odometry.py
  另开终端发速度：
  ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.1}}"

【对照练习】练习/my_diff_drive_odometry.py，按 # TODO(n) 编号填。
"""

import math                                          # cos/sin 用于把速度投影到世界坐标

import rclpy                                         # ROS2 Python 客户端库
from rclpy.node import Node                          # 节点基类

from geometry_msgs.msg import Twist                  # 订阅的速度指令类型（linear.x / angular.z）
from nav_msgs.msg import Odometry                    # 发布的里程计类型
from geometry_msgs.msg import Quaternion             # 位姿里的朝向用四元数

# ---- 可配置项提常量（标准范本做法，不散落魔法数字）----
WHEEL_BASE = 0.30                                    # 轮距 L（米）：左右轮中心距离，按你小车实际值改
CMD_TOPIC = '/cmd_vel'                               # 订阅的速度话题
ODOM_TOPIC = '/odom_custom'                          # ★ 自己算的里程计，单独话题，别撞 Nav2 的 /odom
TIMER_PERIOD = 0.1                                   # 积分周期 0.1 秒（10Hz，和 Day6 速度节点一致）
LOG_THROTTLE_SEC = 1.0                               # 日志限流，避免刷屏


class DiffDriveOdometry(Node):
    """订阅速度 → 差速运动学 → 积分出位姿 → 发布 /odom_custom 的节点。"""

    def __init__(self):
        super().__init__('diff_drive_odometry')       # ← 练习 TODO(1)：节点名

        # 状态量：机器人当前位姿和速度（对象存活期间一直累积）
        self.x = 0.0                                 # ← 练习 TODO(2)：世界坐标 x，初始 0
        self.y = 0.0                                 # ← 练习 TODO(3)：世界坐标 y，初始 0
        self.yaw = 0.0                               # ← 练习 TODO(4)：朝向角（弧度），初始 0
        self.v = 0.0                                 # ← 练习 TODO(5)：当前线速度 m/s
        self.w = 0.0                                 # ← 练习 TODO(6)：当前角速度 rad/s

        # 订阅速度指令：回调里只存速度，不做积分（积分统一放定时器，节奏稳定）
        self.cmd_sub = self.create_subscription(     # ← 练习 TODO(7)
            Twist, CMD_TOPIC, self.on_cmd, 10)       #    消息类型 / 话题名 / 回调 / 队列深度

        # 发布自己算的里程计
        self.odom_pub = self.create_publisher(       # ← 练习 TODO(8)
            Odometry, ODOM_TOPIC, 10)

        # 定时器：每 TIMER_PERIOD 秒积分一次（★ 回调里禁止 time.sleep，用定时器，Day6 的坑）
        self.timer = self.create_timer(              # ← 练习 TODO(9)
            TIMER_PERIOD, self.on_timer)

        self.get_logger().info('diff_drive_odometry ready, integrating to /odom_custom')

    # ---- 差速运动学：正运动学（左右轮速 → 整车 v/ω）----
    def forward_kinematics(self, v_l, v_r):
        """左右轮线速度 → 整车线速度 v 和角速度 w。"""
        v = (v_l + v_r) / 2.0                        # ← 练习 TODO(10)：两轮平均 = 整车前进速度
        w = (v_r - v_l) / WHEEL_BASE                 # ← 练习 TODO(11)：轮速差 / 轮距 = 角速度
        return v, w                                  # ← 练习 TODO(12)：返回两个值

    # ---- 差速运动学：逆运动学（整车 v/ω → 左右轮速）----
    def inverse_kinematics(self, v, w):
        """整车线速度/角速度 → 左右轮该转多快。"""
        v_l = v - w * WHEEL_BASE / 2.0               # ← 练习 TODO(13)：左轮 = v 减去转向分量
        v_r = v + w * WHEEL_BASE / 2.0               # ← 练习 TODO(14)：右轮 = v 加上转向分量
        return v_l, v_r                              # ← 练习 TODO(15)

    def on_cmd(self, msg):
        """收到速度指令，只更新状态，不在这里积分。"""
        self.v = msg.linear.x                        # ← 练习 TODO(16)：前进速度取 linear.x
        self.w = msg.angular.z                       # ← 练习 TODO(17)：转向速度取 angular.z

    def on_timer(self):
        """每个积分周期：按当前速度推进位姿，并发布里程计。"""
        dt = TIMER_PERIOD                            # ← 练习 TODO(18)：积分步长

        # 航迹推演：先算方向投影再累加（★ 顺序：先更新 x/y 用旧 yaw，再更新 yaw）
        self.x += self.v * math.cos(self.yaw) * dt  # ← 练习 TODO(19)：x 增量 = v·cos(yaw)·dt
        self.y += self.v * math.sin(self.yaw) * dt  # ← 练习 TODO(20)：y 增量 = v·sin(yaw)·dt
        self.yaw += self.w * dt                      # ← 练习 TODO(21)：yaw 增量 = w·dt

        self.publish_odom()                          # ← 练习 TODO(22)：发布算好的位姿

        # 限流打印：能直观看到「发速度 → 位姿变化」
        self.get_logger().info(                      # ← 练习 TODO(23)
            f'位姿 x={self.x:.3f} y={self.y:.3f} yaw={self.yaw:.3f} | '
            f'v={self.v:.3f} w={self.w:.3f}',
            throttle_duration_sec=LOG_THROTTLE_SEC,
        )

    def publish_odom(self):
        """把当前位姿打包成 Odometry 消息发出去。"""
        msg = Odometry()                             # ← 练习 TODO(24)：造空消息

        # 头部：时间戳 + 坐标系（世界系 odom → 车体系 base_link）
        msg.header.stamp = self.get_clock().now().to_msg()   # ← 练习 TODO(25)：时间戳
        msg.header.frame_id = 'odom'                 # ← 练习 TODO(26)：父坐标系
        msg.child_frame_id = 'base_link'             # ← 练习 TODO(27)：子坐标系

        # 位姿：位置 + 朝向（四元数，由 yaw 换算）
        msg.pose.pose.position.x = self.x            # ← 练习 TODO(28)
        msg.pose.pose.position.y = self.y            # ← 练习 TODO(29)
        q = Quaternion()                             # ← 练习 TODO(30)：造四元数
        q.z = math.sin(self.yaw / 2.0)               # ← 练习 TODO(31)：绕 z 轴旋转，q.z = sin(yaw/2)
        q.w = math.cos(self.yaw / 2.0)               # ← 练习 TODO(32)：q.w = cos(yaw/2)（Day6 的公式）
        msg.pose.pose.orientation = q                # ← 练习 TODO(33)

        # 速度：线速度取 x，角速度取 z（差速车只在这两个方向动）
        msg.twist.twist.linear.x = self.v            # ← 练习 TODO(34)
        msg.twist.twist.angular.z = self.w           # ← 练习 TODO(35)

        self.odom_pub.publish(msg)                   # ← 练习 TODO(36)：发出去


def main():
    rclpy.init()                                     # ← 练习 TODO(37)：初始化 ROS2
    node = DiffDriveOdometry()                       # ← 练习 TODO(38)：建节点
    try:
        rclpy.spin(node)                             # ← 练习 TODO(39)：事件循环（不是"启动 ROS2"）
    finally:
        node.destroy_node()                          # ← 练习 TODO(40)
        if rclpy.ok():
            rclpy.shutdown()                         # ← 练习 TODO(41)


if __name__ == '__main__':
    main()

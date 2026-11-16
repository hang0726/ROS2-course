#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
my_diff_drive_odometry.py —— 差速运动学 + 里程计积分（全注释挖空模板）

【做法】按 # TODO(n) 编号，把下面注释掉的代码逐行「解注释 + 填写」，
       对照 答案/diff_drive_odometry.py 的同名编号（讲解全在答案注释里，不给公式/数值/字段名线索）。

【现状】本文件能 import（框架 + 函数体里的中文 docstring 撑住语法，不留任何占位语句），
       但运行时什么都不做——代码行都被注释了。

【安全】里程计是「自己算的」，话题名别用 /odom（会和 Nav2 撞）——这个坑留给你自己发现。
       TODO(1)~TODO(41) 对应答案里同样的编号。
"""

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion

# 可配置项：常量名和值自己定（轮距按你小车实际值）
# ...


class MyDiffDriveOdometry(Node):
    """订阅速度 → 差速运动学 → 积分出位姿 → 发布里程计。"""

    def __init__(self):
        """TODO(1)：节点名。TODO(2)~TODO(6)：5 个状态量。TODO(7)~TODO(9)：订阅/发布/定时器。"""
        # TODO(1)：super().__init__(节点名)
        # TODO(2)：self.x = ...
        # TODO(3)：self.y = ...
        # TODO(4)：self.yaw = ...
        # TODO(5)：self.v = ...
        # TODO(6)：self.w = ...
        # TODO(7)：create_subscription(Twist, 话题, 回调, 队列深度)
        # TODO(8)：create_publisher(Odometry, 话题, 队列深度)
        # TODO(9)：create_timer(周期, 回调)

    def forward_kinematics(self, v_l, v_r):
        """TODO(10)~TODO(12)：左右轮速 → 整车 v/w，返回两个值。"""
        # TODO(10)：v = 两轮的某种平均
        # TODO(11)：w = 轮速差 / 轮距 L
        # TODO(12)：return v, w

    def inverse_kinematics(self, v, w):
        """TODO(13)~TODO(15)：整车 v/w → 左右轮速，返回两个值。"""
        # TODO(13)：v_l = ...
        # TODO(14)：v_r = ...
        # TODO(15)：return v_l, v_r

    def on_cmd(self, msg):
        """TODO(16)~TODO(17)：从速度消息里取前进/转向两个分量存进状态。"""
        # TODO(16)：self.v = msg.???.x
        # TODO(17)：self.w = msg.???.z

    def on_timer(self):
        """TODO(18)~TODO(23)：积分步长 → 更新 x/y/yaw → 发布 → 限流打印。
        ★ 顺序有讲究：更新 x/y 时用旧的 yaw，之后再更新 yaw。
        ★ 回调里禁止 time.sleep()。"""
        # TODO(18)：dt = 积分步长
        # TODO(19)：self.x += ...
        # TODO(20)：self.y += ...
        # TODO(21)：self.yaw += ...
        # TODO(22)：发布位姿
        # TODO(23)：get_logger().info(限流打印)

    def publish_odom(self):
        """TODO(24)~TODO(36)：打包 Odometry——头部坐标系、位姿(四元数)、速度。
        四元数换算公式回去看 Day6 send_nav_goal.py 的 _yaw_to_quat。"""
        # TODO(24)：msg = Odometry()
        # TODO(25)：msg.header.stamp = ...
        # TODO(26)：msg.header.frame_id = ...
        # TODO(27)：msg.child_frame_id = ...
        # TODO(28)：msg.pose.pose.position.x = ...
        # TODO(29)：msg.pose.pose.position.y = ...
        # TODO(30)：q = Quaternion()
        # TODO(31)：q.z = ...
        # TODO(32)：q.w = ...
        # TODO(33)：msg.pose.pose.orientation = ...
        # TODO(34)：msg.twist.twist.linear.x = ...
        # TODO(35)：msg.twist.twist.angular.z = ...
        # TODO(36)：self.odom_pub.publish(msg)


def main():
    """TODO(37)~TODO(41)：init → 建节点 → spin → 收尾销毁关闭。"""
    # TODO(37)：rclpy.init()
    # TODO(38)：node = MyDiffDriveOdometry()
    # TODO(39)：try: rclpy.spin(node) / finally: 收尾
    # TODO(40)：node.destroy_node()
    # TODO(41)：if rclpy.ok(): rclpy.shutdown()


if __name__ == '__main__':
    main()

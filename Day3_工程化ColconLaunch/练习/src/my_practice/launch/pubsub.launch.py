#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day3 练习 · launch 文件（请你自己敲！）
===================================
目标：用 Node() 把 talker 和 listener 一起拉起，一条命令起两个节点。
用到：
  - from launch import LaunchDescription
  - from launch_ros.actions import Node
  - Node(package='my_practice', executable='talker', name='talker', output='screen')
  - Node(package='my_practice', executable='listener', name='listener', output='screen')
  - return LaunchDescription([talker_node, listener_node])
用法：在 练习/ 目录 colcon build 后 → ros2 launch my_practice pubsub.launch.py
卡住时对照答案：src/my_robot_course/launch/pubsub.launch.py
"""
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    talker_node = Node(
        package = 'my_practice',
        executable = 'talker',#
        name = 'talker',
        output='screen'
    )
    listener_node=Node(
        package = 'my_practice',
        executable = 'listener',
        name = 'listener',
        output = 'screen',
    )

    return LaunchDescription([talker_node,listener_node])


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Day3 模板 · launch 文件（后缀必须是 .launch.py）
# 作用：一条命令同时启动 talker + listener，不用开两个终端。
# 用法：ros2 launch my_robot_course pubsub.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """launch 文件入口：返回一个 LaunchDescription（里面是要起的节点列表）。"""
    talker_node = Node(
        package='my_robot_course',        # 包名（package.xml 的 <name>）
        executable='talker',              # setup.py 里注册的入口名
        name='talker',                    # 运行时的节点名（可和 executable 不同）
        output='screen',                  # 把节点日志打到终端
    )
    listener_node = Node(
        package='my_robot_course',
        executable='listener',
        name='listener',
        output='screen',
    )
    # 返回描述：launch 会按顺序把这两个节点都拉起来
    return LaunchDescription([talker_node, listener_node])

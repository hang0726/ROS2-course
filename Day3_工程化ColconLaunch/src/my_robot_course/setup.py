#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Day3 模板 · ROS2 ament_python 包的 setup.py
# 作用：告诉 colcon 怎么装这个包，并把"节点/launch"注册成命令行入口。

from setuptools import setup

package_name = 'my_robot_course'                      # ★★★ 必须和 package.xml 的 <name> 一致


setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],                          # Python 包目录（和包同名）
    data_files=[
        # 让 colcon 认识这是 ROS2 包
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 注册 launch 目录（ros2 launch 能找到里面的 *.launch.py）
        ('share/' + package_name + '/launch', ['launch/pubsub.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MicckeY',
    maintainer_email='you@example.com',
    description='我的 ROS2 课程练习包',
    license='Apache-2.0',
    # ★★★ 节点入口：命令行名字 = 模块:函数（main 函数）
    entry_points={
        'console_scripts': [
            'talker = my_robot_course.talker:main',
            'listener = my_robot_course.listener:main',
            'add_server = my_robot_course.service_param:main_server',
            'add_client = my_robot_course.service_param:main_client',
            'param_node = my_robot_course.service_param:main_param',
        ],
    },
)

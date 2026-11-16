#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Day3 练习包 · setup.py（package_name 已填好、节点入口已注册）
# 你只需在各 .py 里把节点代码敲出来，入口名要和这里注册的对应：
#   talker / listener / add_server / add_client / param_node

from setuptools import setup

package_name = 'my_practice'


setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/pubsub.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MicckeY',
    maintainer_email='you@example.com',
    description='Day3 练习包',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'talker = my_practice.talker:main',
            'listener = my_practice.listener:main',
            'add_server = my_practice.service_param:main_server',
            'add_client = my_practice.service_param:main_client',
            'param_node = my_practice.service_param:main_param',
        ],
    },
)

cmake_minimum_required(VERSION 3.8)
project(cpp_pubsub)

# 找 C++ 编译依赖（对应 Python 里 import 的那些库）
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# ---- 编译 talker 可执行文件 ----
add_executable(talker src/talker.cpp)
ament_target_dependencies(talker rclcpp std_msgs)

# ---- 编译 listener 可执行文件 ----
add_executable(listener src/listener.cpp)
ament_target_dependencies(listener rclcpp std_msgs)

# 安装到 install/cpp_pubsub/lib/cpp_pubsub/，这样 ros2 run 才找得到
install(TARGETS
  talker
  listener
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

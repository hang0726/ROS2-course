# C++ 话题通讯实战（对应进阶版视频 [2-3]）

> 🎯 **这份材料补什么**：你 Day2 学的是 **Python** 写 publisher/subscriber，
> 但求职岗位硬要求「熟悉 C++」，进阶版视频最后一集正好是 **C++ 话题通讯实战**。
> 这里给你一套和 Day2 一一对应的 C++ 版本：答案（逐行注释）+ 全注释挖空练习。
> 做通之后 `colcon build` 能过 → 这就是你 GitHub 作品集里缺的 **C++ 独立实现证据**。

---

## 一、和 Day2 Python 版的对照（原理一样，写法不同）

| 概念 | Day2 Python | 这里 C++ |
|---|---|---|
| 引入库 | `import rclpy` | `#include "rclcpp/rclcpp.hpp"` |
| 建节点 | `Node('talker')` | `rclcpp::Node::make_shared("talker")`（返回共享指针） |
| 建发布者 | `create_publisher(String, 'topic', 10)` | `create_publisher<std_msgs::msg::String>("topic", 10)` |
| 定时发布 | `create_timer(1.0, callback)` | `create_wall_timer(1s, callback)` |
| 建订阅者 | `create_subscription(..., callback)` | `create_subscription<...>(..., callback)` |
| 日志 | `self.get_logger().info()` | `RCLCPP_INFO(this->get_logger(), ...)` |
| 转圈 | `rclpy.spin(node)` | `rclcpp::spin(node)` |
| 初始化 | `rclpy.init()` | `rclcpp::init(argc, argv)` |

> 🔑 C++ 多出来的三件事：① `#include` 头文件 ② **智能指针** `SharedPtr` ③ 编译要先 `colcon build`。
> Python 不用编译，C++ 要——这正是面试官想看的「工程能力」。

---

## 二、目录结构

```
C++话题通讯/
├── README.md              # 本文件
├── CMakeLists.txt         # 编译配置（C++ 必需，Python 没有）
├── package.xml            # 包描述（C++ 必需）
├── 答案/
│   ├── talker.cpp         # 发布者标准范本（逐行注释）
│   └── listener.cpp       # 订阅者标准范本（逐行注释）
└── 练习/
    ├── my_talker.cpp      # 全注释挖空模板（不给答案）
    └── my_listener.cpp    # 全注释挖空模板
```

> 答案和练习**二选一**：把要用的那两个 `.cpp` 复制到 `src/` 目录再编译（见下）。
> 不能同时放——两个文件都有 `main()`，会编译冲突。

---

## 三、编译运行（这是和 Python 最大的不同）

```bash
# 0. 先进 ROS2 环境（忘 source 是头号坑）
source /opt/ros/humble/setup.bash

# 1. 建工作空间（对应 Day3 学的 Colcon）
mkdir -p ~/cpp_ws/src
cd ~/cpp_ws/src

# 2. 把本目录拷成一个 ROS2 包
cp -r "<本目录>" ./cpp_pubsub
cd cpp_pubsub
mkdir -p src
cp 答案/talker.cpp 答案/listener.cpp src/     # 或改成 练习/my_*.cpp 并改 CMakeLists 里的文件名

# 3. 编译（C++ 独有步骤）
cd ~/cpp_ws
colcon build --packages-select cpp_pubsub
source install/setup.bash                     # ⚠️ 每次新终端都要 source

# 4. 跑：开两个终端，各 source 一次
ros2 run cpp_pubsub talker                    # 终端 A：每 0.5 秒发一句话
ros2 run cpp_pubsub listener                  # 终端 B：收到就打印
```

✅ 通关标准：终端 A 打印 `publishing: 'hello world 0'...`，终端 B 打印 `I heard: [hello world 0]`。

---

## 四、练习怎么做

1. 先读 `答案/talker.cpp` 和 `答案/listener.cpp` 的注释——讲解全在代码里，不单独出文档。
2. 打开 `练习/my_*.cpp`：除了 `#include` 和 class / 函数框架，**其余代码行全被注释掉**。
3. 按 `# TODO(n)` 编号，把注释掉的代码一行行「解注释 + 填写」，对照答案同名位置。
4. 编译不过就 `colcon build --event-handlers console_direct+` 看报错。

> 🔴 红线：`练习/` 里不给具体值、不给 API 细节——这是留给你自己查的。
> 但**语法框架保留**（`#include`、class、`main` 的空 `{}`），所以文件本身能编译，只是什么都不做。

---

## 五、面试怎么讲这段

不要说「我会用 C++ 写了个 hello world」，要说：
> 「我用 rclcpp 独立实现了 ROS2 的发布订阅节点，用 `SharedPtr` 管理节点生命周期、
> `create_wall_timer` 做周期任务，并通过 `colcon build` 编译成可执行节点，
> 和之前 Python 版做了逐一对照，理解了两套 API 的映射关系。」

---

## 自查 3 问
1. C++ 版比 Python 版多哪三个必须掌握的东西？（头文件 / 智能指针 / 编译）
2. 为什么答案和练习不能同时放进 `src/`？（两个 `main()` 冲突）
3. 每次新开终端跑节点前必须先做什么？（`source install/setup.bash`）

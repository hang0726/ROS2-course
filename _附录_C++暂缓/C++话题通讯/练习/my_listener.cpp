// my_listener.cpp —— C++ 订阅者练习（全注释挖空模板）
//
// 做法：按 # TODO(n) 编号，把下面注释掉的代码逐行「解注释 + 填写」，
//       对照 答案/listener.cpp 的同名位置（讲解全在答案的注释里）。
//       不给具体值、不给 API 细节——这些要你自己查。
//
// 现状：本文件能编译（框架 + 头文件都在），但运行时什么都不做——代码行都被注释了。
//       TODO(1)~TODO(10) 对应答案里同样的编号。

// ---- 头文件：框架给你保留（对应 Python 的 import，这一层不挖空）----
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// 定义节点类，继承 ROS2 C++ 的 Node 基类
class MyListener : public rclcpp::Node
{
public:
  // 构造函数：// ← 练习 TODO(1)：给基类传节点名
  MyListener()  // : Node("...")   ← TODO(1)
  {
    // ← 练习 TODO(2)：创建订阅者（消息类型 / 话题名 / 队列深度），赋给 subscription_
    // subscription_ = ...
    // ← 练习 TODO(3)：想清楚回调函数怎么绑定，_1 代表什么

    // ← 练习 TODO(4)：打印一条启动日志
  }

private:
  // 订阅回调：// ← 练习 TODO(5)：参数类型（为什么要避免拷贝？）
  void topic_callback(/* TODO(5)：参数 */) const
  {
    // TODO(6)：打印收到的消息内容
  }

  // ← 练习 TODO(7)：成员变量（订阅者指针），想清楚类型
};

// main：// ← 练习 TODO(8)：初始化 / TODO(9)：spin / TODO(10)：关闭
int main(int argc, char ** argv)
{
  // TODO(8)：初始化 ROS2
  // TODO(9)：创建节点并 spin
  // TODO(10)：退出前关闭 ROS2
  return 0;
}

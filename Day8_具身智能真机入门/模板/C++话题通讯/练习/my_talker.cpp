// my_talker.cpp —— C++ 发布者练习（全注释挖空模板）
//
// 做法：按 # TODO(n) 编号，把下面注释掉的代码逐行「解注释 + 填写」，
//       对照 答案/talker.cpp 的同名位置（讲解全在答案的注释里）。
//       不给具体值、不给 API 细节——这些要你自己查。
//
// 现状：本文件能编译（框架 + 头文件都在），但运行时什么都不做——代码行都被注释了。
//       TODO(1)~TODO(15) 对应答案里同样的编号。

// ---- 头文件：框架给你保留（对应 Python 的 import，这一层不挖空）----
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>
#include <string>

using namespace std::chrono_literals;   // 让 500ms 这种时间字面量能直接写

// 定义节点类，继承 ROS2 C++ 的 Node 基类
class MyTalker : public rclcpp::Node
{
public:
  // 构造函数：// ← 练习 TODO(1)：给基类传节点名
  MyTalker()  // : Node("...")   ← TODO(1)
  {
    // ← 练习 TODO(2)：创建发布者（消息类型 / 话题名 / 队列深度）
    // publisher_ = ...

    // ← 练习 TODO(3)：创建定时任务，周期触发 timer_callback
    // timer_ = ...

    // ← 练习 TODO(4)：打印一条启动日志（RCLCPP_INFO）
  }

private:
  // 定时器回调：// ← 练习 TODO(5)：造消息 / TODO(6)：赋值 / TODO(7)：发布 / TODO(8)：打印 / TODO(9)：计数
  void timer_callback()
  {
    // TODO(5)：造一个空消息对象
    // TODO(6)：给消息内容赋值（字符串 + 计数）
    // TODO(7)：发布消息（注意发布者是指针）
    // TODO(8)：打印发布内容
    // TODO(9)：计数器加一
  }

  // ← 练习 TODO(10)：成员变量——发布者指针，想清楚类型
  // ← 练习 TODO(11)：成员变量——定时器指针，想清楚类型
  // ← 练习 TODO(12)：成员变量——计数器，想清楚类型
};

// main：// ← 练习 TODO(13)：初始化 / TODO(14)：spin / TODO(15)：关闭
int main(int argc, char ** argv)
{
  // TODO(13)：初始化 ROS2
  // TODO(14)：创建节点并 spin
  // TODO(15)：退出前关闭 ROS2
  return 0;
}

// talker.cpp —— ROS2 C++ 发布者节点（标准范本，逐行注释）
//
// 用法（编译后）：
//   source ~/cpp_ws/install/setup.bash
//   ros2 run cpp_pubsub talker
// 效果：每 0.5 秒往话题 /chatter 发一条字符串 "hello world N"。
//
// 对应练习：练习/my_talker.cpp，按 # TODO(n) 编号逐行对照本文件同名位置。
// 这是你求职作品集里的「C++ 独立实现证据」之一。

// ---- 头文件：C++ 比 Python 多出来的第一件事 ----
#include "rclcpp/rclcpp.hpp"                  // ROS2 C++ 客户端库：Node / spin / 日志都在这
#include "std_msgs/msg/string.hpp"            // 要发的消息类型 String（对应 Python 的 std_msgs.msg.String）
#include <chrono>                             // C++ 时间库：定时周期 500ms 要用
#include <string>                             // std::string 字符串

using namespace std::chrono_literals;         // 让 "500ms" 这种字面量能直接写（C++ 时间单位语法）

// 定义节点类，继承 rclcpp::Node（对应 Python 的 class Talker(Node)）
class Talker : public rclcpp::Node
{
public:
  // 构造函数：节点一创建就在这里把「发布者 + 定时器」准备好
  Talker() : Node("talker")                   // ← 练习 TODO(1)：节点名传 "talker" 给基类
  {
    // 创建发布者：模板参数 <消息类型>，参数：话题名 + 队列深度
    publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);  // ← 练习 TODO(2)

    // 创建定时器：每 500 毫秒调一次 timer_callback（对应 Python create_timer）
    timer_ = this->create_wall_timer(
      500ms, std::bind(&Talker::timer_callback, this));   // ← 练习 TODO(3)

    RCLCPP_INFO(this->get_logger(), "talker node started, publishing to /chatter");  // ← 练习 TODO(4)
  }

private:
  // 定时器回调：每次触发就发一条消息
  void timer_callback()
  {
    auto msg = std_msgs::msg::String();       // ← 练习 TODO(5)：造一个空消息对象
    msg.data = "hello world " + std::to_string(count_);  // ← 练习 TODO(6)：填内容 = 字符串 + 计数

    publisher_->publish(msg);                 // ← 练习 TODO(7)：发布（注意是 -> 不是 .，因为是指针）
    RCLCPP_INFO(this->get_logger(), "publishing: '%s'", msg.data.c_str());  // ← 练习 TODO(8)

    count_ += 1;                              // ← 练习 TODO(9)：计数加一
  }

  // 成员变量：C++ 里发布者/定时器都用「智能指针」持有（Python 不用操心这个）
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;   // ← 练习 TODO(10)
  rclcpp::TimerBase::SharedPtr timer_;                              // ← 练习 TODO(11)
  size_t count_ = 0;                                                // ← 练习 TODO(12)：发了几条
};

// main：程序入口（C++ 独有，Python 用 if __name__ == '__main__'）
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);                   // ← 练习 TODO(13)：初始化 ROS2 C++ 环境
  rclcpp::spin(std::make_shared<Talker>());   // ← 练习 TODO(14)：创建节点并进入事件循环（对应 rclpy.spin）
  rclcpp::shutdown();                         // ← 练习 TODO(15)：退出前关掉 ROS2
  return 0;
}

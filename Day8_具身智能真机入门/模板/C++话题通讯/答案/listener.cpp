// listener.cpp —— ROS2 C++ 订阅者节点（标准范本，逐行注释）
//
// 用法（编译后，另开一个终端）：
//   source ~/cpp_ws/install/setup.bash
//   ros2 run cpp_pubsub listener
// 效果：收到 /chatter 上的字符串就打印 "I heard: [...]"。
//
// 对应练习：练习/my_listener.cpp，按 # TODO(n) 编号逐行对照本文件同名位置。

// ---- 头文件 ----
#include "rclcpp/rclcpp.hpp"                  // ROS2 C++ 客户端库
#include "std_msgs/msg/string.hpp"            // 订阅的消息类型 String

// 定义节点类，继承 rclcpp::Node
class Listener : public rclcpp::Node
{
public:
  // 构造函数：节点一创建就把「订阅者」准备好
  Listener() : Node("listener")               // ← 练习 TODO(1)：节点名传 "listener" 给基类
  {
    // 创建订阅者：模板参数 <消息类型>，参数：话题名 + 队列深度 + 回调函数
    subscription_ = this->create_subscription<std_msgs::msg::String>(  // ← 练习 TODO(2)
      "chatter", 10,
      std::bind(&Listener::topic_callback, this, std::placeholders::_1));  // ← 练习 TODO(3)：绑定回调，_1 是收到的消息

    RCLCPP_INFO(this->get_logger(), "listener node started, subscribing /chatter");  // ← 练习 TODO(4)
  }

private:
  // 订阅回调：每收到一条消息就调一次
  // 参数用 const 引用（SharedPtr 指向的常量消息），避免拷贝
  void topic_callback(const std_msgs::msg::String::SharedPtr msg) const  // ← 练习 TODO(5)
  {
    RCLCPP_INFO(this->get_logger(), "I heard: [%s]", msg->data.c_str());  // ← 练习 TODO(6)：打印 msg->data
  }

  // 成员变量：订阅者也用智能指针持有
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;  // ← 练习 TODO(7)
};

// main：程序入口
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);                   // ← 练习 TODO(8)：初始化
  rclcpp::spin(std::make_shared<Listener>()); // ← 练习 TODO(9)：创建节点进事件循环
  rclcpp::shutdown();                         // ← 练习 TODO(10)：关闭
  return 0;
}

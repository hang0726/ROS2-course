# 检测结果接入 ROS2（Day12 · 衔接抓取）

> 🎯 讲清怎么把 AscendCL C++ 推理出的检测结果，发布成 ROS2 话题，供 Day12 抓取节点和 Day13 系统用。

---

## 一、为什么要用标准消息

检测结果是"类别 + 框坐标 + 置信度"。ROS2 有标准消息 `vision_msgs/Detection2DArray` 专门表达这个：

```
Detection2DArray
  └─ detections[]
       ├─ results[]: hypothesis.class_id / score
       └─ bbox: center.x / center.y / size_x / size_y
```
✅ 用标准消息的好处：RViz 能显示、其它节点能直接订阅、面试时说得出消息名。

---

## 二、两种接入方式

| 方式 | 做法 | 适合 |
|---|---|---|
| **A. C++ 节点直接发** | 在 AscendCL 推理程序里 link rclcpp，发布 Detection2DArray | 高性能，一步到位（推荐） |
| **B. 进程间通信** | C++ 推理程序把结果写串口/共享内存，另一个 Python 节点读出来转发 | 改动小，解耦 |

方式 A 的骨架：
```cpp
#include "rclcpp/rclcpp.hpp"
#include "vision_msgs/msg/detection2_d_array.hpp"
// 推理出结果后：
auto msg = vision_msgs::msg::Detection2DArray();
// 填充 detections[] ...
publisher->publish(msg);
```

---

## 三、从检测框到抓取点（和 Day11 手眼串起来）

```
bbox.center (u, v)     →  像素坐标（框中心）
+ 深度图在 (u,v) 的值 d →  相机坐标 (xc,yc,zc) = 反投影(u,v,d, 相机内参)
+ 手眼变换 X (Day11)   →  机械臂基座坐标
→ MoveIt 抓取
```
🔴 深度单位：有的相机给 mm，有的给 m——搞错抓取位置差 1000 倍。

【待材料：3D 相机的内参、深度单位、厂商取流接口】

---

## 四、自查 3 问
1. 检测结果用什么 ROS2 标准消息？（vision_msgs/Detection2DArray）
2. 两种接入 C++ 推理和 ROS2 的方式？（C++ 节点直接发 / 进程间通信转发）
3. 从检测框到抓取坐标还要哪些量？（深度 d + 相机内参 + 手眼变换 X）

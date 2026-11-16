#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day6 · 第 3 课 / 标准参考答案：发速度指令（Twist → /cmd_vel）
════════════════════════════════════════════════════════════════════
★ 这份文件是【对照基准】，练习在 练习/my_velocity_commander.py（9 个 TODO）。
  答案里每个关键行都标了 `# ← 练习 TODO(n)`，编号与练习里的 # TODO(n)
  一一对应，填完可以按编号逐条核对。

【本文件遵守的标准写法（三份答案一致，可照抄这个习惯）】
  ① 可配置项一律提成模块常量，代码里不散落魔法数字；
  ② 方法名 / 参数 / 顺序与练习骨架完全一致（`__init__(self)` 不带参数）；
  ③ 公开方法带类型注解与 docstring；
  ④ main() 统一收尾：stop → destroy_node → 判断 rclpy.ok() → shutdown，不用 pass；
  ⑤ 日志纯文本；★ `stop()` 做成幂等，重复调用无害，收尾更安全。
  ⚠️ 练习里直接写数字就是对的；答案用常量是工程习惯，不是硬要求。

【Twist 六个分量，差速车只用两个】
  linear.x    前进/后退 m/s            ✅ 用
  linear.y    横移 m/s                 ❌ 差速车没有
  linear.z    升降 m/s                 ❌
  angular.x   翻滚                     ❌
  angular.y   俯仰                     ❌
  angular.z   原地转向 rad/s，正=左转  ✅ 用
  Twist() 默认六个分量【全 0】→ 所以「发一条空 Twist」就等于停车。

【★ 回调里禁止 time.sleep()】
  单线程 executor 被阻塞时，所有回调（订阅 / 定时器 / action 反馈）一起停摆，
  节点看起来像死了。要按时间切动作，就用定时器算 t = now - start，
  这是最简单的【状态机】。create_timer(0.1) = 10Hz，底盘常用 10~50Hz；
  太慢车一顿一顿，太快纯浪费带宽。

【★ 安全红线】
  ① stop() 里的全 0 速度永远别删。正常结束和 Ctrl+C 都会走 finally 补发一次；
     真机上漏了就是车一直往前冲。本答案把 stop() 做成幂等：重复调、上下文
     已关闭时都安全。
  ② Nav2 的 controller_server 在导航进行中也发 /cmd_vel，两个发布者抢同一
     话题 → 车抽风。等导航结束再跑本节点；Nav2 空闲时是安全的。

【用法】python3 velocity_commander.py
════════════════════════════════════════════════════════════════════
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist               # 速度指令消息（线速度+角速度）

# ── 可配置项集中在这里（练习里的空位直接写对应值即可）──────────────
CMD_VEL_TOPIC = '/cmd_vel'                       # ← 练习 TODO(1)：话题名
QOS_DEPTH = 10
TIMER_PERIOD_SEC = 0.1                           # ← 练习 TODO(2)：定时器周期（10Hz）
FORWARD_END_SEC = 2.0                            # ← 练习 TODO(6)：第一阶段阈值
TURN_END_SEC = 4.0                           # ← 练习 TODO(6)：第二阶段阈值
FORWARD_SPEED = 0.2                              # ← 练习 TODO(7)：前进速度 m/s
TURN_SPEED = 0.5                                 # ← 练习 TODO(7)：左转角速度 rad/s


class VelocityCommander(Node):
    """速度指令发布者：定时下发 Twist，做出「前进→转向→停车」的简单动作。"""

    def __init__(self) -> None:
        super().__init__('velocity_commander')    # 节点名
        # 创建发布者：消息类型 / 话题名 / QoS 队列深度。底盘订阅 /cmd_vel
        self.pub = self.create_publisher(
            Twist, CMD_VEL_TOPIC, QOS_DEPTH)                             # ← 练习 TODO(1)
        # 定时器每 0.1 秒（10Hz）触发一次 loop —— 不是 while + sleep
        self.timer = self.create_timer(TIMER_PERIOD_SEC, self.loop)     # ← 练习 TODO(2)
        self.start = time.time()                  # ← 练习 TODO(3)：记录起点时间
        self._stopped = False                    # 幂等标志，防止重复停车
        self.get_logger().info(f'开始发速度指令到话题: {CMD_VEL_TOPIC}')

    def _cmd(self, vx: float, wz: float) -> None:
        """构造并发布一条 Twist：vx=前进速度, wz=转向角速度。"""
        msg = Twist()                             # ★ 六个分量默认全 0
        msg.linear.x = vx                         # ← 练习 TODO(4)：前进速度（米/秒）
        msg.angular.z = wz                        # ← 练习 TODO(5)：转向角速度（弧度/秒）
        self.pub.publish(msg)

    def stop(self) -> None:
        """★ 安全红线：发一条全 0 速度并停掉定时器。

        幂等：重复调用无害；上下文已被 shutdown 时 publish 会抛错，直接跳过。
        这样 main() 的 finally 里就能无条件写一行 node.stop()，与练习骨架对齐。
        """
        if self._stopped or not rclpy.ok():
            return
        self._stopped = True
        self.timer.cancel()
        self._cmd(0.0, 0.0)                      # ★ 停车，别让车一直冲
        self.get_logger().info('已发全 0 速度，停车')

    def loop(self) -> None:
        """定时回调：按时间切三个阶段（★ 这里绝不能 time.sleep）。"""
        t = time.time() - self.start
        if t < FORWARD_END_SEC:                                          # ← 练习 TODO(6)
            self._cmd(vx=FORWARD_SPEED, wz=0.0) # 阶段1：前进 2 秒      ← 练习 TODO(7)
        elif t < TURN_END_SEC:                                           # ← 练习 TODO(6)
            self._cmd(vx=0.0, wz=TURN_SPEED)    # 阶段2：原地左转 2 秒  ← 练习 TODO(7)
        else:
            self.stop()                          # 阶段3：停车
            self.get_logger().info('动作完成（前进→左转→停车）')
            rclpy.shutdown()                     # 让 main 里的 spin 退出


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VelocityCommander()
    try:
        # ★ spin() 让定时器跑起来；回调里调用 shutdown() 后它会退出
        rclpy.spin(node)                                                 # ← 练习 TODO(8)
    except (KeyboardInterrupt, ExternalShutdownException):
        # ★ 标准写法：不用 pass，明确记一句退出原因
        node.get_logger().info('用户中断或上下文关闭，退出')
    finally:
        # ★ 安全红线：Ctrl+C 时上下文还活着，必须补一次停车（练习 TODO(9)）
        node.stop()                                                      # ← 练习 TODO(9)
        # 固定收尾三件套，三份答案顺序一致
        node.destroy_node()
        if rclpy.ok():                           # 避免重复 shutdown 报错
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 让车前进改哪个字段？        → Twist.linear.x
# Q2 回调里为什么不能 sleep？    → 卡住单线程 executor，所有回调一起停摆
# Q3 Twist() 全 0 为什么能停车？ → 六个分量默认 0，stop() 就是发一条空 Twist
# ─────────────────────────────────────────────────────────────────────

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════
Day10 · 实例代码 1：TF 树检查节点（把 view_frames 变成自动判定）
════════════════════════════════════════════════════════════════════

【这个文件解决什么问题】
  笔记 Day10 让你跑 view_frames 生成 frames.pdf 用肉眼看 TF 树。
  但"用眼睛看箭头"很容易漏掉断链——本节点用 tf2_ros 直接查四个关键变换，
  逐段告诉你"齐/缺"，缺哪段就报该起哪个节点。这是岗位 JD 里
  "坐标系转换""机器人无法定位/建图扭曲"排错的程序化版本。

【心智模型：建图/导航必须齐的四段 TF】
    map ──→ odom ──→ base_link ──→ laser_frame
     ①        ②          ③
  ① map→odom       建图时由 SLAM(gmapping) 给；导航时由 AMCL 给（两者互斥！）
  ② odom→base_link 里程计给的（Day9 验证过 /odom）
  ③ base_link→laser_frame 雷达装车位置，静态变换（static_transform_publisher 或 URDF）
  少任何一段 → 建图/导航直接崩。★ 最常见坑：建图和 AMCL 同时跑，都在发 map→odom，
  TF 打架 → 报 "multiple authority" 或位姿乱跳。

【three 个关键异常（面试会问）】
  LookupException        —— 这个变换根本没人发布（最常见=某节点没起）
  ExtrapolationException —— 时间戳超出缓存范围（两节点时钟不同步、或数据太旧）
  ConnectivityException  —— 两坐标系间链路断了（中间某段没接上）

【为什么用 Buffer + TransformListener 而不是直接 echo /tf】
  /tf 是"增量流"：只发当前变化，echo 出来一堆看似无关的矩阵。
  tf2_ros.Buffer 帮你把增量流累成"完整树"，lookup_transform 直接问
  "A 相对 B 现在的位姿"，这才是建图/导航代码真正用的接口。

【前置】车节点 + 雷达已起；建图时 gmapping 已起（它发 map→odom）。
        若只起底盘没起建图，map→odom 会缺——这是预期现象，不是 bug。
【用法】python3 tf_tree_check.py
        python3 tf_tree_check.py 3.0     # 每 3 秒检查一次
【输出】逐段 [齐] 平移=(x,y,z) / [缺] + 原因，末尾给总结论。
════════════════════════════════════════════════════════════════════
"""

import sys                                          # 读命令行参数（检查周期）
import rclpy                                        # ROS2 Python 总入口
from rclpy.node import Node                         # 节点基类
from rclpy.time import Time                         # TF 查询用的零时刻（取最新变换）
from rclpy.duration import Duration                 # 给 TF 查询的超时时长用
from rclpy.executors import ExternalShutdownException  # 上下文关闭异常，接住避免 traceback
import tf2_ros                                      # TF2 的 Buffer / Listener，查坐标变换的核心库
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
# ↑ TF 查询的三类典型异常，分开捕获才能给出准确的排错提示

# ── 可配置项集中在这里 ─────────────────────────────────────────
CHECK_PERIOD_SEC = 2.0                              # 默认每 2 秒查一遍整条链
TF_CACHE_SEC = 5.0                                  # Buffer 缓存时长：够覆盖查询延迟
# 四段关键变换：(父坐标系, 子坐标系, 人话说明, 缺了要去起什么)
CHAIN = [
    ('map', 'odom', 'SLAM/AMCL 定位', '建图起 slam_gmapping；导航起 AMCL（两者别同时跑）'),
    ('odom', 'base_link', '里程计', '起底盘节点，确认 /odom 有数据（Day9）'),
    ('base_link', 'laser_frame', '雷达到车体', '起 static_transform_publisher 或 robot_state_publisher'),
]
# 注：不同车的雷达 frame 名可能是 laser / laser_frame / lidar_link，
#     用 ros2 run tf2_tools view_frames 看真实名字后改这里。
QOS_TIMEOUT_SEC = 1.0                               # transform 就绪的等待上限


class TfTreeCheck(Node):
    """TF 链巡检：逐段查四段变换是否可查，输出带排错提示的报告。"""

    def __init__(self) -> None:
        super().__init__('tf_tree_check')
        # Buffer 存变换历史，Listener 订阅 /tf 和 /tf_static 往里填
        self._buffer = tf2_ros.Buffer(cache_time=Duration(seconds=TF_CACHE_SEC))
        self._listener = tf2_ros.TransformListener(self._buffer, self)
        period = float(sys.argv[1]) if len(sys.argv) > 1 else CHECK_PERIOD_SEC
        self._timer = self.create_timer(period, self.check)

    def query_link(self, parent: str, child: str) -> tuple:
        """
        查一段变换 parent→child 是否可查。
        返回 (是否成功, 说明文本)。
        ★ lookup_transform(parent, child, Time()) 表示"查最新的"，
          Time() 零时刻 = 取最新可用变换，不用纠结时间戳。
        """
        try:
            # can_transform 先探一下，避免 lookup 直接抛异常打断流程
            if not self._buffer.can_transform(
                    parent, child, Time(),
                    timeout=Duration(seconds=QOS_TIMEOUT_SEC)):
                return False, '变换不存在（无人发布）'
            tf = self._buffer.lookup_transform(parent, child, Time())
            t = tf.transform.translation          # 平移向量
            return True, f'平移=({t.x:.2f}, {t.y:.2f}, {t.z:.2f})'
        except LookupException:
            return False, 'LookupException：该坐标系对没人发布'
        except ConnectivityException:
            return False, 'ConnectivityException：两坐标系间链路断了'
        except ExtrapolationException:
            return False, 'ExtrapolationException：时间戳超范围/数据太旧'
        except Exception as exc:                    # 兜底：未知异常也别让节点崩
            return False, f'未知异常：{type(exc).__name__}'

    def check(self) -> None:
        """周期巡检整条链：逐段查、汇总、缺哪段给对应排错动作。"""
        lines = []
        missing = []
        for parent, child, desc, fix in CHAIN:
            ok, info = self.query_link(parent, child)
            tag = '齐' if ok else '缺'
            lines.append(f'[{tag}] {parent} → {child:<12} {desc} | {info}')
            if not ok:
                missing.append((parent, child, fix))
        self.get_logger().info('===== TF 链体检 =====\n' + '\n'.join(lines))
        if not missing:
            self.get_logger().info('结论：四段 TF 全齐，可以建图/导航')
        else:
            for parent, child, fix in missing:
                self.get_logger().warn(f'  {parent}→{child} 缺失 → {fix}')
            self.get_logger().warn('结论：TF 链不完整，先补齐再进建图/导航')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TfTreeCheck()
    try:
        rclpy.spin(node)                              # 驱动定时器 + Listener 后台收 /tf
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('用户中断或上下文关闭，退出 TF 检查')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

# ─────────────────────────── 本节自查 3 问 ───────────────────────────
# Q1 建图/导航必须齐哪四段？   → map→odom→base_link→laser_frame
# Q2 map→odom 谁发？           → 建图时 SLAM 发，导航时 AMCL 发，两者互斥不能同时
# Q3 为什么不用 echo /tf 看？  → /tf 是增量流；Buffer 才累成完整树供 lookup_transform 查
# ─────────────────────────────────────────────────────────────────────

# ROS2 课程 · 长期稳定环境方案（2026-11-12 定稿）

> 🎯 **目标**：一次定好，以后不再折腾环境。
> **结论**：按用途分成**两个独立 WSL2 发行版，物理隔离**。
> 不装 VMware、不删任何 WSL、不动 `.wslconfig`、不下 3.5G ISO。

---

## 一、为什么这才叫「稳定」
回头看这几次事故，根因是同一个 —— **一个系统里塞了太多用途**：

| 事故 | 根因 |
|---|---|
| Day3 `ros2 run` No executable | ML/torch 把 setuptools 顶到 78，污染了 ament_python |
| Day4 装包 `pkgProblemResolver generated breaks` | 论文环境的 `gz-tools2`(Gazebo Garden) 与 TB3 的 `gazebo11` 硬冲突 |
| E 盘 `Ubuntu` 装不了 Humble | 它是 **26.04 resolute**，Humble 只支持 22.04 jammy |

「一个环境装下所有」本身就是不稳定的来源。
✅ **稳定 = 会打架的东西分开，各自能独立重建。**

---

## 二、架构（长期不再变）

| 发行版 | 位置 | 用途 | 规则 |
|---|---|---|---|
| **`Ubuntu-22.04`**（现有） | `D:\WSL\Ubuntu-22.04` | **论文 / 研究线**：Gazebo Garden(`gz-sim7`)、Isaac Sim、AMCL/Nav2 链路、InternUtopia、PX4、Aliengo、LeRobot、TienKung | 🔴 **永远不动一个包** |
| **`ROS2Course`**（新建） | `E:\WSL\ROS2Course` | **课程线**：ROS2 Humble + TB3 + Gazebo Classic 11 + SLAM/Nav2，Day1~Day7 全在这里 | 随便装/卸/降级，崩了就重建 |
| `Ubuntu` = 26.04（现有） | `E:\WSL\Ubuntu` | 保留，装不了 Humble | 不用于本课程 |
| `docker-desktop`（现有） | `C:\...` | 保留 | 不动 |

**全局配置** `C:\Users\MicckeY\.wslconfig` —— 🔴 **保持原样，一个字都别改**：
```ini
[wsl2]
networkingMode=nat      # InternUtopia / Isaac 的 DDS 多播命脉（mirrored 会破坏）
dnsTunneling=true
autoProxy=true
memory=12GB             # Isaac Sim 需要
processors=8
swap=8GB
```

**为什么 WSL2 而不是 VM**：WSL2 **有 CUDA/GPU 能力**，VM 没有 NVIDIA 直通 ——
以后课程要接 Isaac / 训练也不受限；且零 Windows 功能改动、零重启、`/mnt/d` 文件互通。

---

## 三、为什么不选其它方案（对比）

| 方案 | 为什么不当长期方案 |
|---|---|
| VMware VM | 无 GPU 直通，以后 CUDA/Isaac 受限；要改 Windows 功能+重启；独占 6~8G；共享文件夹/快照维护负担 |
| 删 WSL 全用 VM | 毁掉论文/Isaac/训练环境，**不可逆**，且 GPU 受限 |
| 复用 `~/ros2_amcl` 跑课程 | 能救今天，但课程与论文共用一个环境，迟早再撞；载具是 Isaac 人形 H1 而非 TB3，与主流教程脱节 |
| 在现有 WSL 强装/降级 | `gz-tools2` 硬冲突，卸了毁论文环境；setuptools 降级撞 torch |

---

## 四、一次性落地（约 30~40 分钟，全部放 E 盘）

### 1. 下载干净 22.04 rootfs（325MB，E 盘）
**PowerShell**：
```powershell
New-Item -ItemType Directory -Force E:\WSLDownload | Out-Null
Invoke-WebRequest -Uri "https://cloud-images.ubuntu.com/wsl/jammy/current/ubuntu-jammy-wsl-amd64-ubuntu22.04lts.rootfs.tar.gz" -OutFile "E:\WSLDownload\ubuntu-22.04-rootfs.tar.gz"
```
备用（223MB）：`https://cloud-images.ubuntu.com/wsl/releases/22.04/current/ubuntu-jammy-wsl-amd64-wsl.rootfs.tar.gz`
下载慢就用浏览器/下载工具下好放同一路径。

### 2. 导入为独立发行版（名字 `ROS2Course`）
```powershell
wsl --import ROS2Course E:\WSL\ROS2Course E:\WSLDownload\ubuntu-22.04-rootfs.tar.gz --version 2
wsl -l -v
```
> ⚠️ `wsl.exe` 在我这侧被沙箱黑名单拦截，这两条**得你在 PowerShell 敲**。

### 3. 建普通用户（导入后默认是 root）
```bash
wsl -d ROS2Course
# 进去后依次执行：
adduser micckey                 # 设密码，其余一路回车
usermod -aG sudo micckey
printf '[user]\ndefault=micckey\n' | tee -a /etc/wsl.conf
exit
```
回 PowerShell：`wsl --terminate ROS2Course`，再 `wsl -d ROS2Course` 即生效。

### 4. 一键装课程环境
```bash
cd /mnt/d/ROS2七天速成/Day4_Nav2建图/模板
bash 一键装ROS2课程环境.sh
```
脚本：locale → 中科大 ROS2 源 → `ros-humble-desktop` + `ros-dev-tools` →
TB3 / Gazebo11 / SLAM / Nav2 → 写 `~/.bashrc` → 验证。约 **20~40 分钟**。跑完重开终端。

### 5. 验证（应全绿）
```bash
lsb_release -c -s                    # 必须 jammy
ros2 --version
ros2 pkg prefix turtlebot3_gazebo
gazebo --version                     # 应输出 Gazebo 11.x
dpkg -l | grep gz-tools2             # 应为空 ← 隔离成功的标志
```

---

## 五、★ 长期规则（「以后一直用」的关键）
1. **课程 / 任何新 ROS2 包 → 只在 `ROS2Course`**，想装啥装啥、随便降级/卸载。
2. **论文 / Isaac Sim / Gazebo Garden / LeRobot / 训练 → 只在 `Ubuntu-22.04`**，一个包都别动。
3. **`.wslconfig` 永远不改**（`networkingMode=nat` 是 InternUtopia DDS 的命脉）。
4. **分时运行**：不同时跑两个重负载（内存全局 12G 上限）。做课程前 `wsl --shutdown` 可释放内存，之后重开即可；两个环境「后面都能用」。
5. **课程材料放 D 盘**（`D:\ROS2七天速成`），两边 `/mnt/d` 都能读；不要在 WSL 内部互拷。
6. **B 崩了就重建**：`wsl --unregister ROS2Course` → 重跑第四节 2~4 步，约 30 分钟满血；**A 永不参与，绝不连坐**。

---

## 六、Day4 在这套环境下怎么跑
在 **`ROS2Course`** 终端里（三终端，与 `笔记.md` 一致）：
```bash
bash /mnt/d/ROS2七天速成/Day4_Nav2建图/模板/启动建图.sh
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
ros2 run turtlebot3_teleop teleop_keyboard
```
建完存图：`bash 模板/保存地图.sh` → `~/tb3_map.pgm` + `.yaml`（Day5 用）。

> **图形**：Win11 自带 WSLg，`echo $DISPLAY` 有值即可；黑屏兜底 `export LIBGL_ALWAYS_SOFTWARE=1`。
> 只有 WSLg 实在跑不了 Gazebo 时，才启用第七节的 VM 备选。

---

## 七、备选（留档，非当前路线）
- `VM方案_装机清单.md` + `模板/VM内一键装ROS2与TB3.sh`：WSLg 图形失败时启用，ISO/VM 文件放 E 盘（196G 可用）。
- `模板/现有WSL_安全清理.sh`：只清 apt/pip 缓存，不动任何包。
- `~/ros2_amcl` 菜单链路：论文线的现成 SLAM/AMCL/Nav2 实现，可作 Day4/Day5 参考，**不与课程线混用**。

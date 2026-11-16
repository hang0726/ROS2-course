# Day4 · B 方案：VMware 虚拟机装机清单

> 🎯 **目的**：在**干净的 Ubuntu 22.04 桌面 VM** 里跑 ROS2 Humble + TurtleBot3 建图，
> 与现有 WSL（Gazebo Garden / 论文环境）**完全隔离、互不干扰**。
>
> 🔴 **三条红线（贯穿全程）**
> 1. **不要动现有 WSL 的任何包**，尤其 `gz-tools2` / `gz-sim7` / `gz-garden`（论文、PX4、人形课室、Aliengo 的仿真底座）。
> 2. **不要执行 `bcdedit /set hypervisorlaunchtype off`**（会关掉 WSL2 / Docker / 内存完整性）。
> 3. VM 里**只装 Gazebo Classic 11**，别手滑装新版 `gz-*`，否则又冲突。

---

## 为什么必须换环境（一句话）
`ros-humble-turtlebot3-gazebo` 需要 **Gazebo Classic 11**；你现有 WSL 装的是
**Gazebo Garden**（`gz-garden 1.0.0` / `gz-sim7 7.9.0` / `gz-tools2 2.0.4`），
而 `gz-tools2` 的 deb 明确写了 `Conflicts: gazebo (>=11.0.0) (<=11.14.0)` → apt 无解。

⚠️ 上次安装失败发生在**依赖解析阶段**，一个包都没装进去 —— **现有 WSL 环境完好无损，本来就还能用**，不需要修、不需要卸。

---

## 一、Windows 侧（4 步）

### 1. 启用「Windows 虚拟机监控程序平台」（让 VMware 与 WSL2 共存）
本机是 Win11 **家庭版**，无 Hyper-V 管理器，但 WSL2 的 hypervisor 已在跑。
**管理员 PowerShell**：
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -All
```
或 GUI：`控制面板 → 程序 → 启用或关闭 Windows 功能` → 勾 **Windows 虚拟机监控程序平台** → 确定 → **重启**。
> 只勾这一个，别碰 `bcdedit`。

### 2. 装 VMware Workstation Pro
Broadcom 官网下载 Windows 版（**2024-11 起个人/商用全免费**，需注册账号，无需 license key）。
备选：VirtualBox 7.x（免注册，但 3D 加速对 Gazebo 支持较弱，可能黑屏）。

### 3. 下载 Ubuntu 22.04.5 桌面 ISO
`https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/22.04/`（清华镜像，约 3.5G）
> ⚠️ ROS2 **Humble 只支持 22.04**，别下 24.04。

### 4. 新建虚拟机（关键参数）
| 项 | 建议 |
|---|---|
| 内存 | **6~8 GB**（本机共 31.4G，见第四节分时复用） |
| 处理器 | 4 核 |
| 磁盘 | **≥ 50 GB**（ROS2 + Gazebo + TB3 约 20G，留余量） |
| 网络 | NAT（默认） |
| ★ 显示 | **勾选「加速 3D 图形」**，显存拉到 2~4 GB ← **Gazebo 不黑屏的关键** |
| 共享文件夹 | 勾上，把 `D:\ROS2七天速成` 挂进 VM |

装 Ubuntu 一路下一步，用户名建议 `micckey`，密码记好。
进桌面后先跑一次：
```bash
sudo apt update && sudo apt upgrade -y && sudo reboot
```

---

## 二、把课程材料弄进 VM
三选一：**VMware 共享文件夹**（最快）/ U 盘 / 直接拖文件。
目标路径建议 `~/ROS2七天速成/`，把 `D:\ROS2七天速成` 整个拷进去。
> 共享文件夹挂点通常是 `/mnt/hgfs/ROS2七天速成/`；看不到就先装 `open-vm-tools`（一键脚本里已装）再重登。

---

## 三、VM 内一键装环境
```bash
cd ~/ROS2七天速成/Day4_Nav2建图/模板
bash VM内一键装ROS2与TB3.sh
```
脚本做 6 件事：locale → 中科大 ROS2 源 → `ros-humble-desktop` + `ros-dev-tools` →
TB3 / Gazebo11 / SLAM / Nav2 全家桶 → `open-vm-tools` → 写 `~/.bashrc`。
约 **20~40 分钟**（看网速）。跑完**重开终端**或 `source ~/.bashrc`。

---

## 四、★ 内存怎么安排（这就是「清理内存」的答案，零改动）
实测：本机 **31.4 GB** 总内存，当时可用仅 **5.5 GB**。
查到 `C:\Users\MicckeY\.wslconfig` **已存在且是给 InternUtopia + Isaac Sim 配的**：
```ini
[wsl2]
networkingMode=nat      # 注释：为了 DDS 多播能跨 Windows/WSL
dnsTunneling=true
autoProxy=true
memory=12GB
processors=8
swap=8GB
```

🔴 **不要改这个文件**：
- `networkingMode=nat` 一改，InternUtopia 的 DDS 发现就崩；
- `memory=12GB` 是 Isaac Sim 需要的，调小会拖慢它。

✅ **正确做法 = 分时复用（零配置改动，两个环境「后面也都能用」）**
- **做 ROS2 课程（Day4~Day7）时**：在 Windows PowerShell 执行
  ```powershell
  wsl --shutdown
  ```
  这会关掉 WSL2 虚拟机，把 `vmmem` 占用的内存**全部释放**（最多 12G），VM 立刻有内存可用。
  ⚠️ 执行前确认 WSL 里没有正在跑的仿真/训练（会被一起关掉）。
- **要回去跑 InternUtopia / Isaac Sim / AMCL 论文时**：关掉 VM，重开一个 Ubuntu 终端，WSL 自动起来，`.wslconfig` 原样生效 —— **什么都没变，照旧能用**。

> 结论：现有 WSL **不需要清理、不需要修复**，它本来就是好的；
> 只是别让它和 VM 同时抢内存。

---

## 五、Day4 接着跑（VM 里三终端，与笔记一致）
```bash
# 终端1：起 Gazebo 世界
bash ~/ROS2七天速成/Day4_Nav2建图/模板/启动建图.sh
# 终端2：起 SLAM 建图
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
# 终端3：RViz + 键盘遥控
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
ros2 run turtlebot3_teleop teleop_keyboard
```
建完存图：`bash 模板/保存地图.sh` → `~/tb3_map.pgm` + `.yaml`（Day5 用）。

---

## 六、现有 WSL 的可选清理（只清缓存，不动任何包）
```bash
bash ~/ROS2七天速成/Day4_Nav2建图/模板/现有WSL_安全清理.sh
```
只做：清 apt 下载缓存、systemd 日志、pip 缓存 → **纯腾磁盘**。
> ⚠️ 我这边 `wsl.exe` 被沙箱黑名单拦截、Bash 的 PATH 也被 strip，
> 所以**清缓存和 `wsl --shutdown` 都需要你在自己的终端敲**；脚本已写好，一行跑完。

---

## 七、坑清单
- **Gazebo 黑屏 / 极卡** → VM 设置里「加速 3D 图形」没勾或显存太小；兜底 `export LIBGL_ALWAYS_SOFTWARE=1`。
- **`ros2 run` 找不到包** → 忘了 `source ~/.bashrc`；重开终端最省事。
- **`Unable to locate package ros-humble-*`** → USTC 源没写对，检查 `/etc/apt/sources.list.d/ros2.list`。
- **VM 里手滑装了 `gz-*`** → 立刻 `apt remove`，别让它和 gazebo11 共存。
- **分辨率不自适应 / 不能复制粘贴** → 确认 `open-vm-tools-desktop` 已装并重启 VM。
- **共享文件夹 `/mnt/hgfs` 为空** → `sudo mount -t fuse.vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other` 或重登。

# AscendCL C++ 推理五步（Day12 · 补 C++ 缺口的实战）

> 🎯 这份文档讲清用 AscendCL 加载 .om 模型做推理的标准五步，配套昇腾官方样例库
> `https://gitee.com/ascend/samples` 的 ResNet50 分类样例看代码。
> ★ 这就是你一直缺的 **C++ 独立实现证据**——不是写玩具，是真正部署 AI 模型。

---

## 环境准备

```bash
source ~/Ascend/ascend-toolkit/set_env.sh   # 加载 CANN 环境变量
export DDK_PATH=~/Ascend/ascend-toolkit/<版本>
export NPU_HOST_LIB=$DDK_PATH/acllib/linux.x86_64/lib64/stub
```
🔴 `CMakeLists.txt` 里 `acllib` 的 include 路径要指对，否则报 `acl/acl.h not found`。

---

## 推理五步（背下来，面试会问）

| 步 | API | 干什么 |
|---:|---|---|
| ① 初始化 | `aclInit(nullptr)` | 初始化 AscendCL 运行时 |
| ② 加载模型 | `aclmdlLoadFromFile("model.om", &modelId)` | 把 ATC 转出的 .om 加载进 NPU |
| ③ 准备数据 | `aclrtMalloc` + `aclrtMemcpy` | 申请 Device 内存，把输入数据拷进去 |
| ④ 执行推理 | `aclmdlExecute(modelId, input, output)` | NPU 跑推理 |
| ⑤ 取结果+释放 | `aclrtMemcpy` 拷回 Host + `aclmdlUnload` + `aclFinalize` | 拿输出、释放资源 |

---

## 最小代码骨架（照 samples 改）

```cpp
#include "acl/acl.h"
int main() {
    aclInit(nullptr);                                    // ① 初始化
    uint32_t modelId;
    aclmdlLoadFromFile("model_ascend.om", &modelId);     // ② 加载 .om
    // ③ 准备 input/output dataset（见 samples 完整代码，含 aclmdlCreateDataset 等）
    // ④ aclmdlExecute(modelId, inputDataset, outputDataset);
    // ⑤ 拷贝结果到 Host、打印、释放
    aclmdlUnload(modelId);
    aclFinalize();
    return 0;
}
```

> 完整可编译版：`gitee.com/ascend/samples` → `cplusplus/level2_simple_inference/1_classification/resnet50_imagenet_classification`

---

## 常见坑

- **`aclInit` 失败** —— 环境变量没 source / 驱动没装。
- **加载 .om 失败** —— soc_version 不对 / CANN 版本和 ATC 转换时不一致。
- **推理结果全错** —— 预处理和训练不一致（BGR/RGB、归一化均值方差、HWC/NCHW）。
- **内存越界** —— input shape 和 .om 期望的不一致。

---

## 怎么变成简历证据

把 samples 的 ResNet50 改成**你的检测模型**，让推理结果（类别+框）通过 ROS2 话题发出去
（见 `detection_to_ros2.md`）——这就从"跑通官方样例"升级成"我做的端侧 AI 部署节点"。

---

## 自查 3 问
1. AscendCL 推理五步？(aclInit→加载.om→准备数据→aclmdlExecute→取结果释放)
2. 为什么这是 C++ 证据？（AscendCL 是 C/C++ API，官方样例就是 C++ 工程）
3. 推理结果全错优先查什么？（预处理和训练是否一致：通道序/归一化/数据布局）

# Mocap API 演示程序集

本项目包含多个基于 `mocap_api` 的演示程序，用于与各种动作捕捉系统进行交互。这些演示程序展示了如何使用 `mocap_api` 库获取动作捕捉数据和发送控制命令。

## 演示程序列表

### 1. Axis Studio 命令控制演示 (`mocap_axis_command_demo.py`)

**功能**：用于控制 Axis Studio 软件的录制功能。

**主要特性**：
- 开始/停止录制任务
- 支持自定义录制任务名称
- 命令执行状态检查
- 键盘快捷键控制

**键盘快捷键**：
- `N` - 设置录制任务名称
- `R` - 开始录制
- `S` - 停止录制
- `ESC` - 退出程序

### 2. Axis Studio 数据接收演示 (`mocap_axis_demo.py`)

**功能**：实时接收并显示来自 Axis Studio 的人体 BVH 数据。

**主要特性**：
- UDP 协议数据接收
- 实时解析人体关节数据
- 显示关节名称、位置和旋转信息

### 3. Hybrid Data Server 数据接收演示 (`mocap_hds_demo.py`)

**功能**：接收并显示来自 Hybrid Data Server 的多种数据类型。

**支持的数据类型**：
- 人体 BVH 数据 (`AvatarUpdated`)
- 追踪器数据 (`AliceTrackerUpdated`)
- Marker 散点数据 (`AliceMarkerUpdated`)
- 刚体数据 (`AliceRigidbodyUpdated`)
- 道具数据 (`TrackerUpdated`)
- 惯性传感器数据 (`AliceIMUUpdated`)

### 4. Axis Studio 计算数据接收演示 (`mocap_axis_calc_demo.py`)

**功能**：接收并显示来自 Axis Studio 的计算数据。

**主要特性**：
- 配置计算数据接收
- 实时解析骨骼传感器数据
- 显示姿态、角速度和加速度信息

### 5. PNLink 命令控制演示 (`mocap_pnlink_command_demo.py`)

**功能**：用于控制 PNLink 设备的各种命令。

**支持的命令**：
- 开始/停止捕捉 (`N`/`F`)
- 动作校准 (`C`)
- 恢复原始手部姿势 (`R`)
- 清除零动作漂移 (`0`)
- 恢复原始身体姿势 (`O`)
- 归零位置 (`Z`)
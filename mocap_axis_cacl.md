Calculation Data 数据广播

## 一、概述

本文档详细阐述使用 mocap api 获取Axis Studio Calculation Data 数据广播的具体流程。

## 二、获取前提条件

### 1. 实时数据广播开启​

- **操作步骤：​**
1. 连接动作捕捉设备并完成校准，确保 Axis Studio 显示实时数据。​

2. 打开Settings→Calc Broadcasting，启用Calculation Data - Capture模块（开关变蓝）。​

3. 选择传输协议（UDP/TCP），设置本地端口（如7012），确保与 mocap api 代码中settings.set_udp(7012)一致。​

![实时广播](cacl_capture.png)

### 2. 录制数据广播开启​

- **操作步骤：**​
1. 在 Axis Studio 中打开已录制的动作数据文件。​

2. 点击Play播放数据，启用Calculation Data - Edit模块，配置相同协议和端口。​

3. 如需循环广播，勾选Repeat选项。

![录制广播](cacl_edit.png)

## 三、数据获取流程

- **代码实现**

```python
# 导入必要模块
from pnmocap import MCPApplication, MCPSettings, MCPEventType, MCPAvatar

# 1. 初始化应用与设置
app = MCPApplication()
settings = MCPSettings()

# 2. 配置数据广播协议与端口（需与Axis Studio一致）
settings.set_udp(7012)  # 使用UDP协议，端口7012
settings.set_calc_data()  # 关键配置：指定获取Calculation Data

# 3. 应用设置并连接Axis Studio
app.set_settings(settings)
app.open()

# 4. 循环获取数据（实时监听Avatar更新事件）
try:
    while True:
        evts = app.poll_next_event()
        for evt in evts:
            if evt.event_type == MCPEventType.AvatarUpdated:
                # 解析角色数据
                avatar = MCPAvatar(evt.event_data.avatar_handle)
                joints = avatar.get_joints()  # 获取所有关节

                for joint in joints:
                    joint_name = joint.get_name()
                    sensor_module = joint.get_sensor_module()

                    # 提取Calculation Data核心数据
                    posture = sensor_module.get_posture()        # 姿态四元数
                    angular_velocity = sensor_module.get_angular_velocity()  # 角速度
                    acceleration = sensor_module.get_accelerated_velocity()  # 加速度

                    # 示例：打印数据（实际应用中可发送至机器人/引擎）
                    print(f"关节: {joint_name}, 姿态: {posture}, 角速度: {angular_velocity}, 加速度: {acceleration}")

except KeyboardInterrupt:
    # 异常处理：安全关闭连接
    app.close()
```

- 上述代码分别创建了`MCPApplication`应用实例和`MCPSettings`设置实例，为后续配置和连接 Axis Studio 软件做准备。`MCPApplication`实例用于管理整个数据获取应用的生命周期，`MCPSettings`实例则用于配置数据获取相关的参数。
* `settings.set_udp(7012)`：此代码设置使用 UDP 协议进行数据传输，并指定端口号为 7012。在实际应用中，需确保该端口未被其他程序占用，且与 Axis Studio 软件配置的目标端口一致，以保证数据能够正确发送和接收。

* `settings.set_calc_data()`：该方法至关重要，用于配置获取 Calculation Data 数据。调用此方法后，mocap api 将按照 Calculation Data 数据格式的要求，从 Axis Studio 软件获取数据。

* `app.set_settings(settings)`：将配置好的`MCPSettings`实例应用到`MCPApplication`实例中，使之前设置的网络参数和数据类型生效。

* `app.open()`：尝试建立与 Axis Studio 软件的连接。若连接成功，即可开始进行数据获取操作；若连接失败，需检查网络配置、权限设置以及 Axis Studio 软件是否正常运行。

* 使用一个无限循环持续轮询应用事件，`app.poll_next_event()`方法用于获取下一批事件。

* 当检测到事件类型为`MCPEventType.AvatarUpdated`时，表示数据已更新，此时创建`MCPAvatar`实例来获取角色相关信息。

* 通过`avatar.get_joints()`获取角色所有关节数据，遍历每个关节，获取其传感器模块。

* 从传感器模块中提取姿态（`posture`）、角速度（`angular_velocity`）、加速度（`accelerated_velocity`）等 Calculation Data 数据，并进行打印输出。在实际应用中，可将这些数据进一步处理，如发送给机器人控制模块、用于生物力学分析等。



## 五，传感器骨骼对应表



| 名称  | 标识            | 序号  |
| --- | ------------- | --- |
| 臀部  | Hips          | 1   |
| 右大腿 | RightUpLeg    | 2   |
| 右小腿 | RightLeg      | 3   |
| 右脚  | RightFoot     | 4   |
| 左大腿 | LefUpleg      | 5   |
| 左小腿 | LeftLeg       | 6   |
| 左脚  | LeftFoot      | 7   |
| 右肩  | RightShoulder | 8   |
| 右大臂 | RightArm      | 9   |
| 右前臂 | RightForeArm  | 10  |
| 右手  | RightHand     | 11  |
| 左肩  | LeftShoulder  | 12  |
| 左大臂 | LeftArm       | 13  |
| 左前臂 | LeftForeArm   | 14  |
| 左手  | LeftHand      | 15  |
| 头部  | Head          | 16  |
| 脊柱  | Spine2        | 17  |

## 六，骨骼与传感器关系

在 Calculation Data 数据体系中，传感器与骨骼并非传统意义上的物理绑定关系，而是基于**数据影响权重**的逻辑关联。即使某个关节未安装 IMU 传感器，系统仍能通过计算邻近传感器数据的影响程度，推算该关节对应的 SensorModule 位姿信息。

### 1. 数据推算原理

系统默认以**层级最近的父骨骼传感器**为基准，结合骨骼拓扑结构，采用空间插值算法推算无传感器关节数据。例如，当右手未佩戴 IMU 时：

- 右手关节（RightHand）的 SensorModule 数据将直接继承自其**父骨骼 —— 右前臂（RightForeArm）传感器**。
- 若右前臂同样无传感器，则继续向上追溯至**右大臂（RightArm）传感器**，直至找到可用数据源。

### 2. 应用场景说明

这种设计机制主要适用于以下场景：

- **部分设备缺失**：用户因设备不足或临时故障导致传感器佩戴不全时，仍可获取完整的骨骼姿态数据。
- **数据补全需求**：在数据处理过程中，通过算法填充缺失传感器数据，确保动作捕捉数据的连贯性与完整性。

### 3. 数据准确性说明

系统推算的 SensorModule 数据并非随机生成，而是基于严谨的物理模型与拓扑逻辑。尽管与实际传感器数据存在细微差异，但在大多数应用场景下（如虚拟角色动画、基础动作分析），推算数据已能满足基础使用需求。若需**高精度数据，建议确保所有关键关节均配备传感器。**

# PN-Link Python 操作指南

本文介绍如何通过 Python WebUI 调用 MocapApi SDK，直连 PN-Link 主节点，完成动作数据采集、人体姿态校准和数据可视化。

## 目录

- [1. 产品与工程概述](#1-产品与工程概述)
- [2. 快速开始](#2-快速开始)
- [3. 环境与依赖](#3-环境与依赖)
- [4. 网络配置](#4-网络配置)
- [5. 启动 Web 服务](#5-启动-web-服务)
- [6. 设备操作](#6-设备操作)
- [7. 指令调用说明](#7-指令调用说明)
- [8. 常见问题](#8-常见问题)
- [9. 安全退出](#9-安全退出)

## 1. 产品与工程概述

### 1.1 PN-Link

PN-Link 是诺亦腾推出的全身有线惯性动作捕捉产品。各身体子节点通过有线方式将数据汇总至背部主节点，再由主节点通过网络传输至主机。

与无线惯性动作捕捉产品相比，PN-Link 支持直连模式：无需安装 Axis Studio，即可通过 MocapApi SDK 直接连接主节点，完成数据采集和人体姿态校准等操作。

### 1.2 示例工程

本工程通过 Python WebUI 演示以下功能：

- 连接 PN-Link 主节点
- 开始和停止动作捕捉
- 执行人体姿态校准
- 输出 3D 骨骼数据或关节数据
- 在浏览器中实时显示 3D 动作
- 调整 PN-Link 网络与数据参数

## 2. 快速开始

以下命令假设工程目录为 `~/mocapapi-demo-py`，且 `MocapApi` 与 `python_webui` 均位于工程根目录下。若实际目录结构不同，请相应调整路径。

```bash
cd ~/mocapapi-demo-py

# 创建并激活 Python 3.11 虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
python -m pip install --upgrade pip
python -m pip install nicegui==2.24.1
python -m pip install -e ./MocapApi

# 启动 Web 服务
cd python_webui
python web_ui.py
```

启动成功后，在浏览器中访问 [http://localhost:8080](http://localhost:8080/)。

> 每次打开新终端运行本工程前，都需要先进入工程根目录并执行 `source venv/bin/activate`。

## 3. 环境与依赖

### 3.1 环境要求

| 项目 | 要求 |
| --- | --- |
| Python | 建议使用 Python 3.8 至 3.11；本文以 Python 3.11 为例 |
| NiceGUI | `nicegui==2.24.1` |
| 浏览器 | 支持 WebGL 的现代浏览器，如 Chrome 或 Microsoft Edge |
| 硬件 | PN-Link 有线动作捕捉套装 |

> Python 3.12 及以上版本未在本文对应工程中确认兼容性。若出现依赖错误，建议改用 Python 3.11 创建虚拟环境后重试。

### 3.2 使用虚拟环境

Ubuntu、Debian 等 Linux 发行版可能限制直接向系统 Python 安装第三方包，并提示 `externally-managed-environment`。为避免污染系统环境，本工程应在虚拟环境中安装和运行。

创建虚拟环境：

```bash
cd ~/mocapapi-demo-py
python3.11 -m venv venv
```

激活虚拟环境：

```bash
source venv/bin/activate
```

激活后，终端提示符通常会出现 `(venv)` 前缀。退出虚拟环境时执行：

```bash
deactivate
```

### 3.3 安装 Python 3.11

#### Ubuntu

如果当前 Ubuntu 软件源未提供 Python 3.11，可使用 deadsnakes PPA：

```bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv -y
```

> deadsnakes PPA 面向 Ubuntu，不适用于 Debian。

#### Debian

优先使用 Debian 官方软件源提供的 Python 和 `venv` 组件：

```bash
sudo apt update
sudo apt install python3 python3-venv -y
python3 --version
```

如果系统提供的 Python 版本不在本工程建议范围内，请通过适合当前 Debian 版本的方式单独安装 Python 3.11，再使用该解释器创建虚拟环境。

### 3.4 安装工程依赖

在工程根目录执行：

```bash
source venv/bin/activate
python -m pip install nicegui==2.24.1
python -m pip install -e ./MocapApi
```

网络访问 PyPI 较慢时，可选用清华 PyPI 镜像安装 NiceGUI：

```bash
python -m pip install nicegui==2.24.1 \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

检查安装结果：

```bash
python --version
python -m pip show nicegui
```

`pip show` 输出中的 `Version` 应为 `2.24.1`。

## 4. 网络配置

### 4.1 默认参数

| 角色 | 默认 IP 地址 | 默认 UDP 端口 | 用途 |
| --- | --- | --- | --- |
| 客户端（运行工程的主机） | `10.42.0.101` | `8002` | 接收动作数据 |
| 服务器（PN-Link 主节点） | `10.42.0.202` | `8080` | 提供设备连接 |

需要将主机网卡配置到 `10.42.0.x` 网段，例如 `10.42.0.101`，确保主机与 PN-Link 主节点位于同一局域网且 IP 地址不冲突。

### 4.2 工程配置

IP 地址、端口和相关资源路径可在 `web_config.py` 中调整：

```python
# web_config.py
SERVER_IP = "10.42.0.202"      # PN-Link 主节点 IP
SERVER_PORT = 8080             # PN-Link 主节点 UDP 端口
CLIENT_IP = "10.42.0.101"     # 主机 IP
CLIENT_PORT = 8002             # 主机 UDP 端口
BVH_HEADER_FILE = "config/bvh_header.json"
WEB_THREE_HTML = "web/three_fbx_viewer.html"
```

`mocap_control.py` 中的初始化逻辑如下：

```python
class MCPControl:
    def __init__(self, msg_queue: multiprocessing.Queue = None):
        self.app = MCPApplication()
        settings = MCPSettings()

        # 配置 BVH 数据格式和转换方式
        settings.set_bvh_data(MCPBvhData.Binary)
        settings.set_bvh_transformation(MCPBvhDisplacement.Enable)
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)

        # 配置 UDP 传输参数
        settings.SetSettingsUDPEx(CLIENT_IP, CLIENT_PORT)
        settings.SetSettingsUDPServer(SERVER_IP, SERVER_PORT)
```

默认骨骼旋转顺序为 `XYZ`。如需调整，请同时确认设备端与工程配置使用相同的旋转顺序。

## 5. 启动 Web 服务

1. 打开终端并进入工程根目录：

   ```bash
   cd ~/mocapapi-demo-py
   ```

2. 激活虚拟环境：

   ```bash
   source venv/bin/activate
   ```

3. 进入 WebUI 目录并启动服务：

   ```bash
   cd python_webui
   python web_ui.py
   ```

4. 在浏览器中访问 [http://localhost:8080](http://localhost:8080/)。

## 6. 设备操作

### 6.1 连接 PN-Link

前置条件：

- PN-Link 主节点已上电并正常工作。
- 主机与主节点位于同一网段。
- `web_config.py` 中的 IP 地址和端口与实际环境一致。
- Web 服务已启动。

打开 Web 页面后，状态栏显示绿色“已连接”，表示设备连接成功。

### 6.2 开始捕捉

1. 点击 **Start Capture**。
2. 保持站立或坐姿稳定至少 15 秒，等待设备完成初始化。
3. 为获得更稳定的初始化效果，可额外等待约 10 秒后再开始动作。

初始化完成后，页面开始接收并显示实时动作数据。

### 6.3 姿态校准

1. 点击 **Calibrate**。
2. 按页面提示依次完成以下姿态：

   - VB-Pose
   - P-Pose
   - T-Pose
   - A-Pose
   - F-Pose

3. 完成所有姿态后等待系统计算校准结果，通常需要 1 至 3 分钟。
4. 页面显示“Mocap 校准完成！”时，表示校准成功。

### 6.4 其他操作

| 操作 | 作用 |
| --- | --- |
| **Resume Hands** | 恢复手势捕捉 |
| **Reset 0 Motion Drift** | 清除运动漂移误差 |
| **Resume Body** | 恢复身体姿态基准 |
| **Zero Position** | 将当前位置设置为姿态零点 |
| **Stop Capture** | 停止动作数据采集 |

### 6.5 切换数据输出

点击“切换数据输出”，可在以下两种模式间切换：

| 模式 | 输出内容 |
| --- | --- |
| **3D Data** | 完整骨骼位置与旋转数据，可用于浏览器 3D 实时显示 |
| **Joint Data** | 关节角度数据 |

### 6.6 PN-Link 设置

点击 **PN-Link 设置**，可调整以下参数：

- IP 地址和端口
- 数据传输格式
- 骨骼旋转顺序

修改后应确保设备端与工程端的网络和数据格式配置一致。

## 7. 指令调用说明

### 7.1 推荐执行顺序

1. 创建网络连接。
2. 执行开始采集指令。
3. 接收并输出采集数据。
4. 根据需要执行校准或其他控制指令。
5. 执行停止采集指令。

### 7.2 单条指令生命周期

每条指令应按以下顺序处理：

1. 创建指令。
2. 执行指令。
3. 等待指令执行完成。
4. 销毁指令。

## 8. 常见问题

### 8.1 设备连接失败

按以下顺序检查：

1. 确认主机与 PN-Link 主节点均已上电并正常连接。
2. 确认主机 IP 与主节点 IP 位于同一网段，例如 `10.42.0.x`。
3. 确认 `web_config.py` 中的客户端和服务器 IP 与实际配置一致。
4. 确认客户端 UDP 端口 `8002` 未被其他程序占用。
5. 确认防火墙未阻止相关网络通信。
6. 重启 PN-Link 主节点和 Web 服务后重试。

### 8.2 姿态校准失败

- 开始捕捉后，保持姿态稳定至少 15 秒再执行校准。
- 按页面提示完成全部校准姿态。
- 确认工程与设备使用相同的骨骼旋转顺序，默认值为 `XYZ`。
- 若仍然失败，停止捕捉、重启设备，然后重新执行初始化和校准。

### 8.3 出现 `externally-managed-environment`

原因：当前命令尝试向受系统管理的 Python 环境安装第三方包。

解决方法：

```bash
cd ~/mocapapi-demo-py
python3.11 -m venv venv
source venv/bin/activate
python -m pip install nicegui==2.24.1
python -m pip install -e ./MocapApi
```

不要使用系统级 `pip` 直接安装本工程依赖。

### 8.4 出现与 `pkgutil` 相关的 `AttributeError`

该问题可能与 Python 版本或依赖版本不兼容有关。先检查当前解释器：

```bash
python --version
which python
```

确认命令使用的是工程虚拟环境中的 Python。若当前版本高于 3.11，可删除并重新创建 Python 3.11 虚拟环境，然后重新安装依赖。

## 9. 安全退出

为避免采集数据丢失或设备状态异常，建议按以下顺序关闭系统：

1. 点击 **Stop Capture**，停止动作捕捉。
2. 确认采集已停止后关闭浏览器页面。
3. 在运行 Web 服务的终端中按 `Ctrl+C`。
4. 如需退出虚拟环境，执行 `deactivate`。

---

> 本文根据现有操作文档整理。工程目录、页面按钮和 SDK 兼容范围应以实际源码、设备固件及所用 MocapApi SDK 版本为准。

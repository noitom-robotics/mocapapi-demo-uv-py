本工程演示了如何从Noitom公司提供的动捕设备获取数据，并通过MocapApi库获取数据，并操作axis studio进行开始录制和结束录制功能。

## 项目概述

本项目提供了一个图形界面应用程序，用于控制Noitom动捕设备进行动作录制和停止操作。它基于MocapApi库与动捕设备通信，并提供直观的用户界面来执行基本控制命令。

## 目录结构

```
.
├── 3rdparty
│   └── MocapApi
│       ├── include
│       │   └── MocapApi
│       │       └── MocapApi.h
│       ├── mocap_api.py
│       └── setup.py
├── python_command
    ├── config.py
    ├── gui_mocap_controller.py
    ├── mocap_control.py
    └── README.md

 
```

## 功能特性

- 图形用户界面控制动捕设备
- 开始/停止动作录制功能
- 通过UDP协议与动捕服务端通信
- 实时状态信息显示
- 错误处理和日志记录

## 环境要求

- Python 3.x
- Tkinter (通常随Python一起安装)
- Noitom动捕设备及相关软件 (Axis Studio)

## 安装步骤

1. 确保已安装Python 3.x环境
2. 安装MocapApi库:
   ```bash
   cd MocapApi
   pip install -e .
   ```
3. 确保动捕设备及相关软件已正确安装和配置

## 配置说明

在[python_command/config.py](python_command/config.py)中配置以下参数:

- `SERVER_IP`: 动捕服务端IP地址
- `SERVER_PORT`: 动捕服务端端口
- `CLIENT_IP`: 客户端IP地址
- `CLIENT_PORT`: 客户端端口

## Axis Studio
### 启动*Axis Studio*, 打开一个动作数据文件
此时能看到Axis Studio里的3D模型在运动，如下图所示：

   ![launch_axis_studio](img/launch_axis_studio.gif)

### 配置 *BVH Broadcasting*

打开设置对话框，选择BVH Broadcasting并使能：

其中Local Address填写运行Axis Studio软件的windows电脑IP，Destination Address填写运行Mocap api节点的Linux电脑IP。


## 使用方法

运行图形界面控制器:
```bash
cd python_command
python gui_mocap_controller.py
```

界面将显示以下按钮:
- Start Recording: 开始录制动作
- Stop Recording: 停止录制动作
- Clear Log: 清除日志信息
- Exit: 退出程序

## 核心模块

### [mocap_control.py](python_command/mocap_control.py)
动捕设备控制核心模块，负责与MocapApi通信，处理设备连接、命令发送和数据接收。

### [gui_mocap_controller.py](python_command/gui_mocap_controller.py)
图形用户界面模块，提供直观的操作界面和状态显示。

### [config.py](python_command/config.py)
配置文件，包含网络参数和消息类型定义。

## 工作原理

1. 程序启动时初始化MCPApplication并与动捕服务端建立连接
2. 通过UDP协议接收动捕数据
3. 用户通过GUI界面发送开始/停止录制命令
4. 程序处理设备返回的状态信息和错误信息
5. 所有状态信息实时显示在日志区域

## 注意事项

1. 使用前请确保动捕设备已正确连接并运行
2. 配置正确的服务端和客户端IP地址及端口
3. 确保防火墙允许UDP通信
4. 程序运行时不要关闭动捕设备软件

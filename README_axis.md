本示例代码演示了如何通过mocapapi获取Axis Studio的数据。

# 安装并运行
```
cd MocapApi
pip install .
cd ..
python mocap_axis_demo.py
```

## Axis Studio

### 启动*Axis Studio*, 打开一个动作数据文件

此时能看到Axis Studio里的3D模型在运动，如下图所示：

![launch_axis_studio](img/launch_axis_studio.gif)

### 配置 *BVH Broadcasting*

打开设置对话框，选择BVH Broadcasting并使能：

其中Local Address填写运行Axis Studio软件的windows电脑IP，Destination Address填写运行ROS节点的Linux电脑IP。

其余红框部分，需要严格按照图示填写。

![bvh_edit](img/bvh_edit.png)

> 设置页面里，选择“BVH 数据广播”，里面有两个选项：BVH-捕捉和BVH-编辑。BVH-捕捉用于获取实时的动作数据，BVH-编辑用于获取回放录制的动作数据。测试时，请选择BVH-捕捉。
本示例代码演示了如何通过mocapapi获取Hybrid Data Server的数据。

# 安装并运行
```
cd MocapApi
pip install .
cd ..
python mocap_hds_demo.py
```

# 配置Hybrid Data Server输出数据

进入hybrid data server的设置->输出设置

![](img\hds-main.png)

![](img\hds-output.png)

配置如下：

- 轴序XYZ，需要跟示例代码里保持一致 

  ```
  settings.set_bvh_rotation(MCPBvhRotation.XYZ)
  ```

- 选择UDP

- 目标地址输入接收电脑的IP地址，以及端口号（默认为7012）

- 数据类型，根据需要勾选下面的三种常用类型

  - Marker散点：光点的空间坐标
  - 追踪器：光混追踪的6dof
  - 人体BVH：人体骨骼的6dof
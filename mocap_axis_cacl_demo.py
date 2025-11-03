import time
from mocap_api import *


def get_event_type_name(event_type_value):
    """
    Convert event type value to corresponding enum name
    
    Args:
        event_type_value: The numeric event type value
        
    Returns:
        str: The corresponding event type name
    """
    event_type_map = {
        MCPEventType.InvalidEvent: 'InvalidEvent',
        MCPEventType.AvatarUpdated: 'AvatarUpdated',
        MCPEventType.TrackerUpdated: 'TrackerUpdated',
        MCPEventType.AliceIMUUpdated: 'AliceIMUUpdated',
        MCPEventType.AliceRigidbodyUpdated: 'AliceRigidbodyUpdated',
        MCPEventType.AliceTrackerUpdated: 'AliceTrackerUpdated',
        MCPEventType.AliceMarkerUpdated: 'AliceMarkerUpdated',
    }
    return event_type_map.get(event_type_value, f'Unknown({event_type_value})')


class MocapCalcDemo:
    """
    Mocap Calculation Data Demo class for demonstrating how to get Calculation Data through Mocap API
    """
    
    def __init__(self):
        """
        Initialize Mocap Calculation Data Demo instance
        """
        self.app = None
        self.running = False
    
    def start(self, udp_port=7012):
        """
        Start Mocap application and handle event loop
        
        Args:
            udp_port: UDP port number, default is 7012
        """
        # 1. 初始化应用与设置
        self.app = MCPApplication()
        settings = MCPSettings()
        
        # 2. 配置数据广播协议与端口（需与Axis Studio一致）
        settings.set_udp(udp_port)  # 使用UDP协议，端口7012
        settings.set_calc_data()    # 关键配置：指定获取Calculation Data
        
        # 3. 应用设置并连接Axis Studio
        self.app.set_settings(settings)
        
        # 检查连接状态
        success = self.app.open()
        if success:
            print(f"Mocap application initialized successfully, UDP port: {udp_port}")
            print(f"正在接收来自Axis Studio的Calculation Data数据...")
        else:
            print(f"Failed to initialize Mocap application, UDP port: {udp_port}")
            print("请检查：")
            print("1. Axis Studio是否已启动")
            print("2. Calculation Data广播是否已开启")
            print("3. 端口设置是否一致")
            return
        
        self.running = True
        try:
            # 4. 循环获取数据（实时监听Avatar更新事件）
            while self.running:
                evts = self.app.poll_next_event()
                for evt in evts:
                    if evt.event_type == MCPEventType.AvatarUpdated:
                        # 解析角色数据
                        self._handle_calculation_data(evt)
                    else:
                        print('Other events:', get_event_type_name(evt.event_type))
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
        finally:
            self.stop()

    def _handle_calculation_data(self, evt):
        """
        Handle calculation data from avatar
        """
        # 解析角色数据
        avatar = MCPAvatar(evt.event_data.avatar_handle)
        joints = avatar.get_joints()  # 获取所有关节
        
        # 骨骼传感器对应表
        sensor_map = {
            1: "Hips", 2: "RightUpLeg", 3: "RightLeg", 4: "RightFoot",
            5: "LefUpleg", 6: "LeftLeg", 7: "LeftFoot", 8: "RightShoulder",
            9: "RightArm", 10: "RightForeArm", 11: "RightHand", 12: "LeftShoulder",
            13: "LeftArm", 14: "LeftForeArm", 15: "LeftHand", 16: "Head", 17: "Spine2"
        }
        
        # 打印帧分隔线
        print("\n" + "="*60)
        
        for joint in joints:
            joint_name = joint.get_name()
            sensor_module = joint.get_sensor_module()

            # 提取Calculation Data核心数据
            if sensor_module:
                posture = sensor_module.get_posture()        # 姿态四元数
                angular_velocity = sensor_module.get_angular_velocity()  # 角速度
                acceleration = sensor_module.get_accelerated_velocity()  # 加速度

                # 找到对应的骨骼序号
                bone_index = None
                for idx, name in sensor_map.items():
                    if name == joint_name:
                        bone_index = idx
                        break
                
                # 示例：打印数据（实际应用中可发送至机器人/引擎）
                print(f"关节: {joint_name} (序号: {bone_index})")
                print(f"  姿态: {posture}")
                print(f"  角速度: {angular_velocity}")
                print(f"  加速度: {acceleration}")

    def stop(self):
        """
        Close Mocap application
        """
        self.running = False
        if self.app:
            self.app.close()
            print("Mocap application closed")


if __name__ == "__main__":
    # 创建并运行演示实例
    print("=== Mocap Calculation Data Demo ===")
    print("请确保：")
    print("1. Axis Studio中已启用Calculation Data广播")
    print("2. 广播端口与代码中设置一致")
    print("3. Axis Studio正在运行并输出数据")
    print("\n按Ctrl+C停止程序\n")
    
    demo = MocapCalcDemo()
    demo.start()

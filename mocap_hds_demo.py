import time
from mocap_api.mocap_api import *


class MocapHDSDemo:
    """
    Mocap HDS Demo类，用于演示Mocap API的基本功能
    """
    
    def __init__(self):
        """
        初始化Mocap HDS Demo实例
        """
        self.app = None
        self.running = False
    
    def start(self, udp_port=7012):
        """
        启动Mocap应用并处理事件循环
        
        Args:
            udp_port: UDP端口号，默认为7012
        """
        # 初始化Mocap应用
        self.app = MCPApplication()
        settings = MCPSettings()
        settings.set_udp(udp_port)
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)
        self.app.set_settings(settings)
        self.app.open()
        print(f"Mocap应用已初始化，UDP端口: {udp_port}")
        
        # 处理事件循环
        if not self.app:
            print("错误：Mocap应用尚未初始化")
            return
        
        self.running = True
        try:
            while self.running:
                evts = self.app.poll_next_event()
                for evt in evts:
                    if evt.event_type == MCPEventType.AvatarUpdated:
                        self._handle_avatar_data(evt)
                    elif evt.event_type == MCPEventType.RigidBodyUpdated:
                        print('rigid body updated')
                    elif evt.event_type == MCPEventType.AliceTrackerUpdated:
                        self._handle_tracker_data()
                    elif evt.event_type == MCPEventType.AliceMarkerUpdated:
                        self._handle_marker_data()
                    else:
                        print('unknown event')
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("程序被用户中断")
        finally:
            self.stop()

    def _handle_marker_data(self):
        """
        处理标记点数据
        """
        alicehub = MCPAliceHub()
        recv, count = alicehub.get_marker_list()
        if count > 0:
            recv, count1 = alicehub.get_marker_list(count)
            for i in range(count):
                marker_handle = recv[i]
                marker = MCPMarker(marker_handle)
                marker_x, marker_y, marker_z = marker.get_marker_position()
                print(f'marker data : position: {marker_x}, {marker_y}, {marker_z}')
    
    def _handle_tracker_data(self):
        """
        处理追踪器数据
        """
        alicehub = MCPAliceHub()
        recv, count = alicehub.get_PWR_list()
        if count > 0:
            recv, count1 = alicehub.get_PWR_list(count)
            timestamp = alicehub.get_PWR_timestamp()
            for i in range(count):
                PWRHandle = recv[i]
                MCPPWRH = MCPPWR(PWRHandle)
                id = MCPPWRH.get_PWR_id()
                status = MCPPWRH.get_PWR_status()
                position = MCPPWRH.get_PWR_position()
                quaternion = MCPPWRH.get_PWR_quaternion()
                print('tracker data : timestamp',timestamp,'id:', id, 'status:', status, 'position:', position, 'quaternion:', quaternion)

    def _handle_avatar_data(self, evt):
        """
        处理 avatar 事件
        """
        avatar = MCPAvatar(evt.event_data.avatar_handle)
        # 获取并打印时间码信息
        second, nanosecond = avatar.get_avatar_posture_ptp_time()
        print(f" avatar posture ptp time : {second},{nanosecond}")
        joints = avatar.get_joints()  # Get all joint data
        for joint in joints:
            link_name = joint.get_name()  # Get joint name
            position = joint.get_local_position()  # Get joint position
            rotation = joint.get_local_rotation()  # Get joint rotation
            print(f"avatar data : joint: {link_name}, position: {position}, rotation: {rotation}")
   
    def stop(self):
        """
        关闭Mocap应用
        """
        self.running = False
        if self.app:
            self.app.close()
            print("Mocap应用已关闭")

if __name__ == "__main__":
    # 创建并运行演示实例
    demo = MocapHDSDemo()
    print("启动Mocap HDS演示...")
    demo.start()
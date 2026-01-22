from mocap_api import *
from datetime import datetime, time

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


class MocapAxisDemo:
    """
    Mocap Axis Studio Demo class for demonstrating how to get Axis Studio data through Mocap API
    """
    
    def __init__(self):
        """
        Initialize Mocap Axis Studio Demo instance
        """
        self.app = None
        self.running = False  
    
    def start(self, udp_port=7012):
        """
        Start Mocap application and handle event loop
        
        Args:
            udp_port: UDP port number, default is 7012
        """
        # Initialize Mocap application
        self.app = MCPApplication()
        settings = MCPSettings()
        # settings.set_udp(udp_port)
        settings.set_tcp('127.0.0.1',7001)
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)
        self.app.set_settings(settings)
        self.app.open()
        print(f"Mocap application initialized, UDP port: {udp_port}")
        
        self.running = True
        try:
            while self.running:
                evts = self.app.poll_next_event()
                for evt in evts:
                    if evt.event_type == MCPEventType.AvatarUpdated: # avatar bvh(人体BVH)
                        self._handle_avatar_data(evt)
                    else:
                        print('Other events:', get_event_type_name(evt.event_type))
                # time.sleep(0.001)
        except KeyboardInterrupt:
            print("Program interrupted by user")
        finally:
            self.stop()

   
   

    def convert_time_to_datetime(self,hour, minute, second, millisecond):
        """
        将时间分量转换为Python datetime对象
        
        Args:
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            second: 秒 (0-59)
            millisecond: 毫秒 (0-999)
        
        Returns:
            datetime: 当前日期加上给定时间分量的datetime对象
        """
        # 获取当前日期
        now = datetime.now()
        # 创建时间对象
        t = time(hour, minute, second, millisecond * 1000)  # 注意：datetime的microsecond参数需要微秒，所以乘以1000
        # 组合日期和时间
        dt = datetime.combine(now.date(), t)
        return dt
    def _handle_avatar_data(self, evt):
        """
        Handle avatar data
        """
        avatar = MCPAvatar(evt.event_data.avatar_handle)
        # 获取时间分量并格式化为可读时间
        hour, minute, second, millisecond = avatar.get_avatar_posture_time()
        print(f"get_avatar_posture_time(): {self.convert_time_to_datetime(hour, minute, second, millisecond)}")
        joints = avatar.get_joints()  # Get all joint data
        for joint in joints:
            link_name = joint.get_name()  # Get joint name
            position = joint.get_local_position()  # Get joint position
            rotation = joint.get_local_rotation()  # Get joint rotation
            print(f"avatar data : joint: {link_name}, position: {position}, rotation: {rotation}")


    def stop(self):
        """
        Close Mocap application
        """
        self.running = False
        if self.app:
            self.app.close()
            print("Mocap application closed")

if __name__ == "__main__":
    # Create and run demo instance
    demo = MocapAxisDemo()
    print("Starting Mocap Axis Studio demo...") 
    demo.start()
import time
import sys
import os
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


class MocapHDSDemo:
    """
    Mocap Hybrid Data Server Demo class for demonstrating how to get Hybrid Data Server data through Mocap API
    """
    
    def __init__(self):
        """
        Initialize Mocap HDS Demo instance
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
        settings.set_udp(udp_port)
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
                    elif evt.event_type == MCPEventType.AliceTrackerUpdated: # AliceTracker(追踪器)
                        self._handle_tracker_data()
                    elif evt.event_type == MCPEventType.AliceMarkerUpdated: # marker(Marker散点)
                        self._handle_marker_data()
                    elif evt.event_type == MCPEventType.AliceRigidbodyUpdated: # AliceRigidbody(刚体)
                        self._handle_rigid_body_data()
                    elif evt.event_type == MCPEventType.TrackerUpdated: # device(道具)
                        self._handle_device_data(evt)
                    elif self.event_type == MCPEventType.AliceIMUUpdated: # sensor modules(惯性传感器)
                        print('AliceIMUUpdated') # TODO: 处理惯性传感器数据
                    else:
                        print('Other events:', get_event_type_name(evt.event_type))
                # time.sleep(0.001)
        except KeyboardInterrupt:
            print("Program interrupted by user")
        finally:
            self.stop()

    def _handle_marker_data(self):
        """
        Handle marker data
        """
        alicehub = MCPAliceHub()
        recv, count = alicehub.get_marker_list()
        if count > 0:
            recv, count1 = alicehub.get_marker_list(count)
            timestamp = alicehub.get_marker_timestamp()
            for i in range(count):
                marker_handle = recv[i]
                marker = MCPMarker(marker_handle)
                marker_x, marker_y, marker_z = marker.get_marker_position()
                print(f'marker data : timestamp: {timestamp}, position: {marker_x}, {marker_y}, {marker_z}')
    
    def _handle_tracker_data(self):
        """
        Handle tracker data
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
        Handle avatar data
        """
        avatar = MCPAvatar(evt.event_data.avatar_handle)
        # Get and print timecode information
        second, nanosecond = avatar.get_avatar_posture_ptp_time()
        print(f" avatar posture ptp time : {second},{nanosecond}")
        joints = avatar.get_joints()  # Get all joint data
        for joint in joints:
            link_name = joint.get_name()  # Get joint name
            position = joint.get_local_position()  # Get joint position
            rotation = joint.get_local_rotation()  # Get joint rotation
            print(f"avatar data : joint: {link_name}, position: {position}, rotation: {rotation}")

    def _handle_device_data(self, evt):
        """
        Handle device data
        """
        try:
            device = MCPTracker(evt.event_data.tracker_handle)
            device_name = device.get_device_name()
            # device_count = device.get_device_count(evt.event_data.tracker_handle)
            # px,py,pz,pname = device.get_tracker_position()
            # qx,qy,qz,qw,qname = device.get_tracker_rotataion()
            # print(f"device data : position: {px}, {py}, {pz}, {pname}")
            print(f"device data : name: {device_name}")
        except Exception as e:
            print(f"Error handling device data: {e}")

    def _handle_rigid_body_data(self):
        """
        Handle rigid body data
        """
        alicehub = MCPAliceHub()
        recv, count = alicehub.get_rigid_body_list()
        if count > 0:
            recv, count1 = alicehub.get_rigid_body_list(count)
            timestamp = alicehub.get_rigid_body_timestamp()
            for i in range(count):
                right_body_handle = recv[i]
                right_body = MCPRigidBody(right_body_handle)
                # status = right_body.get_status()
                id = right_body.get_id()
                pos = right_body.get_position()
                rot = right_body.get_rotation()
                print('rigid body data : id', id,'timestamp:', timestamp, 'position:', pos, 'rotation:', rot)


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
    demo = MocapHDSDemo()
    print("Starting Mocap HDS demo...")
    demo.start()
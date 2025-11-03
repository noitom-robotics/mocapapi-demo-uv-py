import sys
sys.path.append(r'./MocapApi')

import asyncio
import logging
import threading

from enum import Enum
from pynput.keyboard import Listener
from mocap_api import *

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MsgType(Enum):
    START = 1
    STOP = 2
    RUN_COMMAND = 3
    STATUS = 4
    ERROR = 5
    DATA = 6
    CONNENT_SUCCESS = 7
    SUCCESS = 11

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

class MCPAxisCommandDemo:
    def __init__(self):
        # Initialize current command and running state
        self.current_command = -1  # Current command being executed
        self.connent_key = False   # Connection state flag
        self._running = False      # Running flag
        
        # Create application instance and settings
        self.app = MCPApplication()
        settings = MCPSettings()
        
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)
        settings.SetSettingsUDPEx('10.0.6.51', 7003)  # 客户端IP和端口
        settings.SetSettingsUDPServer('10.0.4.53', 7012)  # 服务端IP和端口
        self.app.set_settings(settings)
        self.app.open()

        self.task = None
        self.loop = None
        self.thread = None

        def run_udp_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.task = self.loop.create_task(self.udp_listener_loop())
            try:
                self.loop.run_forever()
            finally:
                # Finally close the loop
                if self.loop and not self.loop.is_closed():
                    self.loop.close()

                self.loop = None
                self.task = None
                self.thread = None
                self._send_message(MsgType.STATUS, f"UDP thread exited")

        self.thread = threading.Thread(target=run_udp_loop, daemon=True)
        self.thread.start()
        self._send_message(MsgType.STATUS, f"UDP thread started")        
    def _send_message(self, msg_type, message):
        # print(f"{msg_type}: {message}")
        if msg_type == MsgType.ERROR:
            logging.error(message)
        else:
            logging.info(message)

    def get_current_command_title(self):
        # Return the title corresponding to the current command
        if self.current_command == EMCPCommand.CommandStartRecored:
            return 'Start Recored'
        elif self.current_command == EMCPCommand.CommandStopRecored:
            return 'Stop Recored'
        else:
            return 'None'

    def check_current_command(self):
        # Check if the specified command can be executed
        if self.connent_key == False:
            self._send_message(MsgType.ERROR, 'Link failure.')
            return False
        elif self.current_command != -1:
            # If another command is running, prohibit executing other commands
            self._send_message(MsgType.ERROR, f'Pending command {self.get_current_command_title()} is running.')

        return True

    def running_command(self, running_command):
        # Execute specified command
        if self.check_current_command() == True:     
            self.app.queue_command(running_command)  # Execute command
            self.current_command = running_command   # Update current command
            self._send_message(MsgType.STATUS, f'Pending command {self.get_current_command_title()} is running.')

    def handleNotify(self, notifyData):
        # Handle notification events
        if notifyData._notify == MCPEventNotify.Notify_SystemUpdated:
            mcpSystem = MCPSystem(notifyData._notifyHandle)  # Get system information
            self._send_message(MsgType.STATUS, f'MasterInfo : ( Version : {mcpSystem.get_master_version()}, SerialNumber : {mcpSystem.get_master_serial_number()} )')
            self._send_message(MsgType.CONNENT_SUCCESS, 'Connected.')

    def handleResult(self, commandRespond):
        # Handle command result
        command = MCPCommand()
        _commandHandle = commandRespond._commandHandle
        ret_code = command.get_result_code(_commandHandle)
        if ret_code != 0:
            ret_msg = command.get_result_message(_commandHandle)
            self._send_message(MsgType.ERROR, f'ResultCode: {self.get_current_command_title()}, ResultMessage: {ret_msg}')  # Print command execution error message
        else:
            self._send_message(MsgType.SUCCESS, f'{self.get_current_command_title()} done.')  # Print command execution success message    
        command.destroy_command(_commandHandle)  # Destroy command handle
        self.current_command = -1  # Reset current command

    def handleAvatar(self, avatar_handle):
        # Handle avatar update event
        avatar = MCPAvatar(avatar_handle)  # Get avatar data
        joints = avatar.get_joints()  # Get all joint data
        bvh_json = []
        for joint in joints:
            link_name = joint.get_name()  # Get joint name
            position = joint.get_local_position()  # Get joint position
            rotation = joint.get_local_rotation()  # Get joint rotation
            node = {}
            node["bone"] = link_name
            if link_name == "Hips":
                node["offset"] = {"x": position[0], "y": position[1], "z": position[2]}
            node["rotation"] = {"w": rotation[0], "x": rotation[1], "y": rotation[2], "z": rotation[3]}
            bvh_json.append(node)
        bones_json = {"bones": bvh_json}  
        self._send_message(MsgType.DATA, bones_json)


    async def udp_listener_loop(self):
        """Asynchronous update function, processing event loop"""
        self._running = True
        try: 
            while self._running:
                self.connent_key = True
                evts = self.app.poll_next_event()  # Get next event
                for evt in evts:
                    if evt.event_type == MCPEventType.AvatarUpdated:
                        self.handleAvatar(evt.event_data.avatar_handle)    
                    elif evt.event_type == MCPEventType.Notify:
                        self.handleNotify(evt.event_data.notifyData)
                    elif evt.event_type == MCPEventType.CommandReply:
                        if evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Response:
                            self._send_message(MsgType.STATUS, 'MCPReplay_Response')
                        elif evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Running:
                            self._send_message(MsgType.STATUS, 'MCPReplay_Running')
                        elif evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Result:
                            self.handleResult(evt.event_data.commandRespond)
                    else:
                        print('Other events:', get_event_type_name(evt.event_type))

                await asyncio.sleep(0.001)  # Wait 0.1 seconds
        except Exception as e:
            self._send_message(MsgType.ERROR, f"An error occurred: {e}")
        finally:
            self._running = False
    def stop(self):
        """Safely stop all operations"""
        self._running = False
        self.app.close()

    def handleAvatar(self, avatar_handle):
        # Handle avatar update event
        avatar = MCPAvatar(avatar_handle)  # Get avatar data
        joints = avatar.get_joints()  # Get all joint data
        str_data = '{'
        for joint in joints:
            link_name = joint.get_name()  # Get joint name
            position = joint.get_local_position()  # Get joint position
            rotation = joint.get_local_rotation()  # Get joint rotation
            str_data += f'{link_name} : {position}, {rotation}'
        str_data += '}'
        print(f"links_data: {str_data}")  # Print joint data

    async def main_async(self):
        # Main asynchronous function
        main = self
        loop = asyncio.get_event_loop()

        # Keyboard event handler function
        def on_key_press(key):
            try:
                key_name = key.char.lower()
                print(f"Key pressed: {key_name}")
                if key_name == 's':
                    main.running_command(EMCPCommand.CommandStartRecored)
                elif key_name == 'p':
                    main.running_command(EMCPCommand.CommandStopRecored) 
            except AttributeError:
                if key == key.esc:
                    print("ESC key pressed, exiting program")
                    return False  # Exit listener

        # Start keyboard listener
        with Listener(on_press=on_key_press) as listener:
            asyncio.run_coroutine_threadsafe(main.udp_listener_loop(), loop)  # Start event update
            print("Press S to Start Record,  P to Stop Record,press ESC to exit program")
            await loop.run_in_executor(None, listener.join)  # Wait for listener to exit

    def main(self):
        asyncio.run(self.main_async())

if __name__ == '__main__':
    MCPAxisCommandDemo().main()       

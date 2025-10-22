import sys
sys.path.append(r'./3rdparty/MocapApi')

import asyncio
import multiprocessing
import logging
import threading
from mocap_api import *
from config import *

# Set up logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MCPControl:
    def __init__(self, msg_queue: multiprocessing.Queue = None):
        # Initialize current command and running state
        self.current_command = -1  # Current command being executed
        self.connent_key = False   # Connection state flag
        self.msg_queue = msg_queue # Message queue
        self._running = False      # Running flag
        
        # Create application instance and settings
        self.app = MCPApplication()
        settings = MCPSettings()
        
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)
        settings.SetSettingsUDPEx(CLIENT_IP, CLIENT_PORT)
        settings.SetSettingsUDPServer(SERVER_IP, SERVER_PORT)
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
                self.msg_queue.put((MsgType.STATUS, f"POSE thread exited"))

        self.thread = threading.Thread(target=run_udp_loop, daemon=True)
        self.thread.start()
        self.msg_queue.put((MsgType.STATUS, f"POSE thread started"))        
    def _send_message(self, msg_type, message):
        # print(f"{msg_type}: {message}")
        """Send message to message queue"""
        if self.msg_queue:
            self.msg_queue.put((msg_type, message))
        else:
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
                    elif evt.event_type == MCPEventType.RigidBodyUpdated:
                        self._send_message(MsgType.STATUS, 'rigid body updated')
                await asyncio.sleep(0.001)  # Wait 0.1 seconds
        except Exception as e:
            self._send_message(MsgType.ERROR, f"An error occurred: {e}")
        finally:
            self._running = False
    def stop(self):
        """Safely stop all operations"""
        self._running = False
        self.app.close()
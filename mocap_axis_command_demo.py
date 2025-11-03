import asyncio
import threading
import time
import select
import sys
from mocap_api import *

class MCPAxisCommandDemo:
    def __init__(self):
        # Initialize current command and running command status
        self.current_command = -1  # Current command being executed
        self.record_key = False  # Record status flag
        self.connent_key = False  # Connection status flag
        self.app = MCPApplication()  # Create application instance
        settings = MCPSettings()  # Create settings instance
        
        # Configure BVH data format to binary
        settings.set_bvh_data(MCPBvhData.Binary)
        # Enable BVH data transformation
        settings.set_bvh_transformation(MCPBvhDisplacement.Enable)
        # Set rotation order to YZX
        settings.set_bvh_rotation(MCPBvhRotation.YXZ)
        # Configure UDP data transmission address and port
        settings.SetSettingsUDPEx('10.0.4.53', 7012)
        settings.SetSettingsUDPServer('10.0.6.51', 7003)
        
        # Apply configuration to application instance and open connection
        self.app.set_settings(settings)
        self.app.open()

    def get_current_command_title(self):
        # Return the title corresponding to the current command
        if self.current_command == EMCPCommand.CommandStartRecored:
            return 'Start Record'
        elif self.current_command == EMCPCommand.CommandStopRecored:
            return 'Stop Record'
        else:
            return 'None'

    def check_current_command(self, running_command):
        # Check if the specified command can be run
        if self.connent_key == False:
            print('Link failure.')  # Print error message if not connected
            return False
        elif self.current_command != -1:
            # If another command is running, prohibit executing other commands
            print(f'Pending command {self.get_current_command_title()} is running.')
            return False
        # Stop record command needs record to be started first
        elif self.record_key == False and running_command == EMCPCommand.CommandStopRecored:
            print('Please start record command first.')
            return False
        return True

    def running_command(self, running_command):
        # Execute the specified command
        if self.check_current_command(running_command) == True:            
            self.app.queue_command(running_command)  # Execute command
            self.current_command = running_command  # Update current command
            print(f'Pending command {self.get_current_command_title()} is running.')

    def handleResult(self, commandRespond):
        # Handle command results
        command = MCPCommand()
        _commandHandle = commandRespond._commandHandle
        ret_code = command.get_result_code(_commandHandle)
        if ret_code != 0:
            ret_msg = command.get_result_message(_commandHandle)
            print(f'ResultCode: {self.get_current_command_title()}, ResultMessage: {ret_msg}')  # Print command execution error message
        else:
            print(f'{self.get_current_command_title()} done.')  # Print command execution success message
            if self.current_command == EMCPCommand.CommandStartRecored:
                self.record_key = True
            elif self.current_command == EMCPCommand.CommandStopRecored:
                self.record_key = False
        command.destroy_command(_commandHandle)  # Destroy command handle
        self.current_command = -1  # Reset current command

    def handleRunning(self, commandRespond):
        # Handle command running status
        print(f'{self.get_current_command_title()} is running...')

    async def update(self):
        try: 
            # Asynchronous update function to handle event loop
            while True:
                evts = self.app.poll_next_event()  # Get next event
                for evt in evts:
                    self.connent_key = True
                    if evt.event_type == MCPEventType.CommandReply:
                        if evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Running:
                            self.handleRunning(evt.event_data.commandRespond)
                        elif evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Result:
                            self.handleResult(evt.event_data.commandRespond)
                await asyncio.sleep(0.1)  # Wait for 0.1 seconds
        except Exception as e:
            print(f"An error occurred: {e}")    

    async def main_async(self):
        # Main asynchronous function
        main = self
        loop = asyncio.get_event_loop()
        
        # Create a flag to control the input thread
        stop_event = threading.Event()
        
        # Input handling function
        def handle_input():
            print("Press R to Start Record, S to Stop Record, Q to exit program")
            while not stop_event.is_set():
                try:
                    # Check if input is available
                    if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.readline().strip().lower()
                        if key == 'r':
                            print("R key pressed")
                            main.running_command(EMCPCommand.CommandStartRecored)
                        elif key == 's':
                            print("S key pressed")
                            main.running_command(EMCPCommand.CommandStopRecored)
                        elif key == 'q':
                            print("Q key pressed, exiting program")
                            stop_event.set()
                            break
                except Exception as e:
                    print(f"Input error: {e}")
                    break
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.1)
        
        # Start the input handling thread
        input_thread = threading.Thread(target=handle_input)
        input_thread.daemon = True
        input_thread.start()
        
        # Start event update
        update_task = asyncio.create_task(main.update())
        
        # Wait until stop event is set
        while not stop_event.is_set():
            await asyncio.sleep(0.1)
        
        # Cancel the update task when exiting
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
        
        print("Program exited")

    def main(self):
        asyncio.run(self.main_async())

if __name__ == '__main__':
    MCPAxisCommandDemo().main()
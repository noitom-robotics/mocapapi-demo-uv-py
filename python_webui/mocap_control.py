import sys
sys.path.append(r'./3rdparty/MocapApi')

import asyncio
import multiprocessing
import logging
import threading
from mocap_api import *
from web_config import *

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MCPControl:
    def __init__(self, msg_queue: multiprocessing.Queue = None):
        # 初始化当前命令和运行状态
        self.current_command = -1  # 当前正在执行的命令
        self.capture_key = False   # 捕获状态标志
        self.connent_key = False   # 连接状态标志
        self.msg_queue = msg_queue # 消息队列
        self._running = False      # 运行标志
        
        # 创建应用实例和设置
        self.app = MCPApplication()
        settings = MCPSettings()
        
        # 配置BVH数据格式为二进制
        settings.set_bvh_data(MCPBvhData.Binary)
        # 启用BVH数据转换
        settings.set_bvh_transformation(MCPBvhDisplacement.Enable)
        # 设置旋转顺序为YZX
        settings.set_bvh_rotation(MCPBvhRotation.XYZ)
        # 配置UDP数据传输地址和端口
        settings.SetSettingsUDPEx(CLIENT_IP, CLIENT_PORT)
        settings.SetSettingsUDPServer(SERVER_IP, SERVER_PORT)
        
        # 应用配置到应用实例并打开连接
        self.app.set_settings(settings)
        self.app.open()

        self.task = None
        self.loop = None
        self.thread = None

        self.current_step = ""
        self.current_state = 0
        self.transform_data_key = False

        def run_udp_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.task = self.loop.create_task(self.udp_listener_loop())
            try:
                self.loop.run_forever()
            finally:
                # 最后关闭 loop
                if self.loop and not self.loop.is_closed():
                    self.loop.close()

                self.loop = None
                self.task = None
                self.thread = None
                self.msg_queue.put((MsgType.STATUS, f"POSE线程已退出"))

        self.thread = threading.Thread(target=run_udp_loop, daemon=True)
        self.thread.start()
        self.msg_queue.put((MsgType.STATUS, f"POSE线程已启动"))        
    def _send_message(self, msg_type, message):
        """向消息队列发送消息"""
        if self.msg_queue:
            self.msg_queue.put((msg_type, message))
        else:
            if msg_type == MsgType.ERROR:
                logging.error(message)
            else:
                logging.info(message)
    def get_current_command_title(self):
        # 返回当前命令对应的标题
        if self.current_command == EMCPCommand.CommandStartCapture:
            return 'Start Capture'
        elif self.current_command == EMCPCommand.CommandStopCapture:
            return 'Stop Capture'
        elif self.current_command == EMCPCommand.CommandCalibrateMotion:
            return 'Calibrate Motion'
        elif self.current_command == EMCPCommand.CommandResumeOriginalHandsPosture:
            return 'Resume Hands'
        elif self.current_command == EMCPCommand.CommandClearZeroMotionDrift:
            return 'Reset 0 Motion Drift'
        elif self.current_command == EMCPCommand.CommandResumeOriginalPosture:
            return 'Resume Body'
        elif self.current_command == EMCPCommand.CommandZeroPosition:
            return 'Zero Position'
        else:
            return 'None'

    def check_current_command(self, running_command):
        # 检查指定命令是否可以运行
        if self.connent_key == False:
            self._send_message(MsgType.ERROR, 'Link failure.')
            return False
        elif self.current_command != -1:
            # 如果有其他命令正在运行，禁止执行其他命令
            self._send_message(MsgType.ERROR, f'Pending command {self.get_current_command_title()} is running.')
            return False
        # 除开始捕获外的命令需要先启动捕获
        elif self.capture_key == False and running_command != EMCPCommand.CommandStartCapture:
            self._send_message(MsgType.ERROR, 'Please start capture command first.')
            return False
        return True

    def running_command(self, running_command):
        # 执行指定命令
        if self.check_current_command(running_command) == True:            
            self.app.queue_command(running_command)  # 执行命令
            self.current_command = running_command   # 更新当前命令
            self._send_message(MsgType.STATUS, f'Pending command {self.get_current_command_title()} is running.')

    def handleNotify(self, notifyData):
        # 处理通知事件
        if notifyData._notify == MCPEventNotify.Notify_SystemUpdated:
            mcpSystem = MCPSystem(notifyData._notifyHandle)  # 获取系统信息
            self._send_message(MsgType.STATUS, f'MasterInfo : ( Version : {mcpSystem.get_master_version()}, SerialNumber : {mcpSystem.get_master_serial_number()} )')
            self._send_message(MsgType.CONNENT_SUCCESS, 'Connected.')
    def handleResult(self, commandRespond):
        # 处理命令结果
        command = MCPCommand()
        _commandHandle = commandRespond._commandHandle
        ret_code = command.get_result_code(_commandHandle)
        if ret_code != 0:
            ret_msg = command.get_result_message(_commandHandle)
            self._send_message(MsgType.ERROR, f'ResultCode: {self.get_current_command_title()}, ResultMessage: {ret_msg}')  # 打印命令执行错误消息
        else:
           
            if self.current_command == EMCPCommand.CommandCalibrateMotion:
                self._send_message(MsgType.CALIBRATION_FINISH,f'{self.get_current_command_title()} done.')
            elif self.current_command == EMCPCommand.CommandStopCapture:
                self.capture_key = False
                self._send_message(MsgType.SUCCESS, f'{self.get_current_command_title()} done.')
            elif self.current_command == EMCPCommand.CommandStartCapture:    
                self._send_message(MsgType.START_CAPTURE, f'{self.get_current_command_title()} done.')
            else:
                self._send_message(MsgType.SUCCESS, f'{self.get_current_command_title()} done.')  # 打印命令执行成功消息    
        command.destroy_command(_commandHandle)  # 销毁命令句柄
        self.current_command = -1  # 重置当前命令

    def handleRunning(self, commandRespond):
        # 处理校准进度
        _calibrateProgressHandle = MCPCommand().get_progress(commandRespond._commandHandle)
        progressHandle = MCPCalibrateMotionProgress(_calibrateProgressHandle)
        count = progressHandle.get_count_of_support_poses()

        str_poses = "Support poses:"
        for i in range(count):
            name = progressHandle.get_name_of_support_poses(i)
            str_poses += name
            if i + 1 != count:
                str_poses += ", "
        str_poses += " : "     
        result_progress = 0
        # 获取校准步骤和校准名称
        result_current_step, result_p_name = progressHandle.get_step_current_pose()        
        if result_current_step == MCPCalibrateMotionProgressStep.CalibrateMotionProgressStep_Countdown:
            # 获取校准倒计时
            result_countdown, result_p_name = progressHandle.get_countdown_current_pose()
            str_poses += (f"Calibration-({result_p_name})-Countdown {result_countdown}.")
            if self.current_state == 0:
             self.current_state = 1
             self._send_message(MsgType.CALIBRATION_STEP, (result_p_name, self.current_state, result_progress))
        elif result_current_step == MCPCalibrateMotionProgressStep.CalibrateMotionProgressStep_Progress:
            # 获取校准进度
            result_progress, result_p_name = progressHandle.get_progress_current_pose()
            str_poses += (f"Calibration-({result_p_name})-Progress {result_progress}.")    
            if self.current_step != result_p_name:
                self._send_message(MsgType.CALIBRATION_STEP, (result_p_name, 0, result_progress))
                self.current_step = result_p_name
                self.current_state = 0       
        elif result_current_step == MCPCalibrateMotionProgressStep.CalibrateMotionProgressStep_Prepare:
            str_poses += (f"Calibration-({result_p_name}) is preparing.")
        else:
            str_poses += (f'Calibration-Unknown({result_current_step}) is running.')

        

        if result_progress == 100:
            self._send_message(MsgType.CALIBRATION_STEP, (result_p_name, 0, result_progress))

    def transform_data(self):
        self.transform_data_key = not self.transform_data_key
        self._send_message(MsgType.SUCCESS, "3D Data" if not self.transform_data_key else "joint Data")
    def handle3DAvatar(self, avatar_handle):
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
        """异步更新函数，处理事件循环"""
        self._running = True
        try: 
            while self._running:
                evts = self.app.poll_next_event()  # 获取下一个事件
                for evt in evts:
                    self.connent_key = True
                    if evt.event_type == MCPEventType.AvatarUpdated:
                        if self.current_command != EMCPCommand.CommandCalibrateMotion and self.current_command == -1:
                            self.capture_key = True
                            if self.transform_data_key:
                                self.handleAvatar(evt.event_data.avatar_handle)
                            else:
                                self.handle3DAvatar(evt.event_data.avatar_handle)    
                    elif evt.event_type == MCPEventType.Notify:
                        self.handleNotify(evt.event_data.notifyData)
                    elif evt.event_type == MCPEventType.CommandReply:
                        if evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Response:
                            self._send_message(MsgType.STATUS, 'MCPReplay_Response')
                        elif evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Running:
                            self.handleRunning(evt.event_data.commandRespond)
                        elif evt.event_data.commandRespond._replay == MCPReplay.MCPReplay_Result:
                            self.handleResult(evt.event_data.commandRespond)
                    elif evt.event_type == MCPEventType.RigidBodyUpdated:
                        self._send_message(MsgType.STATUS, 'rigid body updated')
                await asyncio.sleep(0.001)  # 等待0.1秒
        except Exception as e:
            self._send_message(MsgType.ERROR, f"An error occurred: {e}")
        finally:
            self._running = False
    def stop(self):
        """安全停止所有操作"""
        self._running = False
        self.app.close()
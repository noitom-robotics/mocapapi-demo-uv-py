import sys
sys.path.append(r'./3rdparty/MocapApi')
sys.path.append(r'./3rdparty/robot-retargeting')
from mocap_control import MCPControl
from mocap_api import MCPAvatar
import sys
from robot_retargeting import *
import multiprocessing
import logging
from mocap_api import *
from web_config import *

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#
class MCPDirect(MCPControl):
    def __init__(self,msg_queue: multiprocessing.Queue):
        super().__init__(msg_queue)

    
    def handleAvatar(self, avatar_handle):
        # Handle avatar update event
        avatar = MCPAvatar(avatar_handle)  # Get avatar data
        joints = avatar.get_joints()
        for joint in joints:
            name = joint.get_name()
            tag = joint.get_tag()
            local_position = joint.get_local_position()
            local_rotation = joint.get_local_rotation()
            print(f"Joint: {name}, Tag: {tag}, Local Position: {local_position}, Local Rotation: {local_rotation}")
   

class MCPProcess(multiprocessing.Process):
    def __init__(self, msg_queue: multiprocessing.Queue, command_queue: multiprocessing.Queue):
        super().__init__()
        self.msg_queue = msg_queue
        self.command_queue = command_queue
        self.mcp_control = None

    def run(self):
        try:
            self.mcp_control = MCPDirect(self.msg_queue)
            self._process_commands()
        except Exception as e:
            logging.error(f"MCPProcess 运行异常: {str(e)}")
            self.msg_queue.put((MsgType.ERROR, f"MCPProcess 运行异常: {str(e)}"))
        finally:
            self._cleanup()
            logging.info("MCPProcess 已退出")
            self.msg_queue.put((MsgType.STATUS, "MCPProcess 已退出"))

    def _process_commands(self):
        """处理命令队列中的命令"""
        while True:
            try:
                # 带超时的队列获取，避免永久阻塞
                msg = self.command_queue.get(timeout=2.0)
                command, *args = msg
                if command == MsgType.STOP:
                    break
                elif command == MsgType.DATA:
                    self.mcp_control.transform_data()
                elif command == MsgType.RUN_COMMAND:
                    cmd = args[0]
                    self.mcp_control.running_command(cmd)
            except multiprocessing.queues.Empty:
                # 队列为空，继续循环
                continue
            except Exception as e:
                logging.error(f"MCPProcess 处理命令异常: {str(e)}")
                self.msg_queue.put((MsgType.ERROR, f"MCPProcess 命令处理错误: {str(e)}"))   

    def _cleanup(self):
        """清理资源"""
        if self.mcp_control:
            try:
                self.mcp_control.stop()
            except Exception as e:
                logging.error(f"MCPProcess 清理异常: {str(e)}")

    def set_affinity(self, cpu_id: int):
        """设置进程CPU亲和性"""
        try:
            import psutil
            p = psutil.Process()
            p.cpu_affinity([cpu_id])
            self.msg_queue.put((MsgType.STATUS, f"MCPProcess 设置进程运行在CPU {cpu_id}上"))
        except Exception as e:
            logging.warning(f"设置CPU亲和性失败: {str(e)}")

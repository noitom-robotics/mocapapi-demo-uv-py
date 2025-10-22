from enum import Enum

SERVER_IP = '10.42.0.202'
SERVER_PORT = 8080
CLIENT_IP = '10.42.0.101'
SERVER_URL = 'http://' + SERVER_IP 
CLIENT_PORT = 8002
BVH_HEADER_FILE = "config/bvh_header.json"
WEB_THREE_HTML = 'web/three_fbx_viewer.html'


# 动捕标定信息
PNLINK_CALIB_INFO = {
    "V": ["VB-Pose", "VB-Pose"],
    "P": ["P-Pose", "P-Pose"],
    "T": ["T-Pose", "手臂平举,掌心向下."],
    "A": ["A-Pose", "手臂竖直朝下,勿弯曲,双脚平行与肩同宽."],
    "F": ["F-Pose", "向前自然走出2-3步,转身返回起点A-Pose站立."]
}

PNLINK_CALIB_STEP = [
    ["V", "VB-Pose"],
    ["P", "P-Pose"],
    ["T", "T-Pose"],
    ["A", "A-Pose"],
    ["F", "F-Pose"]
]

class MsgType(Enum):
    START = 1
    STOP = 2
    RUN_COMMAND = 3
    STATUS = 4
    ERROR = 5
    DATA = 6
    CONNENT_SUCCESS = 7
    CAPTURE_SUCCESS = 8
    CALIBRATION_STEP = 9
    CALIBRATION_FINISH = 10
    SUCCESS = 11
    START_CAPTURE = 12
    CALIBRATION_START = 13
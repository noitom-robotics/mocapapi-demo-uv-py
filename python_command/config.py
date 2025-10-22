from enum import Enum

SERVER_IP = '192.168.66.134'
SERVER_PORT = 7003
CLIENT_IP = '192.168.66.78'
CLIENT_PORT = 7012

class MsgType(Enum):
    START = 1
    STOP = 2
    RUN_COMMAND = 3
    STATUS = 4
    ERROR = 5
    DATA = 6
    CONNENT_SUCCESS = 7
    SUCCESS = 11
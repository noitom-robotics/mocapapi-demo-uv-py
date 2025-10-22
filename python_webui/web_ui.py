import json
import logging
import os
import threading
import time
from collections import deque
from pathlib import Path

import multiprocessing
from nicegui import ui, app

# 假设这些类和模块已经正确实现
from mocap_api import EMCPCommand
from config import *
from mocap_direct import MCPProcess


class WebControlPanel:
    def __init__(self):
        # 服务器配置
        self.bvh_header_file = os.path.join(os.path.dirname(__file__), BVH_HEADER_FILE)
        # UI组件引用
        self.pnmocap_calibration_dialog = None
        self.step_countdown_label = None
        self.step_countdown_label_count = 3
        self.step_countdown_timer = None
        self.web3d_dialog = None
        self.web3d_timer = None
        self.message_queue = deque(maxlen=5)
        self.bvh_header = None
        self.card_mask = None
        self.capture_key = False

        self._queue_thread = None  # 重定向计算线程
        self._queue_running = threading.Event()  # 线程运行标志
       

        # 创建一个队列对象
        self.msg_queue = multiprocessing.Queue()
        self.mocap_queue = multiprocessing.Queue()
        self.mocap_process = MCPProcess(self.msg_queue, self.mocap_queue)
        self.mocap_process.start()
        
        # 存储设备状态UI组件的引用
        self.device_status_components = {}
        
        self._queue_thread = threading.Thread(target=self._message_loop, daemon=True)
        self._queue_running.set()
        self._queue_thread.start()

         # 创建一个线程安全的事件队列
        self._ui_event_queue = []
        self._ui_event_lock = threading.Lock()

        self.transform_data_button = None
        self.transform_data_key = False
        
        # 启动定时器检查事件队列
        ui.timer(0.05, self._process_ui_events)
        # 启动定时器检查3D预览
        ui.timer(0.02, self.update_web_3d)

    def init_ui(self):
        """初始化UI界面"""
        with ui.column().classes('w-full items-center p-8 bg-gray-50'):
            ui.label('PN-Link设置面板').classes('text-2xl font-bold mb-8')
            with ui.card().classes('w-full max-w-[1000px] p-6 shadow-lg bg-white rounded-xl'):
                with ui.column().classes('gap-4'):
                    ui.label('状态').classes('text-xl font-semibold mb-2')
                    self.connection_status_row()
            with ui.element('div').classes(
                    'absolute inset-0 z-10 flex flex-col justify-center items-center rounded-xl'
            ).style('background-color: rgba(0, 0, 0, 0.7); display: flex') as self.card_mask:    # flex none
                ui.spinner(size='lg')
                ui.label('请稍候...').classes('text-white text-lg mt-2')

            with ui.card().classes('w-full max-w-[1000px] p-6 shadow-lg bg-white rounded-xl'):
                with ui.column().classes('gap-4'):
                    with ui.row().classes('gap-4'):
                        ui.button('Start Capture', on_click=self.show_pnmocap_connect)                        
                        ui.button('Stop Capture', on_click=lambda: self.running_command(EMCPCommand.CommandStopCapture))

                    with ui.row().classes('gap-4'):
                        ui.button('calibrate', on_click=self.show_pnmocap_calibration)
                        ui.button('Resume Hands', on_click=lambda: self.running_command(EMCPCommand.CommandResumeOriginalHandsPosture))
                        ui.button('Reset 0 Motion Drift', on_click=lambda: self.running_command(EMCPCommand.CommandClearZeroMotionDrift))
                        ui.button('Resume Body', on_click=lambda: self.running_command(EMCPCommand.CommandResumeOriginalPosture))
                        ui.button('Zero Position', on_click=lambda: self.running_command(EMCPCommand.CommandZeroPosition))

                    with ui.row().classes('gap-4'):
                        self.transform_data_button = ui.button('切换数据输出3D Data', on_click=self.transform_data)
                        ui.button('PN-Link设置', on_click=lambda: ui.run_javascript('window.open("'+SERVER_URL+'", "_blank")'))
                        ui.button('骨骼信息', on_click=self.show_skeleton_info)
            self.init_3d_preview()


    def init_3d_preview(self):
        """初始化3D预览区域"""
        with ui.card().classes('w-full max-w-[1000px] p-6 shadow-lg bg-white rounded-xl mt-8'):
            ui.label('3D 预览').classes('text-xl font-semibold mb-4')
            with ui.element('div').classes('relative w-full h-[720px] overflow-hidden'):
                ui.html("""
                <div id="three-container" style="width:100%; height:100%; position:absolute; inset:0; z-index:0;"></div>
                """)

        three_html = os.path.join(os.path.dirname(__file__), WEB_THREE_HTML)
        with open(three_html, 'r') as f:
            html_code = f.read()
        ui.add_body_html(html_code)    
    
    def connection_status_row(self):
        """创建设备状态行"""
        base_color = 'red'
        icon_name = 'cancel'

        with ui.column().classes('w-full gap-1'):
            with ui.row().classes('items-center justify-between w-full').style('min-width: 600px; height: 36px;'):
                with ui.row().classes('items-center gap-2'):
                    self.icon = ui.icon(icon_name, color=base_color)
                    self.label = ui.label('Mocap 动捕设备：未连接').style(f'color: {base_color}')        
            
    def transform_data(self):
        self.mocap_queue.put((MsgType.DATA, "DATA"))
        
        if not self.transform_data_key:
            self.transform_data_button.text = '切换数据输出Joint Data'
        else:
            self.transform_data_button.text = '切换数据输出3D Data' 
        self.transform_data_key = not self.transform_data_key     
    def running_command(self, running_command):
        """运行命令"""
        self.mocap_queue.put((MsgType.RUN_COMMAND, running_command))

    def show_msg_dialog(self, msg_text, is_error=True):
        """显示日志或错误提示框"""
        with ui.dialog() as msg_dialog:
            with ui.card().classes('bg-red-100 w-[400px] h-[200px] flex flex-col relative' if is_error else 'w-[400px] h-[200px] flex flex-col relative'):
                # 右上角关闭按钮
                with ui.element('div').classes('absolute top-0 right-0 p-2'):
                    close_icon = ui.icon('close').classes('cursor-pointer text-xl hover:text-gray-600')
                    close_icon.on('click', msg_dialog.close)

                ui.label('提示信息' if not is_error else '错误信息').classes('text-xl font-bold')
                ui.label(msg_text).classes('text-2xl font-bold mb-6 text-center' if is_error else 'text-2xl font-bold mb-6 text-center text-green-600')
        
        msg_dialog.open()


    def show_pnmocap_connect(self):
        global pnmocap_connect_dialog
        with ui.dialog() as pnmocap_connect_dialog:
            with ui.card().classes('w-[800px] items-center mx-auto').style('max-width: none'):  # mx-auto 让卡片水平居中
                # 关闭按钮（右上角）
                with ui.row().classes('w-full justify-end'):
                    ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click',
                                                                                                        lambda: pnmocap_connect_dialog.close())

                ui.label(f'Mocap动捕设备连接').classes('text-2xl font-bold mb-0 text-center')
                ui.label('点“开始连接”，并保持“站立”或“坐姿”状态15秒').classes('text-lg mb-0 text-center')

                global countdown_label_count, countdown_label
                with ui.element('div').classes('relative w-[600px] h-[500px] mb-0'):
                    ui.image('/res/image/pnmocap_connect.jpg').classes('w-full h-full object-contain')
                    countdown_label = ui.label('').classes(
                        'absolute bottom-4 right-4 text-gray-400 text-[80px] font-semibold drop-shadow-lg '
                        'pointer-events-none select-none'
                    )
                # 居中按钮
                with ui.row().classes('justify-center mt-0'):
                    connect_button = ui.button('开始连接', on_click=lambda: (self.running_command(EMCPCommand.CommandStartCapture), connect_button.set_visibility(False))) \
                        .classes('bg-blue-500 text-white text-xl px-6 py-3 rounded-xl shadow-md hover:bg-blue-600')

        pnmocap_connect_dialog.open()    

    

    def start_pnmocap_connect(self):        
        global countdown_timer, countdown_label_count, countdown_label
        countdown_label_count = 16
        countdown_timer = ui.timer(1.0, lambda: self.update_countdown(self.pnmocap_connect_end))

    def pnmocap_connect_end(self):
        global pnmocap_connect_dialog
        pnmocap_connect_dialog.clear()
        with pnmocap_connect_dialog:
            with ui.card().classes('w-[600px] items-center mx-auto'):
                # 关闭按钮（右上角）
                with ui.row().classes('w-full justify-end'):
                    ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click', lambda: pnmocap_connect_dialog.close())

                # 成功提示
                ui.label(f'Mocap 连接完成！').classes('text-2xl font-bold mb-6 text-center text-green-600')
                # ui.image('/res/image/pnmocap_calib_success.jpg').classes('w-32 h-32 object-contain mb-6')

                # 确认按钮
                ui.button('确认').classes('bg-green-500 text-white w-32').on('click', lambda: pnmocap_connect_dialog.close())
    def show_pnmocap_calibration_finish(self):
        """显示动捕校准完成"""
        self.pnmocap_calibration_dialog.clear()

        with self.pnmocap_calibration_dialog:
            with ui.card().classes('w-[600px] items-center mx-auto'):
                # 关闭按钮（右上角）
                with ui.row().classes('w-full justify-end'):
                    ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click', lambda: self.pnmocap_calibration_dialog.close())

                # 成功提示
                ui.label(f'Mocap 校准完成！').classes('text-2xl font-bold mb-6 text-center text-green-600')

                # 确认按钮
                ui.button('确认').classes('bg-green-500 text-white w-32').on('click', lambda: self.pnmocap_calibration_dialog.close())    

    
            

    def update_device_status(self):
        """更新设备状态"""
        if self.icon.name == 'cancel':
            self.card_mask.style('display: none')

            # 更新每个设备的状态图标和标签
            self.icon.name = 'check_circle' 
            self.icon.props('color="green"')
            self.label.text = 'Mocap 动捕设备：已连接'
            self.label.style(f'color: "green"')
        
        js_code = """
                if (document.getElementById('three-container') && document.getElementById('three-container').innerHTML.trim() == '') {
                    waitForContainer();
                }
            """
        ui.run_javascript(js_code)

    def update_countdown(self,end_callback = None):
        global countdown_label_count, countdown_label, countdown_timer
        countdown_label_count -= 1
        if countdown_label_count >= 1:
            countdown_label.set_text(str(countdown_label_count))
        else:
            countdown_label.set_text('')
            countdown_timer.active = False
            if end_callback:
                end_callback()
    def update_step_countdown(self):
        """更新倒计时"""
        self.step_countdown_label_count -= 1
        if self.step_countdown_label_count >= 1:
            self.step_countdown_label.set_text(str(self.step_countdown_label_count))
        else:
            self.step_countdown_label.set_text('')
            self.step_countdown_timer.active = False            
    def update_pnmocap_calib_timer(self):
        global calibration_seconds, calibration_timer_label
        calibration_seconds += 1
        minutes = calibration_seconds // 60
        seconds = calibration_seconds % 60
        calibration_timer_label.text = f'已用时: {minutes:02d}:{seconds:02d}'

    def show_pnmocap_calibration_step(self, step_info):
        mStep, mState, mProgress = step_info
        mStep = mStep[0]
        """显示动捕校准步骤"""
        if mProgress == 100:
            if mStep == "F":
                self.pnmocap_calibration_dialog.clear()  # 清空之前内容
                with self.pnmocap_calibration_dialog:
                    with ui.card().classes('w-[600px] items-center mx-auto'):
                        ui.label(f'正在计算校准结果(1-3分钟)...').classes('text-2xl font-bold mb-6 text-center text-green-600')
                        global calibration_timer, calibration_seconds, calibration_timer_label
                        calibration_timer_label = ui.label('已用时: 00:00').classes('text-lg font-mono text-center text-gray-600')
                        calibration_seconds = 0
                        calibration_timer = ui.timer(1.0, self.update_pnmocap_calib_timer)
            return

        self.pnmocap_calibration_dialog.clear()  # 清空之前内容
        with self.pnmocap_calibration_dialog:
            with ui.card().classes('w-[600px] h-[500px] items-center mx-auto'):
                ui.label(PNLINK_CALIB_INFO[mStep][0]).classes('text-2xl font-bold text-center mb-2')
                ui.label(PNLINK_CALIB_INFO[mStep][1]).classes('text-base text-gray-600 text-center mb-4')
                if mState == 1:
                    with ui.element('div').classes('relative w-64 h-64 mb-4'):
                        ui.image(f'/res/image/pnmocap_calib_step_{mStep}.jpg').classes('w-64 h-64 object-contain mb-4')
                        # 倒计时大数字
                        self.step_countdown_label = ui.label('').classes(
                            'absolute bottom-0 right-3 text-white/60 text-[64px] font-semibold drop-shadow-lg '
                            'pointer-events-none select-none'
                        )
                    # 启动异步倒计时
                    self.step_countdown_label_count = 4
                    self.step_countdown_timer = ui.timer(1.0, lambda: self.update_step_countdown())
                else:
                    # 当前步骤大图
                    ui.html(f'''
                    <video width="300" autoplay muted playsinline onended="this.pause();">
                      <source src="/res/video/pnmocap_calib_step_{mStep}.mp4" type="video/mp4">
                      Your browser does not support the video tag.
                    </video>
                    ''')
    def show_pnmocap_calibration(self):
        """显示动捕校准对话框"""
        with ui.dialog() as self.pnmocap_calibration_dialog:
            with ui.card().classes('w-[800px] items-center mx-auto').style('max-width: none'):
                # 关闭按钮（右上角）
                with ui.row().classes('w-full justify-end'):
                    ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click', lambda: self.pnmocap_calibration_dialog.close())

                ui.label(f'Mocap动捕设备校准流程').classes('text-2xl font-bold mb-4 text-center')
                ui.label('请先“立正”保持静止10秒,然后按以下步骤开始校准.').classes('text-lg mb-4 text-center')

                # 两行图片，每行两个
                for row in range(2):
                    with ui.row().classes('justify-center gap-8 mb-4'):  # 中间对齐+间距
                        for col in range(3):
                            step = row * 3 + col
                            if step > 4:
                                break
                            with ui.column().classes('items-center'):
                                ui.html(f'''
                                <video width="200" autoplay muted playsinline loop>
                                  <source src="/res/video/pnmocap_calib_step_{PNLINK_CALIB_STEP[step][0]}.mp4" type="video/mp4">
                                  Your browser does not support the video tag.
                                </video>
                                ''')
                                ui.label(f'步骤{step+1}: {PNLINK_CALIB_STEP[step][1]}').classes('text-sm text-center')

                # 居中按钮
                with ui.row().classes('justify-center mt-6'):
                    ui.button('开始校准', on_click=lambda: self.start_pnmocap_calibration()) \
                        .classes('bg-blue-500 text-white text-xl px-6 py-3 rounded-xl shadow-md hover:bg-blue-600')

        self.pnmocap_calibration_dialog.open()


    def start_pnmocap_calibration(self):
        self.pnmocap_calibration_dialog.clear()  # 清空之前内容
        mStep = "V"
        with self.pnmocap_calibration_dialog:
            with ui.card().classes('w-[600px] items-center mx-auto'):
                # # 关闭按钮
                # with ui.row().classes('w-full justify-end'):
                #     ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click', lambda: pnmocap_calibration_dialog.close())

                ui.label(PNLINK_CALIB_INFO[mStep][0]).classes('text-2xl font-bold text-center mb-2')
                ui.label(PNLINK_CALIB_INFO[mStep][1]).classes('text-base text-gray-600 text-center mb-4')

                with ui.element('div').classes('relative w-64 h-64 mb-4'):
                    ui.image(f'/res/image/pnmocap_calib_step_{mStep}.jpg').classes('w-64 h-64 object-contain mb-4')
                    # 倒计时大数字
                    global countdown_label_count, countdown_label
                    countdown_label = ui.label('').classes(
                        'absolute bottom-0 right-3 text-white/60 text-[64px] font-semibold drop-shadow-lg '
                        'pointer-events-none select-none'
                    )
                # 居中按钮
                with ui.row().classes('justify-center mt-6'):
                    ui.button('开始校准', on_click=lambda: self.running_command(EMCPCommand.CommandCalibrateMotion)) \
                        .classes('bg-blue-500 text-white text-xl px-6 py-3 rounded-xl shadow-md hover:bg-blue-600')   

    def show_skeleton_info(self):
        log_text = Path(self.bvh_header_file).read_text() if Path(self.bvh_header_file).exists() else '无骨骼信息。 '

        with ui.dialog() as dialog:
            with ui.card().classes('min-w-[70vh] h-[90vh]').style('max-width: none'):
                with ui.row().classes('w-full justify-end'):
                    ui.icon('close').classes('cursor-pointer text-gray-500 hover:text-black text-3xl').on('click', lambda: dialog.close())

                with ui.element('div').classes('overflow-y-scroll h-full bg-gray-100 p-2 rounded w-full'):
                    ui.code(log_text, language='json').classes('whitespace-pre-wrap text-sm w-full')  # 保留换行
        dialog.open()

    def update_web_3d(self):
        """更新3D视图"""
        if len(self.message_queue) > 0:
            latest = self.message_queue[-1]
            ui.run_javascript(f'window.updateBoneRotations({json.dumps(latest)});')

    def init_bvh_header(self, file_name):
        """初始化BVH头部信息"""
        with open(file_name, 'r', encoding='utf-8') as f:
            bvh_header = json.load(f)
            if (len(bvh_header["bones"]) == 0):
                print("error json:", file_name)
            return bvh_header

    def _message_loop(self):
        """独立线程处理消息队列"""
        while self._queue_running.is_set():
            try:
                if not self.msg_queue.empty():
                    msg = self.msg_queue.get(timeout=1)  # 阻塞1秒后超时
                    command, *args = msg
                    #print(f"消息: {command}: {args}")
                    if  command == MsgType.STATUS:
                        print(f"通知消息: {command}: {args}")
                    else:    
                         # 将 UI 操作添加到事件队列
                        with self._ui_event_lock:
                            self._ui_event_queue.append((self.process_message, (command, args)))
                else:
                    time.sleep(0.01)  # 队列空时短暂休眠
            except Exception as e:
                logging.error(f"消息循环出错: {e}")

    def _process_ui_events(self):
        """处理 UI 事件队列"""
        with self._ui_event_lock:
            if self._ui_event_queue:
                for func, args in self._ui_event_queue:
                    try:
                        func(*args)
                    except Exception as e:
                        logging.error(f"处理 UI 事件出错: {e}")
                self._ui_event_queue = []     
        if self.capture_key:  
            self.update_device_status()      
    
    def process_message(self, command, args):
        """处理从队列接收到的消息"""
        if command == MsgType.CONNENT_SUCCESS:
            self.capture_key = True            
        elif command == MsgType.CALIBRATION_STEP:
            self.show_pnmocap_calibration_step(args[0])
        elif command == MsgType.CALIBRATION_FINISH:
            self.show_pnmocap_calibration_finish()
        elif command == MsgType.SUCCESS: 
            self.show_msg_dialog(args[0], is_error=False) 
        elif command == MsgType.ERROR:
            self.show_msg_dialog(args[0], is_error=True)
        elif command == MsgType.START_CAPTURE:
            self.start_pnmocap_connect()     
        elif command == MsgType.DATA:  
            self.capture_key = True  
            self.message_queue.append(args[0])
        else:
            print(f"未知命令: {command}")

    def run(self):
        """运行应用"""
        self.bvh_header = self.init_bvh_header(self.bvh_header_file)
        self.init_ui()
        # 注册整个目录 - 修正为使用nicegui的app对象
        app.add_static_files(
            url_path='/res',
            local_directory=os.path.join(os.getcwd(), 'web/res')
        )        
        ui.run(title='PN-Link设置面板V1.1.0', dark=False, reload=False)
        
        
    def cleanup(self):
        """清理资源"""
        self._queue_running.clear()
        if self._queue_thread and self._queue_thread.is_alive():
            self._queue_thread.join(timeout=1.0)
            
        if self.mocap_process.is_alive():
            self.mocap_process.terminate()
            self.mocap_process.join(timeout=1.0)

if __name__ in {"__main__", "__mp_main__"}:
    # 确保多进程在Windows上也能正常工作
    multiprocessing.freeze_support()
    
    # 启动应用
    control_panel = WebControlPanel()  # 使用不同的变量名避免命名冲突
    try:
        control_panel.run()
    finally:
        control_panel.cleanup()
# gui_controller.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import multiprocessing
import threading
from mocap_control import MCPControl, MsgType, EMCPCommand

class MocapControllerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Motion Rocord Controller")
        master.geometry("700x600")
        master.resizable(True, True)
        self.record_key = False
        
        # Create message queue
        self.msg_queue = multiprocessing.Queue()
        
        # Initialize MCPControl
        try:
            self.mcp_control = MCPControl(msg_queue=self.msg_queue)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize MCPControl: {str(e)}")
            raise e
            
        # Store calibration step information
        self.calibration_steps = []
        
        # Create UI
        self.create_widgets()
        
        # Start listening for messages
        self.start_listening()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control button area
        control_frame = ttk.LabelFrame(main_frame, text="Control Commands", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # First row of buttons
        button_row1 = ttk.Frame(control_frame)
        button_row1.pack(fill=tk.X, pady=5)
        
        self.btn_start_record = ttk.Button(button_row1, text="Start Recording", command=self.cmd_start_record, state=tk.DISABLED)
        self.btn_start_record.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_stop_record = ttk.Button(button_row1, text="Stop Recording", command=self.cmd_stop_record, state=tk.DISABLED)
        self.btn_stop_record.pack(side=tk.LEFT, padx=(0, 5))
        
    
        
        # Status information area
        status_frame = ttk.LabelFrame(main_frame, text="Status Information", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=15)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear log button
        clear_button = ttk.Button(status_frame, text="Clear Log", command=self.clear_log)
        clear_button.pack(pady=(5, 0))
        
        # Exit button
        exit_button = ttk.Button(main_frame, text="Exit", command=self.on_closing)
        exit_button.pack(pady=(10, 0))

    def cmd_start_record(self):
        self.mcp_control.running_command(EMCPCommand.CommandStartRecored)
        self.btn_stop_record.config(state=tk.NORMAL)
        self.record_key = True
        
    def cmd_stop_record(self):
        self.mcp_control.running_command(EMCPCommand.CommandStopRecored)
        
        
        
    def start_listening(self):
        self.listening = True
        self.listener_thread = threading.Thread(target=self.listen_messages, daemon=True)
        self.listener_thread.start()
        
    def listen_messages(self):
        while self.listening:
            try:
                msg_type, message = self.msg_queue.get(timeout=0.1)
                self.master.after(0, self.process_message, msg_type, message)
            except:
                continue
                
    def process_message(self, msg_type, message):
        # Process different types of messages
        if msg_type == MsgType.STATUS:
            self.add_log(f"[STATUS] {message}")
            
        elif msg_type == MsgType.ERROR:
            self.add_log(f"[ERROR] {message}", "error")
            messagebox.showerror("Error", message)
            
        elif msg_type == MsgType.CONNENT_SUCCESS:
            self.add_log("[CONNECTED] Device connected successfully")
            self.btn_start_record.config(state=tk.NORMAL)
        
            
        elif msg_type == MsgType.SUCCESS:
            self.add_log(f"[SUCCESS] {message}")
            if "Stop Recored" in message or "停止录制" in message:
                self.btn_start_record.config(state=tk.NORMAL)
                self.btn_stop_record.config(state=tk.DISABLED)
                self.record_key = False
       
            elif "Start Recored" in message or "开始录制" in message:
                self.btn_start_record.config(state=tk.DISABLED)
                self.btn_stop_record.config(state=tk.NORMAL)

        elif msg_type == MsgType.DATA:
            # Here we can process skeleton data, just log for now
            if not self.record_key:
                self.add_log("[DATA] Received skeleton data")
                self.btn_start_record.config(state=tk.NORMAL)
                
    def add_log(self, message, level="info"):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def clear_log(self):
        """Clear log"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def on_closing(self):
        """Close application"""
        if messagebox.askokcancel("Confirm Exit", "Are you sure you want to exit the program?"):
            self.listening = False
            try:
                self.mcp_control.stop()
            except:
                pass
            self.master.destroy()

def main():
    root = tk.Tk()
    app = MocapControllerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
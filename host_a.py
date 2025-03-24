import socket
import pickle
from pynput import mouse, keyboard
from PyQt5 import QtWidgets, QtGui, QtCore
from threading import Thread
import time
import sys
import os

class HostA(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.pending_commands = []
        
        # 添加鼠标移动优化相关变量
        self.last_mouse_position = None
        self.mouse_move_timer = None
        self.mouse_move_delay = 0.1  # 100毫秒的延迟
        
        # 监听器
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # 设置UI
        self.setup_ui()
        
    def setup_ui(self):
        # 设置窗口属性
        self.setWindowTitle("远程控制 - 控制端")
        self.setFixedSize(400, 500)
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        
        # 创建中央部件
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 添加标题
        title_label = QtWidgets.QLabel("远程控制系统")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 添加分隔线
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 添加状态组
        status_group = QtWidgets.QGroupBox("连接状态")
        status_layout = QtWidgets.QVBoxLayout()
        
        # 状态标签
        self.status_label = QtWidgets.QLabel("未连接")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        status_font = QtGui.QFont()
        status_font.setPointSize(12)
        self.status_label.setFont(status_font)
        status_layout.addWidget(self.status_label)
        
        # 连接主机信息
        host_layout = QtWidgets.QHBoxLayout()
        host_label = QtWidgets.QLabel("已连接主机:")
        self.host_info = QtWidgets.QLineEdit()
        self.host_info.setReadOnly(True)
        self.host_info.setPlaceholderText("无连接")
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_info)
        status_layout.addLayout(host_layout)
        
        # IP地址输入
        ip_layout = QtWidgets.QHBoxLayout()
        ip_label = QtWidgets.QLabel("目标IP地址:")
        self.ip_input = QtWidgets.QLineEdit("172.18.254.98")
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)
        status_layout.addLayout(ip_layout)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 添加按钮组
        button_layout = QtWidgets.QHBoxLayout()
        
        # 连接按钮
        self.connect_btn = QtWidgets.QPushButton("启动连接")
        self.connect_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.connect_btn.clicked.connect(self.start_connection)
        self.connect_btn.setMinimumHeight(40)
        button_layout.addWidget(self.connect_btn)
        
        # 断开按钮
        self.disconnect_btn = QtWidgets.QPushButton("终止连接")
        self.disconnect_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        self.disconnect_btn.clicked.connect(self.stop_connection)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setMinimumHeight(40)
        button_layout.addWidget(self.disconnect_btn)
        
        main_layout.addLayout(button_layout)
        
        # 添加日志区域
        log_group = QtWidgets.QGroupBox("操作日志")
        log_layout = QtWidgets.QVBoxLayout()
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪")
        
        # 设置样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
        """)
        
        # 添加日志
        self.add_log("应用程序已启动")
    
    def add_log(self, message):
        """添加日志到日志区域"""
        current_time = time.strftime("%H:%M:%S", time.localtime())
        log_entry = f"[{current_time}] {message}"
        self.log_text.append(log_entry)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def start_connection(self):
        try:
            target_ip = self.ip_input.text().strip()
            if not target_ip:
                self.show_error("请输入有效的IP地址")
                return
                
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建新的socket连接
            self.sock.connect((target_ip, 12345))  # 连接到主机B
            self.connected = True
            
            # 更新UI状态
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.status_label.setText("已连接")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.host_info.setText(f"主机B ({self.sock.getpeername()[0]})")
            self.statusBar().showMessage("连接成功")
            
            # 添加日志
            self.add_log(f"已连接到 {self.sock.getpeername()[0]}")
            
            # 启动监听器
            self.start_listeners()
            
            # 启动命令发送线程
            Thread(target=self.send_commands, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"连接失败: {str(e)}")
    
    def show_error(self, message):
        """显示错误对话框"""
        QtWidgets.QMessageBox.critical(self, "错误", message)
        self.add_log(f"错误: {message}")
    
    def start_listeners(self):
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll)
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release)
        self.keyboard_listener.start()
        
        self.add_log("已启动鼠标和键盘监听")
    
    def send_commands(self):
        while self.connected:
            if self.pending_commands:
                command = self.pending_commands.pop(0)
                try:
                    data = pickle.dumps(command)
                    self.sock.sendall(data)
                    # 等待确认
                    ack = self.sock.recv(1024)
                    if not ack:
                        self.pending_commands.insert(0, command)
                except:
                    self.pending_commands.insert(0, command)
                    time.sleep(1)  # 发送失败时等待
            time.sleep(0.01)
    
    def stop_connection(self):
        self.connected = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        try:
            self.sock.close()
        except:
            pass
            
        # 更新UI状态
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.status_label.setText("未连接")
        self.status_label.setStyleSheet("")
        self.host_info.clear()
        self.statusBar().showMessage("已断开连接")
        
        # 添加日志
        self.add_log("已断开连接")
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.connected:
            self.stop_connection()
        event.accept()
            
    # 鼠标事件处理器
    def on_mouse_move(self, x, y):
        if self.connected:
            # 取消之前的定时器（如果存在）
            if hasattr(self, 'mouse_move_timer') and self.mouse_move_timer is not None:
                try:
                    self.mouse_move_timer.cancel()
                except:
                    pass
            
            # 保存当前位置
            self.last_mouse_position = (x, y)
            
            # 使用定时器延迟发送位置
            self.mouse_move_timer = Thread(target=self.send_delayed_mouse_position)
            self.mouse_move_timer.daemon = True
            self.mouse_move_timer.start()
    
    # 添加延迟发送鼠标位置的方法
    def send_delayed_mouse_position(self):
        try:
            time.sleep(self.mouse_move_delay)  # 等待一段时间
            if self.connected and self.last_mouse_position:
                # 发送最终位置
                pos = self.last_mouse_position
                self.pending_commands.append(('mouse_move', pos))
        except Exception as e:
            self.add_log(f"发送鼠标位置时出错: {str(e)}")
    
    def on_mouse_click(self, x, y, button, pressed):
        if self.connected:
            self.pending_commands.append(('mouse_click', (x, y, str(button), pressed)))
    
    def on_mouse_scroll(self, x, y, dx, dy):
        if self.connected:
            self.pending_commands.append(('mouse_scroll', (x, y, dx, dy)))
    
    # 键盘事件处理器
    def on_key_press(self, key):
        if self.connected:
            self.pending_commands.append(('key_press', str(key)))
    
    def on_key_release(self, key):
        if self.connected:
            self.pending_commands.append(('key_release', str(key)))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = HostA()
    window.show()
    sys.exit(app.exec_()) 
import socket
import pickle
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
from threading import Thread

class HostB:
    def __init__(self):
        # 创建控制器
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.connected = False
        
        # 创建系统托盘应用
        self.app = QtWidgets.QApplication(sys.argv)
        
        # 确保系统支持系统托盘
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            print("系统不支持托盘图标")
            sys.exit(1)
            
        # 设置应用程序不随最后一个窗口关闭而退出
        QtWidgets.QApplication.setQuitOnLastWindowClosed(False)
        
        self.tray = QtWidgets.QSystemTrayIcon()
        
        # 使用系统自带图标，不需要额外的图标文件
        icon = self.app.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon)
        self.tray.setToolTip('远程控制被控端')
        
        # 创建托盘菜单
        self.menu = QtWidgets.QMenu()
        self.status_action = self.menu.addAction('状态: 等待连接')
        self.status_action.setEnabled(False)
        self.menu.addSeparator()
        quit_action = self.menu.addAction('退出')
        quit_action.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(self.menu)
        
        # 显示托盘图标
        self.tray.show()
        
        # 启动服务器
        self.start_server()
        
    def start_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('0.0.0.0', 12345))
            self.sock.listen(1)
            self.connected = True
            
            # 启动接收线程
            Thread(target=self.accept_connection, daemon=True).start()
            
        except Exception as e:
            self.status_action.setText(f'状态: 启动失败 ({str(e)})')
            self.tray.showMessage('错误', f'启动服务器失败: {str(e)}', 
                                QtWidgets.QSystemTrayIcon.Critical, 3000)
    
    def accept_connection(self):
        while self.connected:
            try:
                client, addr = self.sock.accept()
                self.status_action.setText(f'状态: 已连接到 {addr[0]}')
                self.tray.showMessage('连接成功', f'已连接到主机A ({addr[0]})', QtWidgets.QSystemTrayIcon.Information)
                self.handle_client(client)
            except:
                if self.connected:
                    self.status_action.setText('状态: 等待连接')
    
    def handle_client(self, client):
        while self.connected:
            try:
                data = client.recv(1024)
                if not data:
                    break
                
                command = pickle.loads(data)
                self.execute_command(command)
                
                # 发送确认信息
                client.send(b'ACK')
                
            except:
                break
        
        try:
            client.close()
        except:
            pass
            
        if self.connected:
            self.status_action.setText('状态: 连接断开，等待重新连接')
    
    def execute_command(self, command):
        cmd_type = command[0]
        cmd_data = command[1]
        
        try:
            if cmd_type == 'mouse_move':
                x, y = cmd_data
                self.mouse.position = (x, y)
                
            elif cmd_type == 'mouse_click':
                x, y, button, pressed = cmd_data
                self.mouse.position = (x, y)
                if button == 'Button.left':
                    if pressed:
                        self.mouse.press(Button.left)
                    else:
                        self.mouse.release(Button.left)
                elif button == 'Button.right':
                    if pressed:
                        self.mouse.press(Button.right)
                    else:
                        self.mouse.release(Button.right)
                        
            elif cmd_type == 'mouse_scroll':
                x, y, dx, dy = cmd_data
                self.mouse.scroll(dx, dy)
                
            elif cmd_type == 'key_press':
                key = eval(cmd_data)
                self.keyboard.press(key)
                
            elif cmd_type == 'key_release':
                key = eval(cmd_data)
                self.keyboard.release(key)
                
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
    
    def quit_app(self):
        self.connected = False
        try:
            self.sock.close()
        except:
            pass
        self.tray.hide()  # 隐藏托盘图标
        self.app.quit()
        sys.exit(0)
    
    def run(self):
        # 显示启动通知
        self.tray.showMessage('远程控制', '服务已启动，等待连接...', 
                            QtWidgets.QSystemTrayIcon.Information, 3000)
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = HostB()
    app.run()
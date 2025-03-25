import socket
import pickle
from pynput import mouse, keyboard
from PyQt5 import QtWidgets, QtGui, QtCore
from threading import Thread
import time
import sys
import os
import pandas as pd
import csv
import xlsxwriter

class HostA(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.pending_commands = []
        
        # 添加鼠标移动优化相关变量
        self.last_mouse_position = None
        self.mouse_move_timer = None
        self.mouse_move_delay = 0.001  # 100毫秒的延迟
        
        # 监听器
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # 主机列表
        self.hosts = []
        self.current_host_index = -1
        
        # 设置UI
        self.setup_ui()
        
    def setup_ui(self):
        # 设置窗口属性
        self.setWindowTitle("远程控制 - 控制端")
        self.setFixedSize(700, 600)  # 增加横向宽度
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
        
        # 添加主机管理组
        hosts_group = QtWidgets.QGroupBox("主机管理")
        hosts_layout = QtWidgets.QVBoxLayout()
        
        # 主机列表
        self.hosts_table = QtWidgets.QTableWidget(0, 5)  # 增加到5列，添加操作列
        self.hosts_table.setHorizontalHeaderLabels(["选择", "主机名", "IP地址", "状态", "操作"])
        self.hosts_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.hosts_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.hosts_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.hosts_table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.hosts_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.hosts_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.hosts_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.hosts_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.hosts_table.itemDoubleClicked.connect(self.on_host_double_clicked)
        hosts_layout.addWidget(self.hosts_table)
        
        # 添加全选/取消全选复选框
        select_all_layout = QtWidgets.QHBoxLayout()
        self.select_all_checkbox = QtWidgets.QCheckBox("全选/取消全选")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        select_all_layout.addWidget(self.select_all_checkbox)
        select_all_layout.addStretch()
        hosts_layout.addLayout(select_all_layout)
        
        # 主机管理按钮
        hosts_buttons_layout = QtWidgets.QHBoxLayout()
        
        self.add_host_btn = QtWidgets.QPushButton("添加主机")
        self.add_host_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
        self.add_host_btn.clicked.connect(self.add_host)
        hosts_buttons_layout.addWidget(self.add_host_btn)
        
        self.remove_host_btn = QtWidgets.QPushButton("删除主机")
        self.remove_host_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        self.remove_host_btn.clicked.connect(self.remove_host)
        hosts_buttons_layout.addWidget(self.remove_host_btn)
        
        self.import_hosts_btn = QtWidgets.QPushButton("导入主机")
        self.import_hosts_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
        self.import_hosts_btn.clicked.connect(self.import_hosts)
        hosts_buttons_layout.addWidget(self.import_hosts_btn)
        
        self.export_template_btn = QtWidgets.QPushButton("导出模板")
        self.export_template_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
        self.export_template_btn.clicked.connect(self.export_template)
        hosts_buttons_layout.addWidget(self.export_template_btn)
        
        # 添加连接按钮
        self.connect_btn = QtWidgets.QPushButton("启动连接")
        self.connect_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.connect_btn.clicked.connect(self.start_connection)
        hosts_buttons_layout.addWidget(self.connect_btn)
        
        # 添加断开按钮
        self.disconnect_btn = QtWidgets.QPushButton("终止连接")
        self.disconnect_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        self.disconnect_btn.clicked.connect(self.stop_connection)
        self.disconnect_btn.setEnabled(False)
        hosts_buttons_layout.addWidget(self.disconnect_btn)
        
        hosts_layout.addLayout(hosts_buttons_layout)
        hosts_group.setLayout(hosts_layout)
        main_layout.addWidget(hosts_group)
        
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
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #cccccc;
                font-weight: bold;
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
    
    def add_host(self):
        """添加新主机"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("添加主机")
        dialog.setFixedSize(300, 150)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        form_layout = QtWidgets.QFormLayout()
        
        name_input = QtWidgets.QLineEdit()
        form_layout.addRow("主机名:", name_input)
        
        ip_input = QtWidgets.QLineEdit()
        form_layout.addRow("IP地址:", ip_input)
        
        layout.addLayout(form_layout)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_input.text().strip()
            ip = ip_input.text().strip()
            
            if not name or not ip:
                self.show_error("主机名和IP地址不能为空")
                return
            
            # 检查IP地址格式
            ip_parts = ip.split('.')
            if len(ip_parts) != 4:
                self.show_error("IP地址格式不正确")
                return
            
            for part in ip_parts:
                try:
                    num = int(part)
                    if num < 0 or num > 255:
                        self.show_error("IP地址格式不正确")
                        return
                except:
                    self.show_error("IP地址格式不正确")
                    return
            
            # 添加到主机列表
            self.hosts.append({"name": name, "ip": ip, "status": "未连接"})
            self.update_hosts_table()
            self.add_log(f"添加主机: {name} ({ip})")
    
    def remove_host(self):
        """删除选中的主机"""
        selected_rows = self.hosts_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_error("请先选择要删除的主机")
            return
        
        row = selected_rows[0].row()
        host = self.hosts[row]
        
        reply = QtWidgets.QMessageBox.question(
            self, "确认删除", 
            f"确定要删除主机 {host['name']} ({host['ip']}) 吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            del self.hosts[row]
            self.update_hosts_table()
            self.add_log(f"删除主机: {host['name']} ({host['ip']})")
    
    def import_hosts(self):
        """从文件导入主机列表"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "导入主机列表", "", 
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;文本文件 (*.txt);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.xlsx'):
                # 从Excel导入
                df = pd.read_excel(file_path)
                if 'name' not in df.columns or 'ip' not in df.columns:
                    self.show_error("Excel文件格式不正确，必须包含'name'和'ip'列")
                    return
                
                for _, row in df.iterrows():
                    self.hosts.append({
                        "name": str(row['name']),
                        "ip": str(row['ip']),
                        "status": "未连接"
                    })
                
            elif file_path.endswith('.csv'):
                # 从CSV导入
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    if 'name' not in reader.fieldnames or 'ip' not in reader.fieldnames:
                        self.show_error("CSV文件格式不正确，必须包含'name'和'ip'列")
                        return
                    
                    for row in reader:
                        self.hosts.append({
                            "name": row['name'],
                            "ip": row['ip'],
                            "status": "未连接"
                        })
                
            elif file_path.endswith('.txt'):
                # 从TXT导入
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            self.hosts.append({
                                "name": parts[0].strip(),
                                "ip": parts[1].strip(),
                                "status": "未连接"
                            })
            
            self.update_hosts_table()
            self.add_log(f"从文件导入了 {len(self.hosts)} 台主机")
            
        except Exception as e:
            self.show_error(f"导入失败: {str(e)}")
    
    def export_template(self):
        """导出主机列表模板"""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "导出主机列表模板", "hosts_template.xlsx", 
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;文本文件 (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.xlsx'):
                # 导出Excel模板
                workbook = xlsxwriter.Workbook(file_path)
                worksheet = workbook.add_worksheet()
                
                # 添加表头
                bold = workbook.add_format({'bold': True})
                worksheet.write('A1', 'name', bold)
                worksheet.write('B1', 'ip', bold)
                
                # 添加示例数据
                worksheet.write('A2', '主机B')
                worksheet.write('B2', '192.168.1.100')
                worksheet.write('A3', '主机C')
                worksheet.write('B3', '192.168.1.101')
                
                workbook.close()
                
            elif file_path.endswith('.csv'):
                # 导出CSV模板
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['name', 'ip'])
                    writer.writerow(['主机B', '192.168.1.100'])
                    writer.writerow(['主机C', '192.168.1.101'])
                
            elif file_path.endswith('.txt'):
                # 导出TXT模板
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("主机B, 192.168.1.100\n")
                    f.write("主机C, 192.168.1.101\n")
            
            self.add_log(f"模板已导出到: {file_path}")
            
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")
    
    def update_hosts_table(self):
        """更新主机列表表格"""
        self.hosts_table.setRowCount(0)
        
        for host in self.hosts:
            row = self.hosts_table.rowCount()
            self.hosts_table.insertRow(row)
            
            # 添加复选框
            checkbox = QtWidgets.QCheckBox()
            checkbox_widget = QtWidgets.QWidget()
            checkbox_layout = QtWidgets.QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.hosts_table.setCellWidget(row, 0, checkbox_widget)
            
            self.hosts_table.setItem(row, 1, QtWidgets.QTableWidgetItem(host['name']))
            self.hosts_table.setItem(row, 2, QtWidgets.QTableWidgetItem(host['ip']))
            
            status_item = QtWidgets.QTableWidgetItem(host['status'])
            if host['status'] == '已连接':
                status_item.setForeground(QtGui.QBrush(QtGui.QColor('green')))
            elif host['status'] == '连接失败':
                status_item.setForeground(QtGui.QBrush(QtGui.QColor('red')))
            
            self.hosts_table.setItem(row, 3, status_item)
            
            # 添加操作按钮
            action_widget = QtWidgets.QWidget()
            action_layout = QtWidgets.QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            # 根据连接状态显示不同的按钮
            if host['status'] == '已连接':
                connect_btn = QtWidgets.QPushButton("断开")
                connect_btn.setStyleSheet("background-color: #e74c3c;")  # 红色按钮
                connect_btn.clicked.connect(self.stop_connection)
            else:
                connect_btn = QtWidgets.QPushButton("连接")
                connect_btn.clicked.connect(lambda checked, r=row: self.start_connection_to_host(r))
            
            connect_btn.setFixedWidth(60)
            
            edit_btn = QtWidgets.QPushButton("编辑")
            edit_btn.setFixedWidth(60)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_host(r))
            
            # 如果主机已连接，禁用编辑按钮
            if host['status'] == '已连接':
                edit_btn.setEnabled(False)
            
            action_layout.addWidget(connect_btn)
            action_layout.addWidget(edit_btn)
            
            self.hosts_table.setCellWidget(row, 4, action_widget)
    
    def on_host_double_clicked(self, item):
        """双击主机列表项时的处理"""
        row = item.row()
        if row >= 0 and row < len(self.hosts):
            # 如果双击的是复选框列，则切换复选框状态
            if item.column() == 0:
                checkbox = self.hosts_table.cellWidget(row, 0).findChild(QtWidgets.QCheckBox)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
            # 否则，如果未连接，则连接到该主机
            elif not self.connected:
                self.start_connection_to_host(row)
    
    def start_connection_to_host(self, host_index):
        """连接到指定索引的主机"""
        if host_index < 0 or host_index >= len(self.hosts):
            return
        
        host = self.hosts[host_index]
        self.add_log(f"正在连接到 {host['name']} ({host['ip']})")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host['ip'], 12345))
            self.connected = True
            self.current_host_index = host_index
            
            # 更新主机状态
            self.hosts[host_index]['status'] = '已连接'
            self.update_hosts_table()
            
            # 更新UI状态
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.statusBar().showMessage(f"已连接到 {host['name']} ({host['ip']})")
            
            # 添加日志
            self.add_log(f"已连接到 {host['name']} ({host['ip']})")
            
            # 启动监听器
            self.start_listeners()
            
            # 启动命令发送线程
            Thread(target=self.send_commands, daemon=True).start()
            
        except Exception as e:
            self.hosts[host_index]['status'] = '连接失败'
            self.update_hosts_table()
            self.show_error(f"连接失败: {str(e)}")
    
    def get_selected_hosts(self):
        """获取所有被选中的主机索引"""
        selected_indices = []
        for row in range(self.hosts_table.rowCount()):
            checkbox = self.hosts_table.cellWidget(row, 0).findChild(QtWidgets.QCheckBox)
            if checkbox and checkbox.isChecked():
                selected_indices.append(row)
        return selected_indices

    def start_connection(self):
        """连接到选中的主机"""
        selected_indices = self.get_selected_hosts()
        if not selected_indices:
            self.show_error("请先选择要连接的主机")
            return
        
        # 如果已经连接到某个主机，先断开连接
        if self.connected:
            self.stop_connection()
        
        # 只连接到第一个选中的主机
        first_host = selected_indices[0]
        self.start_connection_to_host(first_host)
        
        # 如果选择了多个主机，提示用户
        if len(selected_indices) > 1:
            self.add_log(f"注意: 当前只能连接到一个主机，已连接到 {self.hosts[first_host]['name']}")
            QtWidgets.QMessageBox.information(
                self, 
                "多主机选择", 
                f"您选择了 {len(selected_indices)} 个主机，但当前只能连接到一个主机。\n已连接到: {self.hosts[first_host]['name']}",
                QtWidgets.QMessageBox.Ok
            )
    
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
            
        # 更新主机状态
        if self.current_host_index >= 0:
            self.hosts[self.current_host_index]['status'] = '未连接'
            self.current_host_index = -1
            
        # 更新UI状态
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.statusBar().showMessage("已断开连接")
        
        # 更新表格显示
        self.update_hosts_table()
        
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

    def toggle_select_all(self, state):
        """全选/取消全选所有主机"""
        for row in range(self.hosts_table.rowCount()):
            checkbox_widget = self.hosts_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QtWidgets.QCheckBox)
                if checkbox:
                    checkbox.setChecked(state == QtCore.Qt.Checked)

    def edit_host(self, host_index):
        """编辑主机信息"""
        if host_index < 0 or host_index >= len(self.hosts):
            return
        
        host = self.hosts[host_index]
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("编辑主机")
        dialog.setFixedSize(300, 150)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        form_layout = QtWidgets.QFormLayout()
        
        name_input = QtWidgets.QLineEdit(host['name'])
        form_layout.addRow("主机名:", name_input)
        
        ip_input = QtWidgets.QLineEdit(host['ip'])
        form_layout.addRow("IP地址:", ip_input)
        
        layout.addLayout(form_layout)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = name_input.text().strip()
            ip = ip_input.text().strip()
            
            if not name or not ip:
                self.show_error("主机名和IP地址不能为空")
                return
            
            # 检查IP地址格式
            ip_parts = ip.split('.')
            if len(ip_parts) != 4:
                self.show_error("IP地址格式不正确")
                return
            
            for part in ip_parts:
                try:
                    num = int(part)
                    if num < 0 or num > 255:
                        self.show_error("IP地址格式不正确")
                        return
                except:
                    self.show_error("IP地址格式不正确")
                    return
            
            # 更新主机信息
            self.hosts[host_index]['name'] = name
            self.hosts[host_index]['ip'] = ip
            self.update_hosts_table()
            self.add_log(f"更新主机: {name} ({ip})")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = HostA()
    window.show()
    sys.exit(app.exec_()) 
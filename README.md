

# 远程控制系统 / Remote Control System

## 简介 / Introduction

这是一个基于Python开发的远程控制系统，允许您通过网络控制多台计算机的鼠标和键盘操作。系统由控制端(host_a.py)和被控端(host_b.py)两部分组成。

This is a Python-based remote control system that allows you to control mouse and keyboard operations of multiple computers over a network. The system consists of two parts: the control end (host_a.py) and the controlled end (host_b.py).

## 功能特点 / Features

### 控制端 (host_a.py) / Control End (host_a.py)
- 现代化的PyQt5图形界面 / Modern PyQt5 graphical interface
- 支持管理多台远程主机 / Support for managing multiple remote hosts
- 可导入/导出主机列表（支持Excel、CSV和TXT格式）/ Import/export host lists (supports Excel, CSV, and TXT formats)
- 实时操作日志记录 / Real-time operation logging
- 优化的鼠标移动传输，减少网络流量 / Optimized mouse movement transmission to reduce network traffic
- 支持全选/单选主机进行连接 / Support for selecting multiple/single hosts for connection
- 直观的连接状态显示 / Intuitive connection status display

### 被控端 (host_b.py) / Controlled End (host_b.py)
- 系统托盘应用，无需主窗口 / System tray application, no main window required
- 自动接收并执行来自控制端的命令 / Automatically receives and executes commands from the control end
- 支持鼠标移动、点击、滚轮和键盘操作 / Supports mouse movement, clicking, scrolling, and keyboard operations

## 系统要求 / System Requirements

- Python 3.6+
- 网络连接（局域网或互联网）/ Network connection (LAN or Internet)
- 控制端和被控端需安装以下依赖库 / Both ends need the following dependencies installed

## 安装依赖 / Installing Dependencies

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage Instructions

### 被控端设置 / Controlled End Setup
1. 在需要被控制的计算机上运行 `host_b.py` / Run `host_b.py` on the computer to be controlled
2. 程序将在系统托盘中运行，等待控制端连接 / The program will run in the system tray, waiting for the control end to connect
3. 默认监听端口为12345 / Default listening port is 12345

### 控制端操作 / Control End Operation
1. 运行 `host_a.py` 启动控制端界面 / Run `host_a.py` to start the control end interface
2. 添加被控主机信息（可手动添加或导入文件）/ Add controlled host information (manually or by importing a file)
3. 选择要连接的主机，点击"连接"按钮 / Select the host to connect to and click the "Connect" button
4. 连接成功后，您的鼠标和键盘操作将被传输到被控端 / After successful connection, your mouse and keyboard operations will be transmitted to the controlled end

### 主机管理 / Host Management
- **添加主机 / Add Host**: 点击"添加主机"按钮，输入主机名和IP地址 / Click the "Add Host" button and enter the hostname and IP address
- **编辑主机 / Edit Host**: 点击主机列表中的"编辑"按钮 / Click the "Edit" button in the host list
- **删除主机 / Delete Host**: 选择主机后点击"删除主机"按钮 / Select a host and click the "Delete Host" button
- **导入主机 / Import Hosts**: 从Excel、CSV或TXT文件导入主机列表 / Import host list from Excel, CSV, or TXT file
- **导出模板 / Export Template**: 导出主机列表模板，方便批量添加 / Export host list template for batch addition

## 文件说明 / File Description

- `host_a.py`: 控制端程序 / Control end program
- `host_b.py`: 被控端程序 / Controlled end program
- `requirements.txt`: 依赖库列表 / Dependency list
- `build.py`: 打包脚本 / Packaging script
- `create_icon.py`: 创建图标脚本 / Icon creation script

## 注意事项 / Notes

1. 被控端需要开放12345端口 / The controlled end needs to open port 12345
2. 为保证安全，建议在可信任的网络环境中使用 / For security, it is recommended to use in a trusted network environment
3. 控制端一次只能连接到一台被控主机 / The control end can only connect to one controlled host at a time
4. 鼠标移动已进行优化，只传输最终停止位置，减少网络流量 / Mouse movement is optimized to only transmit the final stop position, reducing network traffic

## 构建可执行文件 / Building Executable Files

使用以下命令可以构建独立的可执行文件 / Use the following command to build standalone executable files:

```bash
python build.py
```

构建完成后，可在`dist`目录找到可执行文件 / After building, you can find the executable files in the `dist` directory.

## 许可证 / License

本项目采用MIT许可证 / This project is licensed under the MIT License.

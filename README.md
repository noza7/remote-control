# Remote Control Program / 远程控制程序

[English](#english) | [中文](#中文)

## English

A remote control program that allows one computer (Host A) to control the mouse and keyboard of another computer (Host B) over the network.

### Features

- Real-time mouse movement synchronization
- Mouse click control (left and right buttons)
- Mouse scroll control
- Keyboard input control
- System tray interface for Host B
- Connection status monitoring
- Simple and intuitive GUI for Host A

### Requirements

- Python 3.6+
- PyQt5
- pynput
- socket
- pickle

### Installation

1. Clone the repository:
```bash
git clone https://github.com/noza7/remote-control.git
```

2. Install required packages:
```bash
pip install PyQt5 pynput
```

### Usage

1. On Host B (controlled computer):
   - Run `host_b.py`
   - The program will minimize to system tray
   - Right-click the tray icon to view status or exit

2. On Host A (controlling computer):
   - Run `host_a.py`
   - Enter Host B's IP address
   - Click "Start Connection"
   - Use your mouse and keyboard to control Host B

### Note

Make sure both computers are on the same network and the required ports are not blocked by firewall.

---

## 中文

一个远程控制程序，允许一台电脑（主机A）通过网络控制另一台电脑（主机B）的鼠标和键盘。

### 功能特点

- 实时鼠标移动同步
- 鼠标点击控制（左键和右键）
- 鼠标滚轮控制
- 键盘输入控制
- 主机B系统托盘界面
- 连接状态监控
- 主机A简洁直观的图形界面

### 运行要求

- Python 3.6+
- PyQt5
- pynput
- socket
- pickle

### 安装方法

1. 克隆仓库：
```bash
git clone https://github.com/noza7/remote-control.git
```

2. 安装所需包：
```bash
pip install PyQt5 pynput
```

### 使用方法

1. 在主机B（被控制端）上：
   - 运行 `host_b.py`
   - 程序会最小化到系统托盘
   - 右键点击托盘图标可查看状态或退出

2. 在主机A（控制端）上：
   - 运行 `host_a.py`
   - 输入主机B的IP地址
   - 点击"启动连接"
   - 使用鼠标和键盘控制主机B

### 注意事项

确保两台电脑在同一网络下，且所需端口未被防火墙阻止。
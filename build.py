import PyInstaller.__main__
import os

# 确保resources文件夹存在
if not os.path.exists('resources'):
    os.makedirs('resources')

# 运行PyInstaller
PyInstaller.__main__.run([
    'host_b.py',
    '--name=RemoteControl_B',
    '--windowed',  # 不显示控制台窗口
    '--icon=resources/icon.png',
    '--add-data=resources/icon.png;resources',  # 添加资源文件
    '--noconsole',
    '--onefile'  # 打包成单个文件
]) 
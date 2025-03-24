import os
import PyQt5

qt_platforms_dir = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins', 'platforms')
qwindows_dll_path = os.path.join(qt_platforms_dir, 'qwindows.dll')
print('路径是：'+qwindows_dll_path)
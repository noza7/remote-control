from PIL import Image, ImageDraw
import os

# 创建resources文件夹
if not os.path.exists('resources'):
    os.makedirs('resources')

# 创建一个32x32的图像
img = Image.new('RGB', (32, 32), color='white')
draw = ImageDraw.Draw(img)

# 画一个简单的图形
draw.rectangle([8, 8, 24, 24], fill='blue')

# 保存图标到resources文件夹
img.save('resources/icon.png') 
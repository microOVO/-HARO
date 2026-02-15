# -*- coding: utf-8 -*-
"""
将图片转换为软件图标
"""

import base64
from PIL import Image
import io

# 图片的Base64数据
base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# 解码Base64数据
image_data = base64.b64decode(base64_data)

# 创建PIL Image对象
image = Image.open(io.BytesIO(image_data))

# 调整图片大小为32x32（适合作为图标）
icon_size = (32, 32)
resized_image = image.resize(icon_size, Image.LANCZOS)

# 保存为PNG文件
png_path = "D:\\game\\haropet\\new_haro_icon.png"
resized_image.save(png_path, format="PNG")

# 转换为ICO文件
ico_path = "D:\\game\\haropet\\icon.ico"
# 为ICO文件创建多个尺寸以支持不同分辨率
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
icons = [resized_image.resize(size, Image.LANCZOS) for size in icon_sizes]

# 保存为ICO文件
icons[0].save(ico_path, format="ICO", sizes=icon_sizes, append_images=icons[1:])

print(f"成功创建PNG图标: {png_path}")
print(f"成功创建ICO图标: {ico_path}")

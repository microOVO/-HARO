# -*- coding: utf-8 -*-
"""
创建简单的图标文件，无需外部库依赖
"""

import base64
import os

# 图片的Base64数据
base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# 解码Base64数据
image_data = base64.b64decode(base64_data)

# 保存为PNG文件 - 使用原始字符串
png_path = r"D:\game\haropet\new_haro_icon.png"
with open(png_path, "wb") as f:
    f.write(image_data)

# 将现有的图标文件备份
ico_path = r"D:\game\haropet\icon.ico"
if os.path.exists(ico_path):
    backup_path = r"D:\game\haropet\icon_backup.ico"
    os.rename(ico_path, backup_path)
    print(f"已备份原有图标: {backup_path}")

# 由于没有Pillow，我们直接将PNG作为新图标
# 注意：某些应用可能需要ICO格式，但我们先测试PNG是否可行
print(f"成功创建PNG图标: {png_path}")
print("注意：没有Pillow库，无法直接创建ICO文件")
print("建议：更新系统托盘代码以支持PNG图标，或手动将PNG转换为ICO")

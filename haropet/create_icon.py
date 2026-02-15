# -*- coding: utf-8 -*-
"""
创建哈罗宠物图标
"""

from PIL import Image, ImageDraw

# 创建一个32x32的图标
icon_size = (32, 32)
icon = Image.new('RGBA', icon_size, (255, 255, 255, 0))
draw = ImageDraw.Draw(icon)

# 绘制哈罗宠物图标
center_x, center_y = icon_size[0] // 2, icon_size[1] // 2
radius = min(icon_size) // 2 - 2

# 绘制身体
draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), 
            fill=(80, 180, 80, 255))

# 绘制眼睛
eye_radius = radius // 4
eye_spacing = radius // 2
draw.ellipse((center_x - eye_spacing - eye_radius, center_y - eye_radius, 
              center_x - eye_spacing + eye_radius, center_y + eye_radius), 
             fill=(200, 50, 50, 255))
draw.ellipse((center_x + eye_spacing - eye_radius, center_y - eye_radius, 
              center_x + eye_spacing + eye_radius, center_y + eye_radius), 
             fill=(200, 50, 50, 255))

# 保存图标
icon.save('haropet.ico')
print("图标创建成功: haropet.ico")

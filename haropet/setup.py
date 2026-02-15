# -*- coding: utf-8 -*-
"""
哈罗桌面宠物打包配置文件
"""

import os
import sys
from cx_Freeze import setup, Executable

# 基础配置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 隐藏控制台窗口

# 依赖项
build_exe_options = {
    "packages": ["PyQt5", "logging", "json", "os", "sys", "typing"],
    "include_files": [],  # 项目没有外部资源文件
    "excludes": [],
    "optimize": 2,
}

# 可执行文件配置
executables = [
    Executable(
        script="main.py",
        base=base,
        targetName="哈罗桌面宠物.exe",
        icon=None,  # 暂时没有图标文件
        shortcutName="哈罗桌面宠物",
        shortcutDir="DesktopFolder",
    )
]

# 安装配置
setup(
    name="哈罗桌面宠物",
    version="1.0.0",
    description="可爱的哈罗桌面宠物",
    author="Gundam Studio",
    options={"build_exe": build_exe_options},
    executables=executables,
)

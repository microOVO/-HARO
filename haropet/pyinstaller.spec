# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 项目文件列表
added_files = []

a = Analysis(
    ['main.py'],
    pathex=['d:\\game\\haropet'],
    binaries=[],
    datas=added_files,
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

executable = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='哈罗桌面宠物',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX，因为版本不支持
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    icon=None,  # 暂时没有图标文件
)

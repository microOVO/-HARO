@echo off
chcp 65001 > nul
title 哈罗桌面宠物

echo 正在启动哈罗桌面宠物...
echo.

cd /d "%~dp0"

REM 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境！
    echo 请确保已安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 启动哈罗桌面宠物
python -m haropet.main

if errorlevel 1 (
    echo.
    echo 启动失败，请检查错误信息
    pause
)
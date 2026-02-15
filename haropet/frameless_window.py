# -*- coding: utf-8 -*-
"""
无边框透明窗口基类
为桌面宠物提供无边框、透明背景的窗口支持
"""

import sys
import os
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QCursor


class FramelessWindow(QWidget):
    """
    无边框透明窗口基类
    支持鼠标拖拽移动窗口
    """
    
    # 拖拽信号
    mouse_press = pyqtSignal(QPoint)
    mouse_move = pyqtSignal(QPoint)
    mouse_release = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_window()
        self._setup_drag()
    
    def _init_window(self) -> None:
        """初始化窗口属性"""
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setCursor(Qt.OpenHandCursor)
    
    def _setup_drag(self) -> None:
        """设置拖拽相关变量"""
        self._is_dragging = False
        self._drag_position = QPoint()
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.mouse_press.emit(self._drag_position)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件"""
        if self._is_dragging:
            self.move(event.globalPos() - self._drag_position)
            self.mouse_move.emit(event.globalPos())
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            self.mouse_release.emit()
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event) -> None:
        """双击事件 - 可以在子类中重写"""
        if event.button() == Qt.LeftButton:
            pass
        super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event) -> None:
        """鼠标进入窗口"""
        self.setCursor(Qt.OpenHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """鼠标离开窗口"""
        self.setCursor(Qt.OpenHandCursor)
        super().leaveEvent(event)
        
    def set_window_opacity(self, opacity: float) -> None:
        """设置窗口透明度"""
        if 0.0 <= opacity <= 1.0:
            self.setWindowOpacity(opacity)
        else:
            self.setWindowOpacity(1.0)
    
    def enable_click_through(self, enable: bool = True) -> None:
        """启用或禁用点击穿透"""
        if enable:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        else:
            self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            
    def is_click_through_enabled(self) -> bool:
        """检查是否启用点击穿透"""
        return self.testAttribute(Qt.WA_TransparentForMouseEvents)

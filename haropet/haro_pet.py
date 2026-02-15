# -*- coding: utf-8 -*-
"""
哈罗桌面宠物主类
实现核心的宠物显示功能，将动画和交互委托给专用管理器
"""

import sys
import os
import logging
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap

from haropet.frameless_window import FramelessWindow
from haropet.resources import HaroResources
from haropet.animation_manager import AnimationManager
from haropet.interaction_manager import InteractionManager
from haropet.config_manager import config_manager

logger = logging.getLogger('Haropet.HaroPet')

class HaroPet(FramelessWindow):
    
    STATE_NORMAL = "normal"
    STATE_BACK = "back"
    
    state_changed = pyqtSignal(str)
    greeted = pyqtSignal()
    
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        
        self._current_state = config_manager.get_state()
        
        # 初始化UI
        self._setup_ui()
        
        # 初始化管理器
        self._animation_manager = AnimationManager(self)
        self._interaction_manager = InteractionManager(self, self._pet_label, self._bubble_label)
        
        # 加载配置
        self._load_config()
        
        # 显示宠物
        self._show()
    
    def _setup_ui(self) -> None:
        """设置用户界面"""
        self.setFixedSize(config_manager.WINDOW_SIZE, config_manager.WINDOW_SIZE)
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self._pet_label = QLabel(self)
        self._pet_label.setFixedSize(config_manager.PET_SIZE, config_manager.PET_SIZE)
        self._pet_label.setAlignment(Qt.AlignCenter)
        self._pet_label.setAttribute(Qt.WA_TranslucentBackground)
        self._pet_label.setStyleSheet("background: transparent;")
        
        self._bubble_label = QLabel(self)
        self._bubble_label.setAttribute(Qt.WA_TranslucentBackground)
        self._bubble_label.setVisible(False)
        self._bubble_label.setStyleSheet("background: transparent;")
        
        self._update_pet_image()
    
    def _load_config(self) -> None:
        """加载配置"""
        # 加载位置配置
        position = config_manager.get_position()
        self.move(position["x"], position["y"])
    
    # 冒泡相关方法已移至InteractionManager
    
    def _show(self) -> None:
        """显示宠物窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _update_pet_image(self, state: Optional[str] = None) -> None:
        """更新宠物图像"""
        if state is None:
            state = self._current_state
        
        pixmap = QPixmap(config_manager.PET_SIZE, config_manager.PET_SIZE)
        pixmap.fill(Qt.transparent)
        HaroResources.draw_haro(pixmap, state)
        self._pet_label.setPixmap(pixmap)
    
    # 动画相关方法已移至AnimationManager
    # 跟随相关方法已移至InteractionManager
    
    def set_follow_enabled(self, enabled: bool) -> None:
        """设置是否启用跟随模式"""
        self._interaction_manager.set_follow_enabled(enabled)
    
    def is_follow_enabled(self) -> bool:
        """检查是否启用跟随模式"""
        return self._interaction_manager.is_follow_enabled()
    
    def turn_around(self) -> None:
        """让宠物转身"""
        self._animation_manager.start_turn_animation()
    
    def start_sway(self) -> None:
        """让宠物摇摆"""
        self._animation_manager.start_sway_animation()
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self._current_state
    
    def set_state(self, new_state: str) -> None:
        """设置宠物状态"""
        if self._current_state != new_state:
            self._current_state = new_state
            config_manager.set_state(new_state)
            self._update_pet_image()
            self.state_changed.emit(new_state)
    
    def get_pet_label(self):
        """获取宠物标签"""
        return self._pet_label
    
    def _set_state(self, new_state: str) -> None:
        """设置宠物状态（内部方法）"""
        self.set_state(new_state)
    
    def greet(self) -> None:
        """让宠物打招呼"""
        self._interaction_manager.greet()
        self.greeted.emit()
    
    def mousePressEvent(self, event) -> None:
        """鼠标按下事件"""
        self._interaction_manager.handle_mouse_press(event)
        
        # 更新拖动状态
        self._interaction_manager.set_dragging(True)
        
        # 调用父类的鼠标按下事件，处理拖拽
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event) -> None:
        """鼠标双击事件"""
        self._interaction_manager.handle_mouse_double_click(event)
        super().mouseDoubleClickEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件"""
        # 更新拖动状态
        self._interaction_manager.set_dragging(False)
        
        # 调用父类的鼠标释放事件
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event) -> None:
        """右键菜单事件"""
        event.accept()
    
    def save_position(self) -> None:
        """保存当前位置"""
        config_manager.set_position(self.x(), self.y())
        config_manager.set_state(self._current_state)
        logger.info(f"保存位置: ({self.x()}, {self.y()})")
    
    def closeEvent(self, event) -> None:
        """关闭事件"""
        # 保存位置
        self.save_position()
        
        # 停止动画
        self._animation_manager.stop_all_animations()
        
        # 清理资源
        self._cleanup_resources()
        
        event.accept()
    
    def _cleanup_resources(self) -> None:
        """清理资源（增强版）"""
        try:
            # 清理标签资源
            if hasattr(self, '_pet_label'):
                if self._pet_label.pixmap():
                    self._pet_label.pixmap().detach()
                self._pet_label.clear()
            
            if hasattr(self, '_bubble_label'):
                if self._bubble_label.pixmap():
                    self._bubble_label.pixmap().detach()
                self._bubble_label.clear()
            
            # 清理管理器资源
            if hasattr(self, '_animation_manager'):
                self._animation_manager.stop_all_animations()
            
            if hasattr(self, '_interaction_manager'):
                self._interaction_manager.cleanup()
            
            # 清理定时器
            for attr in dir(self):
                if attr.startswith('_') and attr.endswith('_timer'):
                    timer = getattr(self, attr, None)
                    if timer and hasattr(timer, 'stop'):
                        timer.stop()
            
            logger.info("哈罗宠物资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源失败: {e}")
    
    def update_user_name(self, name: str) -> None:
        """更新用户名"""
        if name:
            self._interaction_manager.update_user_name(name)
    
    def get_user_name(self) -> str:
        """获取当前用户名"""
        return self._interaction_manager.get_user_name()

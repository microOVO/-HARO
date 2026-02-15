# -*- coding: utf-8 -*-
"""
交互管理模块
负责管理宠物的所有交互功能
"""

import time
import random
import logging
from typing import Optional, List

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QCursor

from haropet.config_manager import config_manager

logger = logging.getLogger('Haropet.InteractionManager')

class InteractionManager:
    """交互管理器"""
    
    def __init__(self, pet_window, pet_widget, bubble_widget):
        self.pet_window = pet_window
        self.pet_widget = pet_widget
        self.bubble_widget = bubble_widget
        
        # 跟随相关
        self._is_following = False
        self._follow_offset = QPoint(30, 30)
        self._last_mouse_pos = None
        
        # 点击相关
        self._click_count = 0
        self._last_click_time = None
        
        # 拖动相关
        self._is_dragging = False
        
        # 气泡相关
        self._bubble_timer = QTimer(self.pet_window)
        self._bubble_timer.setSingleShot(True)
        self._bubble_timer.timeout.connect(self._hide_bubble)
        
        # 点击重置定时器
        self._click_reset_timer = QTimer(self.pet_window)
        self._click_reset_timer.setSingleShot(True)
        self._click_reset_timer.timeout.connect(self._reset_click_count)
        
        # 鼠标跟踪定时器
        self._mouse_timer = QTimer(self.pet_window)
        self._mouse_timer.timeout.connect(self._check_mouse_position)
        self._mouse_timer.start(16)  # ~60 FPS
        
        # 加载配置
        self._is_following = config_manager.get_follow_enabled()
    
    def _get_greet_messages(self) -> List[str]:
        """获取问候消息列表"""
        user_name = config_manager.get_user_name()
        messages = [
            "哈罗！",
            "哈罗——",
            "元気？",
            f"{user_name}，哈罗！",
        ]
        return messages
    
    def _show_bubble(self, message: str) -> None:
        """显示气泡消息"""
        # 设置气泡内容和样式
        self.bubble_widget.setText(message)
        self.bubble_widget.setFont(QFont("Microsoft YaHei", 10))
        self.bubble_widget.setStyleSheet("""
            color: #333333;
            background-color: rgba(255, 255, 255, 200);
            border-radius: 12px;
            padding: 8px 14px;
            border: 2px solid rgba(80, 180, 80, 200);
        """)
        self.bubble_widget.adjustSize()
        
        # 计算气泡位置
        bubble_width = self.bubble_widget.width()
        bubble_height = self.bubble_widget.height()
        
        # 宠物图标中心位置
        pet_center_x = 100 + config_manager.PET_SIZE // 2
        pet_center_y = 100 + config_manager.PET_SIZE // 2
        
        # 气泡在宠物右侧，向上偏移
        bubble_x = pet_center_x + config_manager.PET_SIZE // 2 + 170
        bubble_y = pet_center_y - 80
        
        # 确保气泡在窗口范围内
        bubble_x = min(bubble_x, self.pet_window.width() - bubble_width - 10)
        bubble_y = max(bubble_y, 10)
        
        # 设置气泡位置并显示
        self.bubble_widget.setGeometry(bubble_x, bubble_y, bubble_width, bubble_height)
        self.bubble_widget.setVisible(True)
        self._bubble_timer.start(config_manager.BUBBLE_DURATION)
    
    def _hide_bubble(self) -> None:
        """隐藏气泡"""
        self.bubble_widget.hide()
    
    def _check_mouse_position(self) -> None:
        """检查鼠标位置，实现跟随功能"""
        if not self._is_following:
            return
        
        # 如果正在拖动，则暂停跟随更新
        if self._is_dragging:
            return
        
        screen = self.pet_window.screen().availableGeometry()
        cursor_pos = QCursor.pos()
        
        # 如果鼠标在宠物窗口内，则不跟随
        if self.pet_window.geometry().contains(self.pet_window.mapFromGlobal(cursor_pos)):
            self._last_mouse_pos = None
            return
        
        # 第一次检测到鼠标位置
        if self._last_mouse_pos is None:
            self._last_mouse_pos = cursor_pos
            return
        
        # 计算鼠标移动距离
        dx = cursor_pos.x() - self._last_mouse_pos.x()
        dy = cursor_pos.y() - self._last_mouse_pos.y()
        mouse_delta = abs(dx) + abs(dy)
        
        # 鼠标移动太小则不跟随
        if mouse_delta < config_manager.MOUSE_MOVEMENT_THRESHOLD:
            return
        
        # 计算目标位置（鼠标位置加上偏移）
        target_x = cursor_pos.x() + self._follow_offset.x()
        target_y = cursor_pos.y() + self._follow_offset.y()
        
        # 确保目标位置在屏幕范围内
        margin = config_manager.FOLLOW_MARGIN
        target_x = max(screen.left() + margin, 
                      min(screen.right() - self.pet_window.width() - margin, target_x))
        target_y = max(screen.top() + margin, 
                      min(screen.bottom() - self.pet_window.height() - margin, target_y))
        
        # 计算当前距离
        current_x = self.pet_window.x()
        current_y = self.pet_window.y()
        
        # 计算距离
        distance = ((target_x - current_x) ** 2 + (target_y - current_y) ** 2) ** 0.5
        
        # 根据距离设置缓动系数
        if distance < config_manager.FOLLOW_DISTANCE_THRESHOLD_CLOSE:
            easing = config_manager.FOLLOW_EASING_CLOSE
        elif distance < config_manager.FOLLOW_DISTANCE_THRESHOLD_MEDIUM:
            easing = config_manager.FOLLOW_EASING_MEDIUM
        else:
            easing = config_manager.FOLLOW_EASING_FAR
        
        # 计算新位置
        new_x = current_x + (target_x - current_x) * easing
        new_y = current_y + (target_y - current_y) * easing
        
        # 确保新位置在屏幕范围内
        new_x = max(screen.left(), min(screen.right() - self.pet_window.width(), new_x))
        new_y = max(screen.top(), min(screen.bottom() - self.pet_window.height(), new_y))
        
        # 移动宠物
        self.pet_window.move(int(new_x), int(new_y))
        
        # 更新上次鼠标位置
        self._last_mouse_pos = cursor_pos
    
    def _reset_click_count(self) -> None:
        """重置点击计数"""
        self._click_count = 0
    
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            current_time = time.time()
            
            # 计算点击间隔，检测双击或多次点击
            if self._last_click_time and (current_time - self._last_click_time) < config_manager.CLICK_DOUBLE_THRESHOLD:
                self._click_count += 1
            else:
                self._click_count = 1
            
            # 更新点击时间和重置定时器
            self._last_click_time = current_time
            self._click_reset_timer.start(config_manager.CLICK_RESET_TIMEOUT)
            
            # 三次点击触发转身，否则显示问候
            if self._click_count >= config_manager.CLICK_COUNT_FOR_TURN_AROUND:
                logger.info("三次点击，触发转身")
                self.pet_window.turn_around()
                self._click_count = 0
            else:
                self.greet()
    
    def handle_mouse_double_click(self, event):
        """处理鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            self.pet_window.start_sway()
    
    def set_follow_enabled(self, enabled: bool) -> None:
        """设置是否启用跟随模式"""
        self._is_following = enabled
        config_manager.set_follow_enabled(enabled)
        if not enabled:
            self._last_mouse_pos = None
        logger.info(f"跟随模式 {'启用' if enabled else '禁用'}")
    
    def is_follow_enabled(self) -> bool:
        """检查是否启用跟随模式"""
        return self._is_following
    
    def greet(self) -> None:
        """让宠物打招呼"""
        messages = self._get_greet_messages()
        message = random.choice(messages)
        self._show_bubble(message)
        logger.info(f"打招呼: {message}")
    
    def update_user_name(self, name: str) -> None:
        """更新用户名"""
        config_manager.set_user_name(name)
    
    def get_user_name(self) -> str:
        """获取当前用户名"""
        return config_manager.get_user_name()
    
    def set_dragging(self, is_dragging: bool) -> None:
        """设置拖动状态"""
        self._is_dragging = is_dragging
        if is_dragging:
            logger.info("开始拖动宠物")
        else:
            logger.info("结束拖动宠物")
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            if hasattr(self, '_bubble_timer'):
                self._bubble_timer.stop()
            
            if hasattr(self, '_click_reset_timer'):
                self._click_reset_timer.stop()
            
            if hasattr(self, '_mouse_timer'):
                self._mouse_timer.stop()
            
            # 清理状态
            self._is_following = False
            self._last_mouse_pos = None
            self._click_count = 0
            self._last_click_time = None
            
            # 隐藏气泡
            if self.bubble_widget.isVisible():
                self.bubble_widget.hide()
            
            logger.info("交互管理器资源清理完成")
            
        except Exception as e:
            logger.error(f"清理交互管理器资源失败: {e}")

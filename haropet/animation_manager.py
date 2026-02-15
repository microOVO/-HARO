# -*- coding: utf-8 -*-
"""
动画管理模块
负责管理宠物的所有动画效果
"""

import math
import logging
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

from haropet.config_manager import config_manager
from haropet.resources import HaroResources

logger = logging.getLogger('Haropet.AnimationManager')

class AnimationManager:
    """动画管理器"""
    
    def __init__(self, pet_widget):
        self.pet_widget = pet_widget
        self._is_turning = False
        self._is_swaying = False
        self._turn_animation_frame = 0
        self._sway_frame = 0
        
        # 定时器 - 降低刷新率以减少CPU占用
        self._animation_timer = QTimer(self.pet_widget)
        self._animation_timer.timeout.connect(self._update_animations)
        self._animation_timer.start(33)  # ~30 FPS，平衡流畅度和性能
    
    def _update_animations(self):
        """更新所有动画"""
        if self._is_turning:
            self._update_turn_animation()
        elif self._is_swaying:
            self._update_sway_animation()
    
    def _update_turn_animation(self):
        """更新转身动画"""
        self._turn_animation_frame += 1
        total_frames = config_manager.TURN_ANIMATION_TOTAL_FRAMES
        
        # 计算动画进度（0.0 - 1.0）
        progress = min(self._turn_animation_frame / total_frames, 1.0)
        offset_y = 0
        
        # 计算跳跃高度和偏移，分为起跳、空中、落地三个阶段
        if progress < 0.3:
            # 起跳阶段（0-30%）
            jump_progress = progress / 0.3
            jump_height = 50 * (1 - (1 - jump_progress) ** 2)
            offset_y = -int(jump_height)
        elif progress < 0.7:
            # 空中阶段（30%-70%）
            air_progress = (progress - 0.3) / 0.4
            jump_height = 50 * (1 - air_progress ** 2)
            offset_y = -int(jump_height)
        else:
            # 落地阶段（70%-100%）
            land_progress = (progress - 0.7) / 0.3
            jump_height = 10 * (1 - land_progress)
            offset_y = -int(jump_height)
        
        # 更新宠物标签位置
        pet_label = self.pet_widget.get_pet_label()
        if pet_label:
            pet_label.move(100, 100 + offset_y)
        
        # 动画完成，更新状态
        if self._turn_animation_frame >= total_frames:
            self._turn_animation_frame = 0
            
            pet_label = self.pet_widget.get_pet_label()
            if pet_label:
                pet_label.move(100, 100)
            
            # 切换状态
            current_state = self.pet_widget.get_state()
            new_state = "back" if current_state == "normal" else "normal"
            self.pet_widget.set_state(new_state)
            
            if new_state == "back":
                # 启动回到正面定时器
                QTimer.singleShot(3000, self.turn_back)
            
            self._is_turning = False
    
    def _update_sway_animation(self):
        """更新摇摆动画"""
        self._sway_frame += 1
        
        # 摇摆动画完成，重置状态
        if self._sway_frame >= config_manager.SWAY_DURATION:
            self._sway_frame = 0
            self._is_swaying = False
            self.pet_widget._pet_label.move(100, 100)
        else:
            # 计算摇摆偏移，使用正弦函数生成平滑的摇摆效果
            progress = self._sway_frame / config_manager.SWAY_DURATION
            sway_angle = math.sin(progress * math.pi * 4) * config_manager.SWAY_AMPLITUDE
            self.pet_widget._pet_label.move(100 + int(sway_angle), 100)
    
    def start_turn_animation(self):
        """开始转身动画"""
        if not self._is_turning:
            self._is_turning = True
            self._turn_animation_frame = 0
            logger.info("开始转身动画")
    
    def start_sway_animation(self):
        """开始摇摆动画"""
        if not self._is_swaying and not self._is_turning:
            self._is_swaying = True
            self._sway_frame = 0
            logger.info("开始摇摆动画")
    
    def turn_back(self):
        """转身回到正面"""
        if not self._is_turning and self.pet_widget.get_state() == "back":
            self.start_turn_animation()
    
    def is_animating(self):
        """检查是否正在播放动画"""
        return self._is_turning or self._is_swaying
    
    def stop_all_animations(self):
        """停止所有动画"""
        self._is_turning = False
        self._is_swaying = False
        self._turn_animation_frame = 0
        self._sway_frame = 0
        
        # 使用公共方法获取宠物标签
        pet_label = self.pet_widget.get_pet_label()
        if pet_label:
            pet_label.move(100, 100)
        
        logger.info("停止所有动画")

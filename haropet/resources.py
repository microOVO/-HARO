# -*- coding: utf-8 -*-
"""
哈啰资源管理模块
统一管理应用资源，包括图像绘制和资源加载
"""

import sys
import os
import logging
from typing import Optional, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QRadialGradient, QImage

from haropet.config_manager import config_manager

logger = logging.getLogger('Haropet.Resources')

class HaroResources:
    """资源管理器"""
    
    # 直接初始化静态颜色属性
    colors = config_manager.COLORS
    BODY_COLOR = QColor(*colors["body"])
    BODY_LIGHT = QColor(*colors["body_light"])
    BODY_DARK = QColor(*colors["body_dark"])
    EYE_COLOR = QColor(*colors["eye"])
    BLUSH_COLOR = QColor(*colors["blush"])
    SHADOW_COLOR = QColor(*colors["shadow"])
    TEXT_COLOR = QColor(*colors["text"])
    
    def __init__(self):
        self._resource_cache = {}
        self._cache_access_count = {}
        self._max_cache_size = 20  # 最大缓存数量
    
    @classmethod
    def draw_haro(cls, pixmap, state="normal"):
        """绘制哈罗宠物形象"""
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        w, h = pixmap.width(), pixmap.height()
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 2 - 8

        HaroResources._draw_shadow(painter, center_x, center_y + radius * 0.85, radius * 0.7)
        HaroResources._draw_body(painter, center_x, center_y, radius)
        
        if state == "back":
            HaroResources._draw_back(painter, center_x, center_y, radius)
        else:
            HaroResources._draw_normal_face(painter, center_x, center_y, radius)

        painter.end()
    
    @staticmethod
    def _draw_shadow(painter, x, y, radius):
        """绘制阴影"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawEllipse(x - radius, y - radius // 4, radius * 2, radius // 2)
    
    @staticmethod
    def _draw_body(painter, x, y, radius):
        """绘制身体"""
        gradient = QRadialGradient(x - radius * 0.3, y - radius * 0.3, radius * 1.2)
        gradient.setColorAt(0, HaroResources.BODY_LIGHT)
        gradient.setColorAt(0.7, HaroResources.BODY_COLOR)
        gradient.setColorAt(1, HaroResources.BODY_DARK)

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        HaroResources._draw_mouth_line(painter, x, y, radius)
        
    @staticmethod
    def _draw_mouth_line(painter, x, y, radius):
        """绘制嘴部线条"""
        line_y = y + radius // 3
        line_width = radius * 1.9

        painter.setBrush(Qt.NoBrush)
        pen = painter.pen()
        pen.setWidth(radius // 25)
        
        for i in range(-2, 3):
            offset_y = i * (radius // 50)
            alpha = 60 if i == 0 else 40
            pen_color = QColor(60, 160, 60, alpha)
            painter.setPen(pen_color)
            painter.drawArc(x - line_width // 2, line_y - radius // 12 + offset_y, line_width, radius // 6, 0, 180 * 16)

    @staticmethod
    def _draw_back(painter, x, y, radius):
        """绘制背面"""
        pass

    @staticmethod
    def _draw_normal_face(painter, x, y, radius, is_dancing=False):
        """绘制正面表情"""
        eye_y = y - radius // 12
        eye_width = radius // 6
        eye_height = radius // 6
        eye_spacing = radius // 3

        HaroResources._draw_eyes(painter, x, y, eye_y, eye_width, eye_height, eye_spacing)
        HaroResources._draw_blush(painter, x, y, radius, eye_spacing)

    @staticmethod
    def _draw_eyes(painter, x, y, eye_y, eye_width, eye_height, eye_spacing):
        """绘制眼睛"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(HaroResources.EYE_COLOR)
        painter.drawEllipse(x - eye_spacing, eye_y - eye_height, eye_width, eye_height * 2)
        painter.drawEllipse(x + eye_spacing - eye_width, eye_y - eye_height, eye_width, eye_height * 2)

    @staticmethod
    def _draw_blush(painter, x, y, radius, eye_spacing):
        """绘制腮红"""
        blush_radius = radius // 10
        blush_y = y + radius // 10
        blush_x_offset = eye_spacing * 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(HaroResources.BLUSH_COLOR)
        painter.drawEllipse(x - blush_x_offset, blush_y - blush_radius, blush_radius * 2, blush_radius * 1.6)
        painter.drawEllipse(x + blush_x_offset - blush_radius * 2, blush_y - blush_radius, blush_radius * 2, blush_radius * 1.6)
    
    def load_pixmap(self, resource_name: str, size: Optional[int] = None) -> Optional[QPixmap]:
        """加载图像资源（带缓存管理）"""
        cache_key = f"{resource_name}_{size}" if size else resource_name
        
        # 检查缓存
        if cache_key in self._resource_cache:
            self._cache_access_count[cache_key] = self._cache_access_count.get(cache_key, 0) + 1
            return self._resource_cache[cache_key]
        
        # 尝试加载资源
        try:
            # 对于内置资源，使用绘制方式
            if resource_name == "haro_normal":
                pixmap = QPixmap(size or 200, size or 200)
                self.draw_haro(pixmap, "normal")
                self._add_to_cache(cache_key, pixmap)
                return pixmap
            elif resource_name == "haro_back":
                pixmap = QPixmap(size or 200, size or 200)
                self.draw_haro(pixmap, "back")
                self._add_to_cache(cache_key, pixmap)
                return pixmap
            
            # 对于外部资源，尝试从文件加载
            resource_path = self._get_resource_path(resource_name)
            if resource_path:
                pixmap = QPixmap(resource_path)
                if size and not pixmap.isNull():
                    pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._add_to_cache(cache_key, pixmap)
                return pixmap
            
            logger.warning(f"未找到资源: {resource_name}")
            return None
        except Exception as e:
            logger.error(f"加载资源失败 {resource_name}: {e}")
            return None
    
    def _add_to_cache(self, cache_key: str, pixmap: QPixmap):
        """添加到缓存，自动清理旧缓存"""
        # 如果缓存已满，清理最少使用的缓存
        if len(self._resource_cache) >= self._max_cache_size:
            self._cleanup_cache()
        
        self._resource_cache[cache_key] = pixmap
        self._cache_access_count[cache_key] = 1
    
    def _cleanup_cache(self):
        """清理最少使用的缓存项"""
        if not self._resource_cache:
            return
        
        # 找出最少使用的缓存项
        min_count = min(self._cache_access_count.values())
        keys_to_remove = [k for k, v in self._cache_access_count.items() if v == min_count]
        
        # 删除最少使用的项
        for key in keys_to_remove[:len(keys_to_remove) // 2 + 1]:
            if key in self._resource_cache:
                del self._resource_cache[key]
            if key in self._cache_access_count:
                del self._cache_access_count[key]
        
        logger.info(f"清理了 {len(keys_to_remove)} 个缓存项")
    
    def _get_resource_path(self, resource_name: str) -> Optional[str]:
        """获取资源文件路径"""
        resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        if not os.path.exists(resource_dir):
            resource_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 尝试不同的文件扩展名
        extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg"]
        for ext in extensions:
            path = os.path.join(resource_dir, f"{resource_name}{ext}")
            if os.path.exists(path):
                return path
        
        return None
    
    def clear_cache(self):
        """清除资源缓存"""
        self._resource_cache.clear()
        logger.info("资源缓存已清除")

# 创建全局资源管理器实例
global_resources = HaroResources()
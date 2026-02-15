# -*- coding: utf-8 -*-
"""
图标管理器
负责图标加载、缓存和渲染的统一管理
"""

import os
import logging
from typing import Optional, Dict
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QRadialGradient
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication


class IconManager:
    """
    图标管理器类
    负责统一管理图标加载、缓存和渲染
    """
    
    # 类级别的缓存，提高性能和内存效率
    _cached_icons: Dict[str, QPixmap] = {}
    _cache_access_time: Dict[str, float] = {}
    _max_memory_cache_size = 50  # 内存缓存最大数量
    _max_disk_cache_size = 100  # 磁盘缓存最大数量
    
    def __init__(self, logger_name: str = "Haropet.IconManager"):
        self.logger = logging.getLogger(logger_name)
        self.app_dir = self._get_application_dir()
        self.cache_dir = self._get_cache_dir()
        # 确保缓存目录存在
        self._ensure_cache_dir_exists()
    
    def _get_cache_dir(self) -> str:
        """
        获取缓存目录
        
        Returns:
            缓存目录路径
        """
        try:
            # 使用用户目录下的缓存文件夹
            import tempfile
            cache_dir = os.path.join(tempfile.gettempdir(), "haropet", "icon_cache")
            return cache_dir
        except Exception as e:
            self.logger.error(f"获取缓存目录失败: {e}")
            return os.path.join(self.app_dir, "cache")
    
    def _ensure_cache_dir_exists(self) -> None:
        """
        确保缓存目录存在
        """
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
                self.logger.info(f"创建缓存目录: {self.cache_dir}")
        except Exception as e:
            self.logger.error(f"创建缓存目录失败: {e}")
        
    def _get_application_dir(self) -> str:
        """
        获取应用程序目录
        
        Returns:
            应用程序的完整路径
        """
        try:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            self.logger.error(f"获取应用程序目录失败: {e}")
            return os.getcwd()
    
    def get_icon(self, pet_state: str = "normal") -> QIcon:
        """
        获取指定状态的图标（多级缓存）
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            QIcon对象，如果无法获取则返回默认图标
        """
        try:
            import time
            
            # 首先尝试使用文件图标
            icon_file = self._get_icon_file(pet_state)
            if icon_file:
                icon = QIcon(icon_file)
                if not icon.isNull():
                    return icon
            
            # 生成缓存键
            icon_key = self._generate_icon_key(pet_state)
            
            # 尝试从内存缓存获取
            cached_pixmap = self._get_cached_icon(icon_key)
            if cached_pixmap:
                # 更新访问时间
                self._cache_access_time[icon_key] = time.time()
                return QIcon(cached_pixmap)
            
            # 尝试从磁盘缓存获取
            disk_pixmap = self._load_from_disk_cache(icon_key)
            if disk_pixmap:
                # 缓存到内存
                self._cache_icon(icon_key, disk_pixmap)
                return QIcon(disk_pixmap)
            
            # 渲染并缓存新图标
            pixmap = self._render_icon(pet_state)
            if pixmap:
                return QIcon(pixmap)
            
            # 使用默认图标
            return self._create_default_icon()
            
        except Exception as e:
            self.logger.error(f"获取图标失败: {e}")
            return self._create_default_icon()
    
    def clear_cache(self) -> None:
        """
        清理所有缓存
        """
        try:
            # 清理内存缓存
            self._cached_icons.clear()
            self._cache_access_time.clear()
            
            # 清理磁盘缓存
            if os.path.exists(self.cache_dir):
                for file_name in os.listdir(self.cache_dir):
                    if file_name.endswith(".png"):
                        file_path = os.path.join(self.cache_dir, file_name)
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            self.logger.warning(f"删除缓存文件失败: {e}")
            
            self.logger.info("缓存已清理")
            
        except Exception as e:
            self.logger.error(f"清理缓存失败: {e}")
    
    def _get_icon_file(self, pet_state: str) -> Optional[str]:
        """
        获取指定状态的图标文件
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            图标文件路径，如果不存在则返回None
        """
        # 状态图标文件命名规则
        state_icon_names = {
            "normal": ["new_haro_icon.png", "icon.png", "icon.ico", "haropet.png", "haropet.ico"],
            "happy": ["icon_happy.png", "icon_happy.ico", "haropet_happy.png", "haropet_happy.ico"],
            "excited": ["icon_excited.png", "icon_excited.ico", "haropet_excited.png", "haropet_excited.ico"],
            "sleeping": ["icon_sleeping.png", "icon_sleeping.ico", "haropet_sleeping.png", "haropet_sleeping.ico"],
        }
        
        # 获取可能的状态图标文件列表
        possible_names = state_icon_names.get(pet_state, state_icon_names["normal"])
        
        # 尝试找到第一个存在的图标文件
        for name in possible_names:
            icon_path = os.path.join(self.app_dir, name)
            if os.path.exists(icon_path) and os.path.isfile(icon_path):
                self.logger.debug(f"找到图标文件: {icon_path}")
                return icon_path
        
        self.logger.debug(f"未找到状态为 {pet_state} 的图标文件")
        return None
    
    def _generate_icon_key(self, pet_state: str) -> str:
        """
        生成图标缓存键
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            生成的缓存键字符串
        """
        return f"haro_icon_{pet_state}_48x48"
    
    def _get_cached_icon(self, icon_key: str) -> Optional[QPixmap]:
        """
        获取缓存的图标
        
        Args:
            icon_key: 图标缓存键
            
        Returns:
            缓存的QPixmap对象，如果不存在则返回None
        """
        return self._cached_icons.get(icon_key)
    
    def _cache_icon(self, icon_key: str, pixmap: QPixmap) -> None:
        """
        缓存图标（多级缓存）
        
        Args:
            icon_key: 图标缓存键
            pixmap: 要缓存的QPixmap对象
        """
        import time
        
        # 更新访问时间
        current_time = time.time()
        self._cache_access_time[icon_key] = current_time
        
        # 限制内存缓存大小，使用LRU策略
        if len(self._cached_icons) >= self._max_memory_cache_size:
            # 清理最久未使用的缓存项
            self._cleanup_memory_cache()
        
        # 缓存到内存
        self._cached_icons[icon_key] = pixmap
        
        # 同时缓存到磁盘
        self._cache_to_disk(icon_key, pixmap)
    
    def _cleanup_memory_cache(self) -> None:
        """
        清理内存缓存（LRU策略）
        """
        try:
            # 按访问时间排序，清理最久未使用的
            sorted_keys = sorted(self._cache_access_time.items(), key=lambda x: x[1])
            # 清理一半的缓存项
            items_to_remove = len(self._cached_icons) // 2
            
            for key, _ in sorted_keys[:items_to_remove]:
                if key in self._cached_icons:
                    del self._cached_icons[key]
                if key in self._cache_access_time:
                    del self._cache_access_time[key]
            
            self.logger.info(f"清理了 {items_to_remove} 个内存缓存项")
            
        except Exception as e:
            self.logger.error(f"清理内存缓存失败: {e}")
    
    def _cache_to_disk(self, icon_key: str, pixmap: QPixmap) -> None:
        """
        缓存图标到磁盘
        
        Args:
            icon_key: 图标缓存键
            pixmap: 要缓存的QPixmap对象
        """
        try:
            # 生成缓存文件路径
            cache_file = os.path.join(self.cache_dir, f"{icon_key}.png")
            
            # 保存到磁盘
            pixmap.save(cache_file, "PNG", 90)  # 90% 质量
            
            # 清理磁盘缓存
            self._cleanup_disk_cache()
            
        except Exception as e:
            self.logger.error(f"缓存到磁盘失败: {e}")
    
    def _load_from_disk_cache(self, icon_key: str) -> Optional[QPixmap]:
        """
        从磁盘缓存加载图标
        
        Args:
            icon_key: 图标缓存键
            
        Returns:
            加载的QPixmap对象，如果失败则返回None
        """
        try:
            # 生成缓存文件路径
            cache_file = os.path.join(self.cache_dir, f"{icon_key}.png")
            
            # 检查文件是否存在
            if not os.path.exists(cache_file):
                return None
            
            # 加载文件
            pixmap = QPixmap(cache_file)
            if pixmap.isNull():
                return None
            
            self.logger.debug(f"从磁盘缓存加载图标: {icon_key}")
            return pixmap
            
        except Exception as e:
            self.logger.error(f"从磁盘缓存加载失败: {e}")
            return None
    
    def _cleanup_disk_cache(self) -> None:
        """
        清理磁盘缓存
        """
        try:
            # 获取所有缓存文件
            cache_files = []
            for file_name in os.listdir(self.cache_dir):
                if file_name.endswith(".png"):
                    file_path = os.path.join(self.cache_dir, file_name)
                    if os.path.isfile(file_path):
                        # 获取文件修改时间
                        mtime = os.path.getmtime(file_path)
                        cache_files.append((file_path, mtime))
            
            # 按修改时间排序，清理最旧的
            cache_files.sort(key=lambda x: x[1])
            
            # 清理超出限制的文件
            while len(cache_files) > self._max_disk_cache_size:
                file_path, _ = cache_files.pop(0)
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.warning(f"删除缓存文件失败: {e}")
            
        except Exception as e:
            self.logger.error(f"清理磁盘缓存失败: {e}")
    
    def _render_icon(self, pet_state: str) -> Optional[QPixmap]:
        """
        渲染图标
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            渲染后的QPixmap对象，如果失败则返回None
        """
        try:
            pixmap = QPixmap(48, 48)
            pixmap.fill(Qt.transparent)  # 透明背景
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                raise RuntimeError("QPainter无法激活")
                
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 根据状态绘制不同的图标
            self._draw_haro_icon(painter, pet_state)
            
            painter.end()
            
            # 缓存渲染的图标
            icon_key = self._generate_icon_key(pet_state)
            self._cache_icon(icon_key, pixmap)
            
            return pixmap
            
        except Exception as e:
            self.logger.error(f"渲染图标失败: {e}")
            return None
    
    def _draw_haro_icon(self, painter, pet_state: str) -> None:
        """
        绘制哈罗图标（高级视觉效果版）
        
        Args:
            painter: QPainter对象
            pet_state: 宠物状态
        """
        # 获取颜色方案
        colors = self._get_state_colors(pet_state)
        
        w, h = 48, 48
        center_x, center_y = w // 2, h // 2
        radius = 18
        
        # 绘制阴影（增强版）
        shadow_offset = 2
        shadow_blur = 8
        shadow_radius = radius + shadow_blur // 2
        shadow_color = QColor(0, 0, 0, 60)
        
        # 绘制多层阴影，增强立体感
        for i in range(3):
            current_shadow_offset = shadow_offset + i
            current_opacity = 60 - i * 20
            current_shadow_color = QColor(0, 0, 0, current_opacity)
            painter.setBrush(current_shadow_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                center_x - shadow_radius + current_shadow_offset,
                center_y - shadow_radius // 2 + current_shadow_offset,
                shadow_radius * 2, shadow_radius
            )
        
        # 绘制身体（高级渐变）
        gradient = QRadialGradient(
            center_x - radius * 0.4,
            center_y - radius * 0.4,
            radius * 1.5
        )
        # 更精细的渐变控制
        gradient.setColorAt(0, colors['body_main'].lighter(40))
        gradient.setColorAt(0.3, colors['body_main'].lighter(15))
        gradient.setColorAt(0.7, colors['body_main'])
        gradient.setColorAt(0.9, colors['body_main'].darker(10))
        gradient.setColorAt(1, colors['body_main'].darker(30))
        
        painter.setBrush(gradient)
        painter.setPen(colors['border'])
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 绘制多重高光（增强光泽感）
        # 主高光
        highlight_radius = radius * 0.45
        highlight_offset = radius * 0.5
        highlight_color = QColor(255, 255, 255, 80)
        painter.setBrush(highlight_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - highlight_offset - highlight_radius,
            center_y - highlight_offset - highlight_radius,
            highlight_radius * 2, highlight_radius * 2
        )
        
        # 次高光
        secondary_highlight_radius = radius * 0.2
        secondary_highlight_offset = radius * 0.7
        secondary_highlight_color = QColor(255, 255, 255, 60)
        painter.setBrush(secondary_highlight_color)
        painter.drawEllipse(
            center_x + secondary_highlight_offset - secondary_highlight_radius,
            center_y - secondary_highlight_offset - secondary_highlight_radius,
            secondary_highlight_radius * 2, secondary_highlight_radius * 2
        )
        
        # 绘制眼睛（增强版）
        eye_radius = 4
        eye_offset = 7
        eye_y = center_y - 2
        
        # 左眼
        eye_gradient = QRadialGradient(
            center_x - eye_offset - 3,
            eye_y - 3,
            eye_radius * 2
        )
        eye_gradient.setColorAt(0, colors['eye'].lighter(30))
        eye_gradient.setColorAt(0.5, colors['eye'].lighter(10))
        eye_gradient.setColorAt(1, colors['eye'])
        painter.setBrush(eye_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - eye_offset - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2, eye_radius * 2
        )
        
        # 右眼
        painter.setBrush(eye_gradient)
        painter.drawEllipse(
            center_x + eye_offset - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2, eye_radius * 2
        )
        
        # 绘制眼睛高光（增强版）
        # 主高光
        eye_highlight_radius = 1.8
        eye_highlight_offset = 1
        eye_highlight_color = QColor(255, 255, 255, 220)
        painter.setBrush(eye_highlight_color)
        painter.drawEllipse(
            center_x - eye_offset - eye_highlight_radius - eye_highlight_offset,
            eye_y - eye_radius - eye_highlight_offset,
            eye_highlight_radius * 2, eye_highlight_radius * 2
        )
        painter.drawEllipse(
            center_x + eye_offset - eye_highlight_radius - eye_highlight_offset,
            eye_y - eye_radius - eye_highlight_offset,
            eye_highlight_radius * 2, eye_highlight_radius * 2
        )
        
        # 次高光
        eye_secondary_highlight_radius = 1
        eye_secondary_highlight_offset = 3
        eye_secondary_highlight_color = QColor(255, 255, 255, 180)
        painter.setBrush(eye_secondary_highlight_color)
        painter.drawEllipse(
            center_x - eye_offset - eye_secondary_highlight_radius + eye_secondary_highlight_offset,
            eye_y - eye_radius + eye_secondary_highlight_offset,
            eye_secondary_highlight_radius * 2, eye_secondary_highlight_radius * 2
        )
        painter.drawEllipse(
            center_x + eye_offset - eye_secondary_highlight_radius + eye_secondary_highlight_offset,
            eye_y - eye_radius + eye_secondary_highlight_offset,
            eye_secondary_highlight_radius * 2, eye_secondary_highlight_radius * 2
        )
        
        # 绘制嘴巴（根据状态调整）
        mouth_width = 10 if pet_state in ["normal", "happy"] else 12
        mouth_height = 4 if pet_state in ["normal", "happy"] else 5
        mouth_y = center_y + 4
        
        # 嘴巴渐变效果
        mouth_gradient = QRadialGradient(
            center_x, mouth_y,
            mouth_width
        )
        mouth_gradient.setColorAt(0, colors['mouth'].lighter(20))
        mouth_gradient.setColorAt(1, colors['mouth'])
        
        painter.setBrush(mouth_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - mouth_width // 2,
            mouth_y,
            mouth_width, mouth_height
        )
        
        # 绘制身体边框（精细版）
        border_pen = painter.pen()
        border_pen.setWidth(1)
        border_pen.setColor(colors['border'])
        border_pen.setStyle(Qt.SolidLine)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            center_x - radius,
            center_y - radius,
            radius * 2, radius * 2
        )
    
    def _get_state_colors(self, pet_state: str) -> Dict[str, QColor]:
        """
        获取指定状态的颜色方案
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            颜色方案字典
        """
        from PyQt5.QtGui import QColor
        
        color_schemes = {
            "normal": {
                'body_main': QColor(80, 180, 80),
                'eye': QColor(200, 50, 50),
                'mouth': QColor(40, 120, 40),
                'border': QColor(30, 100, 30, 150)
            },
            "happy": {
                'body_main': QColor(100, 200, 90),
                'eye': QColor(220, 60, 60),
                'mouth': QColor(50, 140, 50),
                'border': QColor(40, 120, 40, 180)
            },
            "excited": {
                'body_main': QColor(120, 220, 100),
                'eye': QColor(240, 80, 80),
                'mouth': QColor(60, 160, 60),
                'border': QColor(50, 140, 50, 200)
            },
            "sleeping": {
                'body_main': QColor(60, 140, 60),
                'eye': QColor(100, 30, 30),
                'mouth': QColor(30, 80, 30),
                'border': QColor(20, 80, 20, 120)
            }
        }
        
        return color_schemes.get(pet_state, color_schemes["normal"])
    
    def _create_default_icon(self) -> QIcon:
        """
        创建默认图标
        
        Returns:
            默认QIcon对象
        """
        try:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(80, 180, 80))
            return QIcon(pixmap)
        except Exception:
            # 如果连默认图标都无法创建，返回空图标
            return QIcon()
    
    def get_animated_icon(self, from_state: str, to_state: str, progress: float) -> QIcon:
        """
        获取状态过渡动画的图标
        
        Args:
            from_state: 起始状态
            to_state: 目标状态
            progress: 动画进度（0.0 - 1.0）
            
        Returns:
            过渡状态的QIcon对象
        """
        try:
            # 生成缓存键
            animation_key = f"animation_{from_state}_{to_state}_{progress:.2f}"
            
            # 尝试从缓存获取
            if animation_key in self._cached_icons:
                return QIcon(self._cached_icons[animation_key])
            
            # 渲染过渡图标
            pixmap = self._render_transition_icon(from_state, to_state, progress)
            if pixmap:
                # 缓存过渡图标
                self._cache_icon(animation_key, pixmap)
                return QIcon(pixmap)
            
            # 回退到目标状态图标
            return self.get_icon(to_state)
            
        except Exception as e:
            self.logger.error(f"获取动画图标失败: {e}")
            return self.get_icon(to_state)
    
    def _render_transition_icon(self, from_state: str, to_state: str, progress: float) -> Optional[QPixmap]:
        """
        渲染状态过渡图标
        
        Args:
            from_state: 起始状态
            to_state: 目标状态
            progress: 动画进度（0.0 - 1.0）
            
        Returns:
            过渡状态的QPixmap对象
        """
        try:
            pixmap = QPixmap(48, 48)
            pixmap.fill(Qt.transparent)  # 透明背景
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                raise RuntimeError("QPainter无法激活")
                
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 绘制过渡效果
            self._draw_transition_icon(painter, from_state, to_state, progress)
            
            painter.end()
            return pixmap
            
        except Exception as e:
            self.logger.error(f"渲染过渡图标失败: {e}")
            return None
    
    def _draw_transition_icon(self, painter, from_state: str, to_state: str, progress: float) -> None:
        """
        绘制状态过渡图标
        
        Args:
            painter: QPainter对象
            from_state: 起始状态
            to_state: 目标状态
            progress: 动画进度（0.0 - 1.0）
        """
        w, h = 48, 48
        center_x, center_y = w // 2, h // 2
        
        # 计算过渡位置和缩放
        scale_factor = 1.0 + progress * 0.1  # 轻微放大效果
        offset_x = int((progress - 0.5) * 10)  # 左右摇摆效果
        offset_y = int(-progress * 5)  # 上下浮动效果
        
        # 保存当前状态
        painter.save()
        
        # 应用变换
        painter.translate(center_x, center_y)
        painter.scale(scale_factor, scale_factor)
        painter.translate(-center_x + offset_x, -center_y + offset_y)
        
        # 根据进度混合两个状态的颜色
        from_colors = self._get_state_colors(from_state)
        to_colors = self._get_state_colors(to_state)
        
        # 绘制过渡图标
        self._draw_haro_icon_with_blended_colors(painter, from_colors, to_colors, progress)
        
        # 恢复状态
        painter.restore()
    
    def _draw_haro_icon_with_blended_colors(self, painter, from_colors: dict, to_colors: dict, progress: float) -> None:
        """
        使用混合颜色绘制哈罗图标
        
        Args:
            painter: QPainter对象
            from_colors: 起始状态颜色
            to_colors: 目标状态颜色
            progress: 混合进度（0.0 - 1.0）
        """
        w, h = 48, 48
        center_x, center_y = w // 2, h // 2
        radius = 18
        
        # 混合颜色
        blended_colors = {}
        for key in from_colors:
            if key in to_colors:
                blended_colors[key] = self._blend_colors(from_colors[key], to_colors[key], progress)
            else:
                blended_colors[key] = from_colors[key]
        
        # 绘制阴影（增强版）
        shadow_offset = 2
        shadow_blur = 8
        shadow_radius = radius + shadow_blur // 2
        
        # 绘制多层阴影，增强立体感
        for i in range(3):
            current_shadow_offset = shadow_offset + i
            current_opacity = 60 - i * 20
            current_shadow_color = QColor(0, 0, 0, current_opacity)
            painter.setBrush(current_shadow_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                center_x - shadow_radius + current_shadow_offset,
                center_y - shadow_radius // 2 + current_shadow_offset,
                shadow_radius * 2, shadow_radius
            )
        
        # 绘制身体（高级渐变）
        gradient = QRadialGradient(
            center_x - radius * 0.4,
            center_y - radius * 0.4,
            radius * 1.5
        )
        # 更精细的渐变控制
        gradient.setColorAt(0, blended_colors['body_main'].lighter(40))
        gradient.setColorAt(0.3, blended_colors['body_main'].lighter(15))
        gradient.setColorAt(0.7, blended_colors['body_main'])
        gradient.setColorAt(0.9, blended_colors['body_main'].darker(10))
        gradient.setColorAt(1, blended_colors['body_main'].darker(30))
        
        painter.setBrush(gradient)
        painter.setPen(blended_colors['border'])
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # 绘制多重高光（增强光泽感）
        # 主高光
        highlight_radius = radius * 0.45
        highlight_offset = radius * 0.5
        highlight_color = QColor(255, 255, 255, 80)
        painter.setBrush(highlight_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - highlight_offset - highlight_radius,
            center_y - highlight_offset - highlight_radius,
            highlight_radius * 2, highlight_radius * 2
        )
        
        # 次高光
        secondary_highlight_radius = radius * 0.2
        secondary_highlight_offset = radius * 0.7
        secondary_highlight_color = QColor(255, 255, 255, 60)
        painter.setBrush(secondary_highlight_color)
        painter.drawEllipse(
            center_x + secondary_highlight_offset - secondary_highlight_radius,
            center_y - secondary_highlight_offset - secondary_highlight_radius,
            secondary_highlight_radius * 2, secondary_highlight_radius * 2
        )
        
        # 绘制眼睛（增强版）
        eye_radius = 4
        eye_offset = 7
        eye_y = center_y - 2
        
        # 左眼
        eye_gradient = QRadialGradient(
            center_x - eye_offset - 3,
            eye_y - 3,
            eye_radius * 2
        )
        eye_gradient.setColorAt(0, blended_colors['eye'].lighter(30))
        eye_gradient.setColorAt(0.5, blended_colors['eye'].lighter(10))
        eye_gradient.setColorAt(1, blended_colors['eye'])
        painter.setBrush(eye_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - eye_offset - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2, eye_radius * 2
        )
        
        # 右眼
        painter.setBrush(eye_gradient)
        painter.drawEllipse(
            center_x + eye_offset - eye_radius,
            eye_y - eye_radius,
            eye_radius * 2, eye_radius * 2
        )
        
        # 绘制眼睛高光（增强版）
        # 主高光
        eye_highlight_radius = 1.8
        eye_highlight_offset = 1
        eye_highlight_color = QColor(255, 255, 255, 220)
        painter.setBrush(eye_highlight_color)
        painter.drawEllipse(
            center_x - eye_offset - eye_highlight_radius - eye_highlight_offset,
            eye_y - eye_radius - eye_highlight_offset,
            eye_highlight_radius * 2, eye_highlight_radius * 2
        )
        painter.drawEllipse(
            center_x + eye_offset - eye_highlight_radius - eye_highlight_offset,
            eye_y - eye_radius - eye_highlight_offset,
            eye_highlight_radius * 2, eye_highlight_radius * 2
        )
        
        # 次高光
        eye_secondary_highlight_radius = 1
        eye_secondary_highlight_offset = 3
        eye_secondary_highlight_color = QColor(255, 255, 255, 180)
        painter.setBrush(eye_secondary_highlight_color)
        painter.drawEllipse(
            center_x - eye_offset - eye_secondary_highlight_radius + eye_secondary_highlight_offset,
            eye_y - eye_radius + eye_secondary_highlight_offset,
            eye_secondary_highlight_radius * 2, eye_secondary_highlight_radius * 2
        )
        painter.drawEllipse(
            center_x + eye_offset - eye_secondary_highlight_radius + eye_secondary_highlight_offset,
            eye_y - eye_radius + eye_secondary_highlight_offset,
            eye_secondary_highlight_radius * 2, eye_secondary_highlight_radius * 2
        )
        
        # 绘制嘴巴
        mouth_width = 10
        mouth_height = 4
        mouth_y = center_y + 4
        
        # 嘴巴渐变效果
        mouth_gradient = QRadialGradient(
            center_x, mouth_y,
            mouth_width
        )
        mouth_gradient.setColorAt(0, blended_colors['mouth'].lighter(20))
        mouth_gradient.setColorAt(1, blended_colors['mouth'])
        
        painter.setBrush(mouth_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - mouth_width // 2,
            mouth_y,
            mouth_width, mouth_height
        )
        
        # 绘制身体边框（精细版）
        border_pen = painter.pen()
        border_pen.setWidth(1)
        border_pen.setColor(blended_colors['border'])
        border_pen.setStyle(Qt.SolidLine)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            center_x - radius,
            center_y - radius,
            radius * 2, radius * 2
        )
    
    def _blend_colors(self, color1: QColor, color2: QColor, factor: float) -> QColor:
        """
        混合两种颜色
        
        Args:
            color1: 第一种颜色
            color2: 第二种颜色
            factor: 混合因子（0.0 - 1.0）
            
        Returns:
            混合后的颜色
        """
        r1, g1, b1, a1 = color1.getRgb()
        r2, g2, b2, a2 = color2.getRgb()
        
        r = int(r1 * (1 - factor) + r2 * factor)
        g = int(g1 * (1 - factor) + g2 * factor)
        b = int(b1 * (1 - factor) + b2 * factor)
        a = int(a1 * (1 - factor) + a2 * factor)
        
        return QColor(r, g, b, a)
    
    def pre_cache_icons(self, states: list) -> None:
        """
        预缓存指定状态的图标
        
        Args:
            states: 需要预缓存的状态列表
        """
        for state in states:
            try:
                QTimer.singleShot(0, lambda s=state: self.get_icon(s))
            except Exception as e:
                self.logger.warning(f"预缓存图标 {state} 失败: {e}")

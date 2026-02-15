# -*- coding: utf-8 -*-
"""
工具类模块
集中管理通用功能函数
"""

import os
import sys
import logging
import platform
import time
import random
from typing import Optional, Tuple, Any, Dict

from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt

logger = logging.getLogger('Haropet.Utils')

class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_application_path() -> str:
        """获取应用程序所在路径"""
        if hasattr(sys, 'frozen'):
            # 对于打包后的应用
            return os.path.dirname(sys.executable)
        else:
            # 对于开发环境
            return os.path.dirname(os.path.abspath(__file__))
    
    @staticmethod
    def get_resource_path(resource_name: str, resource_dir: str = "resources") -> Optional[str]:
        """获取资源文件路径"""
        app_path = FileUtils.get_application_path()
        
        # 尝试不同的资源位置
        possible_paths = [
            os.path.join(app_path, resource_dir, resource_name),
            os.path.join(app_path, resource_name),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 尝试添加不同的扩展名
        extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]
        for ext in extensions:
            for path in possible_paths:
                path_with_ext = path + ext
                if os.path.exists(path_with_ext):
                    return path_with_ext
        
        logger.warning(f"未找到资源文件: {resource_name}")
        return None
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """确保目录存在"""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"创建目录: {directory}")
            return True
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def get_config_directory() -> str:
        """获取配置文件目录"""
        return os.path.join(os.path.expanduser("~"), ".haropet")

class ImageUtils:
    """图像工具类"""
    
    @staticmethod
    def load_pixmap(image_path: str, size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """加载图像为QPixmap"""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logger.error(f"加载图像失败: {image_path}")
                return None
            
            if size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            return pixmap
        except Exception as e:
            logger.error(f"加载图像失败 {image_path}: {e}")
            return None
    
    @staticmethod
    def load_icon(icon_path: str, size: Optional[Tuple[int, int]] = None) -> Optional[QIcon]:
        """加载图像为QIcon"""
        pixmap = ImageUtils.load_pixmap(icon_path, size)
        if pixmap:
            return QIcon(pixmap)
        return None
    
    @staticmethod
    def pixmap_to_image(pixmap: QPixmap) -> QImage:
        """将QPixmap转换为QImage"""
        return pixmap.toImage()
    
    @staticmethod
    def image_to_pixmap(image: QImage) -> QPixmap:
        """将QImage转换为QPixmap"""
        return QPixmap.fromImage(image)

class SystemUtils:
    """系统工具类"""
    
    @staticmethod
    def get_platform() -> str:
        """获取当前平台"""
        return platform.system().lower()
    
    @staticmethod
    def is_windows() -> bool:
        """检查是否为Windows系统"""
        return SystemUtils.get_platform() == "windows"
    
    @staticmethod
    def is_mac() -> bool:
        """检查是否为macOS系统"""
        return SystemUtils.get_platform() == "darwin"
    
    @staticmethod
    def is_linux() -> bool:
        """检查是否为Linux系统"""
        return SystemUtils.get_platform() == "linux"
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """获取系统信息"""
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def show_notification(title: str, message: str) -> None:
        """显示系统通知"""
        # 跨平台通知实现可以在这里添加
        logger.info(f"系统通知: {title} - {message}")

class UIUtils:
    """UI工具类"""
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """获取屏幕尺寸"""
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            size = screen.size()
            return size.width(), size.height()
        return 1920, 1080  # 默认值
    
    @staticmethod
    def center_widget(widget: Any) -> None:
        """将窗口居中显示"""
        screen_width, screen_height = UIUtils.get_screen_size()
        widget_width = widget.width()
        widget_height = widget.height()
        
        x = (screen_width - widget_width) // 2
        y = (screen_height - widget_height) // 2
        
        widget.move(x, y)
    
    @staticmethod
    def create_transparent_pixmap(width: int, height: int) -> QPixmap:
        """创建透明的QPixmap"""
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        return pixmap

class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    @staticmethod
    def get_current_timestamp() -> float:
        """获取当前时间戳"""
        return time.time()
    
    @staticmethod
    def format_time(timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化时间戳"""
        return time.strftime(format_str, time.localtime(timestamp))

class RandomUtils:
    """随机工具类"""
    
    @staticmethod
    def get_random_number(min_val: int, max_val: int) -> int:
        """获取指定范围内的随机整数"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def get_random_float(min_val: float, max_val: float) -> float:
        """获取指定范围内的随机浮点数"""
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def get_random_item(items: list) -> Any:
        """从列表中随机选择一个元素"""
        if not items:
            return None
        return random.choice(items)
    
    @staticmethod
    def get_random_color(alpha: int = 255) -> Tuple[int, int, int, int]:
        """获取随机颜色"""
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            alpha
        )

class StringUtils:
    """字符串工具类"""
    
    @staticmethod
    def truncate_string(text: str, max_length: int, ellipsis: str = "...") -> str:
        """截断字符串"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(ellipsis)] + ellipsis
    
    @staticmethod
    def format_string(text: str, **kwargs) -> str:
        """格式化字符串"""
        return text.format(**kwargs)

# 工具函数的快捷访问
get_application_path = FileUtils.get_application_path
get_resource_path = FileUtils.get_resource_path
ensure_directory = FileUtils.ensure_directory
load_pixmap = ImageUtils.load_pixmap
load_icon = ImageUtils.load_icon
get_platform = SystemUtils.get_platform
is_windows = SystemUtils.is_windows
is_mac = SystemUtils.is_mac
is_linux = SystemUtils.is_linux
get_system_info = SystemUtils.get_system_info
show_notification = SystemUtils.show_notification
get_screen_size = UIUtils.get_screen_size
center_widget = UIUtils.center_widget
create_transparent_pixmap = UIUtils.create_transparent_pixmap
get_current_time = TimeUtils.get_current_time
get_current_timestamp = TimeUtils.get_current_timestamp
format_time = TimeUtils.format_time
get_random_number = RandomUtils.get_random_number
get_random_float = RandomUtils.get_random_float
get_random_item = RandomUtils.get_random_item
get_random_color = RandomUtils.get_random_color
truncate_string = StringUtils.truncate_string
format_string = StringUtils.format_string
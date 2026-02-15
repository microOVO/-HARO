# -*- coding: utf-8 -*-
"""
系统托盘图标和菜单
提供托盘交互和功能菜单
"""

import sys
import os
import logging
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMessageBox, QApplication, QDialog
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QCursor
from haropet.haro_pet import HaroPet
from haropet.user_panel import UserPanel
from haropet.icon_manager import IconManager
from haropet.menu_manager import MenuManager


class HaroSystemTray(QSystemTrayIcon):
    """
    哈罗系统托盘图标和菜单类
    
    提供托盘交互和功能菜单，包含完整的错误处理和类型安全。
    主要功能包括：
    - 绘制专业的哈罗图标
    - 提供交互式菜单
    - 管理宠物状态显示
    - 处理用户交互事件
    
    性能优化：
    - 使用资源缓存避免重复创建
    - 延迟加载非关键资源
    - 优化事件处理减少不必要的更新
    
    Args:
        pet: 哈罗宠物对象，可以为None（功能受限）
    """
    
    def __init__(self, pet: Optional[HaroPet]) -> None:
        """
        初始化哈罗系统托盘
        
        Args:
            pet: 哈罗宠物对象。如果为None，则功能会受限，但仍可基本工作。
        """
        super().__init__()
        self.pet = pet
        
        # 初始化图标缓存
        self._cached_icons = {}
        
        # 初始化管理器
        self.icon_manager = IconManager()
        self.menu_manager = MenuManager(self)
        
        # 性能优化：延迟初始化非关键资源
        self._user_panel: Optional[QDialog] = None
        
        # 立即设置基本图标，确保托盘显示正常
        self._setup_icon()
        
        # 延迟设置菜单和连接，优化启动时间
        QTimer.singleShot(0, self._delayed_setup)
    
    def _delayed_setup(self) -> None:
        """
        延迟设置方法，优化启动性能
        
        在主事件循环启动后设置菜单和信号连接，
        避免阻塞主线程，提升启动速度。
        """
        try:
            self._setup_menu()
            self._setup_connections()
        except Exception as e:
            self._log_error(f"延迟设置失败: {e}")
            # 即使延迟设置失败，托盘也能基本工作
    
    def _safe_setup_paths(self) -> None:
        """
        安全地设置Python路径，避免安全风险
        
        验证路径存在性并限制范围，防止模块加载攻击。
        """
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if os.path.exists(current_dir) and os.path.isdir(current_dir):
                project_root = os.path.abspath(current_dir)
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
        except (OSError, PermissionError) as e:
            self._log_warning(f"路径设置失败: {e}")
    
    def _sanitize_error_message(self, error_msg: str) -> str:
        """
        清理错误消息中的敏感信息
        
        移除可能的路径信息、用户数据等敏感内容，
        防止在日志中泄露敏感信息。
        
        Args:
            error_msg: 原始错误消息
            
        Returns:
            清理后的安全错误消息
        """
        import re
        # 移除路径信息
        sanitized = re.sub(r'[/\\][^/\\]*[/\\][^/\\]*', '[PATH]', error_msg)
        sanitized = re.sub(r'C:.*? ', '[PATH]', sanitized)
        # 移除可能的用户信息
        sanitized = re.sub(r'user[_\s]*name.*?[=\s]\w+', '[USER]', sanitized, flags=re.IGNORECASE)
        return sanitized
    
    def _get_icon_file_path(self) -> Optional[str]:
        """
        获取图标文件路径
        
        尝试从多个位置寻找图标文件，返回第一个找到的有效路径。
        支持ICO和PNG格式的图标文件。
        
        Returns:
            图标文件的完整路径，如果找不到则返回None
        """
        try:
            # 获取当前文件的目录 - 使用可靠的方式获取程序目录
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self._log_debug(f"程序目录: {current_dir}")
            
            # 可能的图标文件路径列表 - 支持ICO和PNG格式
            possible_paths = [
                # 首先检查新创建的PNG图标
                os.path.join(current_dir, "new_haro_icon.png"),
                # 然后检查传统的ICO图标
                os.path.join(current_dir, "icon.ico"),
                os.path.join(current_dir, "icon_backup.ico"),
                os.path.join(current_dir, "haropet.ico"),
                # 检查PNG格式的图标
                os.path.join(current_dir, "icon.png"),
                os.path.join(current_dir, "haropet.png"),
            ]
            
            # 尝试找到第一个存在的图标文件
            for path in possible_paths:
                self._log_debug(f"检查图标路径: {path}")
                if os.path.exists(path) and os.path.isfile(path):
                    self._log_debug(f"找到图标文件: {path}")
                    return path
            
            self._log_debug("未找到任何图标文件")
            return None
        except Exception as e:
            self._log_error(f"获取图标路径失败: {e}")
            return None

    def _log_error(self, message: str) -> None:
        """记录错误日志"""
        logger = logging.getLogger('Haropet.SystemTray')
        logger.error(message)
    
    def _log_warning(self, message: str) -> None:
        """记录警告日志"""
        logger = logging.getLogger('Haropet.SystemTray')
        logger.warning(message)
    
    def _create_fallback_icon(self) -> QIcon:
        """创建默认回退图标"""
        try:
            # 创建一个简单的默认图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.blue)
            return QIcon(pixmap)
        except Exception:
            # 如果连默认图标都无法创建，返回空图标
            return QIcon()
    
    def _setup_icon(self) -> None:
        """设置系统托盘图标，包含性能优化和缓存机制"""
        try:
            # 首先尝试使用现有的icon.ico文件
            icon_file_path = self._get_icon_file_path()
            if icon_file_path and os.path.exists(icon_file_path):
                try:
                    # 使用现有的图标文件
                    icon = QIcon(icon_file_path)
                    if not icon.isNull():
                        self.setIcon(icon)
                        self._icon_initialized = True
                        self._log_debug(f"成功加载图标文件: {icon_file_path}")
                        return
                except Exception as e:
                    self._log_warning(f"加载图标文件失败: {e}")
            
            # 使用IconManager获取图标
            icon = self.icon_manager.get_icon("normal")
            if not icon.isNull():
                self.setIcon(icon)
                self._icon_initialized = True
                self._log_debug("成功从IconManager获取图标")
                return
            
            # 回退到传统绘制方法
            self._create_icon_traditional()
            
        except Exception as e:
            self._log_error(f"设置图标失败: {e}")
            # 使用回退图标
            self.setIcon(self._create_fallback_icon())
            self._icon_initialized = True
    
    def _ensure_icon_cached(self, pet_state: str) -> None:
        """
        确保指定状态的图标已缓存
        
        Args:
            pet_state: 宠物状态
        """
        try:
            # 使用IconManager预缓存图标
            QTimer.singleShot(0, lambda: self.icon_manager.get_icon(pet_state))
        except Exception as e:
            self._log_warning(f"预缓存图标失败: {e}")
    
    def _pre_cache_icon(self, icon_key: str, pet_state: str) -> None:
        """
        后台预缓存图标
        
        Args:
            icon_key: 图标缓存键
            pet_state: 宠物状态
        """
        try:
            # 使用IconManager预缓存图标
            self.icon_manager.get_icon(pet_state)
        except Exception as e:
            self._log_warning(f"后台缓存图标失败: {e}")
    
    def _create_icon_traditional(self) -> None:
        """使用传统方法创建图标（回退方案）"""
        try:
            pixmap = QPixmap(48, 48)
            if pixmap.isNull():
                raise ValueError("无法创建QPixmap对象")
            
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                raise RuntimeError("QPainter无法激活")
                
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 使用传统绘制方法
            self._draw_haro_to_painter(painter, "normal")
            
            painter.end()
            self.setIcon(QIcon(pixmap))
            
        except Exception as e:
            self._log_error(f"传统图标创建失败: {e}")
            self.setIcon(self._create_fallback_icon())
        finally:
            if 'painter' in locals() and painter.isActive():
                painter.end()
    
    def _setup_auto_cleanup(self) -> None:
        """
        设置自动缓存清理机制
        
        定期清理过期的缓存项，防止内存泄漏。
        """
        try:
            # 每5分钟清理一次缓存
            cleanup_timer = QTimer(self)
            cleanup_timer.timeout.connect(self._cleanup_old_cache)
            cleanup_timer.start(5 * 60 * 1000)  # 5分钟
            
            self._cleanup_timer = cleanup_timer
            
        except Exception as e:
            self._log_warning(f"设置自动清理失败: {e}")
    
    def _cleanup_old_cache(self) -> None:
        """
        清理过期的缓存项
        
        保留最近使用的图标，清理旧的缓存项以防止内存泄漏。
        """
        try:
            # 这里可以扩展为基于时间的缓存清理
            # 当前实现基于数量限制，在_cache_icon方法中处理
            
            if len(self._cached_icons) > 5:
                # 保留最新的5个，清除多余的
                keys_to_remove = list(self._cached_icons.keys())[:-5]
                for key in keys_to_remove:
                    del self._cached_icons[key]
                    
                self._log_debug(f"清理了{len(keys_to_remove)}个过期缓存项")
                
        except Exception as e:
            self._log_warning(f"清理缓存失败: {e}")
    
    def _log_debug(self, message: str) -> None:
        """记录调试日志"""
        logger = logging.getLogger('Haropet.SystemTray')
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(message)
    

    

    
    def _draw_professional_haro_icon(self, painter: QPainter, pet_state: str = "normal") -> None:
        """
        绘制专业的哈罗托盘图标（使用IconManager）
        
        使用IconManager来获取和绘制图标，避免重复代码。
        
        Args:
            painter: QPainter对象，用于执行绘制操作
            pet_state: 宠物状态（normal, happy, excited, sleeping）
        """
        try:
            # 使用IconManager获取图标
            icon = self.icon_manager.get_icon(pet_state)
            
            # 绘制图标
            pixmap = icon.pixmap(48, 48)
            painter.drawPixmap(0, 0, pixmap)
            
        except Exception as e:
            self._log_error(f"绘制图标失败: {e}")
            # 回退到简单绘制
            self._draw_simple_haro_icon(painter, pet_state)
    
    def _draw_simple_haro_icon(self, painter: QPainter, pet_state: str = "normal") -> None:
        """
        简单绘制哈罗图标（回退方案）
        
        Args:
            painter: QPainter对象
            pet_state: 宠物状态
        """
        w, h = 48, 48
        center_x, center_y = w // 2, h // 2
        
        # 绘制简单的圆形图标
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80, 180, 80))
        painter.drawEllipse(center_x - 16, center_y - 16, 32, 32)
    

    
    def _setup_menu(self) -> None:
        """
        设置系统托盘菜单
        
        创建完整的交互式菜单，包含状态显示、功能选项和退出选项。
        所有菜单项都连接到对应的处理函数。
        
        Returns:
            None
            
        Raises:
            RuntimeError: 如果QMenu创建失败
        """
        try:
            self.menu = QMenu()
            
            self.status_action = QAction("哈罗haro", self)
            self.status_action.setEnabled(False)
            self.menu.addAction(self.status_action)
        
            self.menu.addSeparator()
            
            self.follow_action = QAction("跟随指针", self)
            self.follow_action.setCheckable(True)
            self.follow_action.setChecked(False)
            self.menu.addAction(self.follow_action)
            
            self.menu.addSeparator()
            
            self.greet_action = QAction("🗣️ 打招呼", self)
            self.menu.addAction(self.greet_action)
            
            self.menu.addSeparator()
            
            self.user_action = QAction("👤 用户设置", self)
            self.menu.addAction(self.user_action)
            
            self.menu.addSeparator()
            
            self.about_action = QAction("ℹ️ 关于", self)
            self.menu.addAction(self.about_action)
            
            self.menu.addSeparator()
            
            self.quit_action = QAction("❌ 退出", self)
            self.menu.addAction(self.quit_action)
            
            self.setContextMenu(self.menu)
            
        except Exception as e:
            self._log_error(f"设置菜单失败: {e}")
            raise RuntimeError(f"无法创建系统托盘菜单: {e}") from e
    
    def _setup_connections(self) -> None:
        """连接信号和槽"""
        try:
            # 连接菜单动作
            self.follow_action.toggled.connect(self._toggle_follow)
            self.greet_action.triggered.connect(self._show_greet)
            self.user_action.triggered.connect(self._show_user_panel)
            self.about_action.triggered.connect(self._show_about)
            self.quit_action.triggered.connect(self._quit_app)
            
            if self.pet is not None:
                self.pet.state_changed.connect(self._update_status)
                # 监听宠物状态变化，更新图标
                self.pet.state_changed.connect(self._on_pet_state_changed)
                
        except Exception as e:
            self._log_error(f"设置信号连接失败: {e}")
            # 即使信号连接失败，也应该让托盘能够基本工作
    
    def update_icon_state(self, pet_state: str = "normal") -> None:
        """
        更新托盘图标状态
        
        根据宠物的不同状态切换对应的图标，支持多种状态变化。
        
        Args:
            pet_state: 宠物状态（normal, happy, excited, sleeping等）
        """
        try:
            # 首先尝试使用现有图标文件中的不同尺寸或状态
            icon_file_path = self._get_state_icon_file_path(pet_state)
            if icon_file_path and os.path.exists(icon_file_path):
                try:
                    icon = QIcon(icon_file_path)
                    if not icon.isNull():
                        self.setIcon(icon)
                        self._log_debug(f"成功加载状态图标: {pet_state} from {icon_file_path}")
                        return
                except Exception as e:
                    self._log_warning(f"加载状态图标失败: {e}")
            
            # 使用IconManager获取状态图标
            icon = self.icon_manager.get_icon(pet_state)
            if not icon.isNull():
                self.setIcon(icon)
                self._log_debug(f"使用IconManager图标: {pet_state}")
                return
            
            # 回退到传统绘制
            self._create_icon_traditional_for_state(pet_state)
            
        except Exception as e:
            self._log_error(f"更新图标状态失败: {e}")
            # 使用回退图标
            self.setIcon(self._create_fallback_icon())
    
    def _get_state_icon_file_path(self, pet_state: str) -> Optional[str]:
        """
        获取特定状态的图标文件路径
        
        Args:
            pet_state: 宠物状态
            
        Returns:
            状态图标文件路径，如果不存在则返回None
        """
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 状态图标文件命名规则 - 支持ICO和PNG格式
        state_icon_names = {
            "normal": ["new_haro_icon.png", "icon.png", "icon.ico", "haropet.png", "haropet.ico"],
            "happy": ["icon_happy.png", "icon_happy.ico", "haropet_happy.png", "haropet_happy.ico"],
            "excited": ["icon_excited.png", "icon_excited.ico", "haropet_excited.png", "haropet_excited.ico"],
            "sleeping": ["icon_sleeping.png", "icon_sleeping.ico", "haropet_sleeping.png", "haropet_sleeping.ico"],
        }
        
        # 获取可能的状态图标文件列表
        possible_names = state_icon_names.get(pet_state, state_icon_names["normal"])
        
        for name in possible_names:
            icon_path = os.path.join(current_dir, name)
            if os.path.exists(icon_path):
                return icon_path
        
        return None
    
    def _create_icon_traditional_for_state(self, pet_state: str) -> None:
        """为特定状态创建传统图标（回退方案）"""
        try:
            pixmap = QPixmap(48, 48)
            if pixmap.isNull():
                raise ValueError("无法创建QPixmap对象")
            
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            if not painter.isActive():
                raise RuntimeError("QPainter无法激活")
                
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 使用状态特定的绘制方法
            self._draw_haro_to_painter(painter, pet_state)
            
            painter.end()
            self.setIcon(QIcon(pixmap))
            self._log_debug(f"创建传统状态图标: {pet_state}")
            
        except Exception as e:
            self._log_error(f"创建状态图标失败: {e}")
            self.setIcon(self._create_fallback_icon())
        finally:
            if 'painter' in locals() and painter.isActive():
                painter.end()
    
    def _on_pet_state_changed(self, state) -> None:
        """
        处理宠物状态变化，更新图标
        
        Args:
            state: 宠物的新状态
        """
        try:
            # 将宠物状态映射到图标状态
            state_map = {
                0: "normal",   # STATE_NORMAL
                1: "happy",    # STATE_HAPPY
                2: "excited",  # STATE_EXCITED
                3: "sleeping"  # STATE_SLEEPING
            }
            
            icon_state = state_map.get(state, "normal")
            self.update_icon_state(icon_state)
            
        except Exception as e:
            self._log_error(f"处理宠物状态变化失败: {e}")
    
    def _toggle_follow(self) -> None:
        """切换跟随模式，包含错误处理"""
        if self.pet is None:
            self._log_warning("宠物对象不可用，无法切换跟随模式")
            # 重置复选框状态
            self.follow_action.setChecked(False)
            return
        
        try:
            self.pet.set_follow_enabled(self.follow_action.isChecked())
        except Exception as e:
            self._log_error(f"切换跟随模式失败: {e}")
            # 显示用户友好的错误提示
            QMessageBox.warning(None, "操作失败", "无法切换跟随模式，请重试")
    
    def _update_status(self, state) -> None:
        """更新状态显示，包含错误处理"""
        try:
            if self.status_action is None:
                return  # 如果菜单还未初始化，跳过更新
                
            state_names = {
                HaroPet.STATE_NORMAL: "哈罗：正常",
                HaroPet.STATE_BACK: "哈罗：背对",
            }
            status_text = state_names.get(state, "哈罗：正常")
            self.status_action.setText(status_text)
            
        except Exception as e:
            self._log_error(f"更新状态显示失败: {e}")
            # 静默失败，不影响其他功能
    
    def _show_about(self) -> None:
        """
        显示关于对话框
        
        显示哈罗桌面宠物的版本信息、介绍和作者信息。
        使用QMessageBox创建模态对话框。
        
        Returns:
            None
            
        Note:
            如果self.pet为None，会使用None作为父窗口。
            错误会在_show_user_panel函数中处理。
        """
        about_text = (
            "哈罗 v1.0.0\n\n"
            "以《机动战士高达》中的哈罗(Haro)为原型\n\n"
            "作者：opfer\n"
            "基于Python和PyQt5实现"
        )
        
        try:
            parent_widget = self.pet if self.pet is not None else None
            QMessageBox.about(
                parent_widget,
                "关于哈罗桌面宠物",
                about_text
            )
        except Exception as e:
            self._log_error(f"显示关于对话框失败: {e}")
            # 显示错误提示但不影响其他功能
            QMessageBox.critical(None, "错误", f"无法显示关于信息: {str(e)}")
    
    def _show_greet(self) -> None:
        """显示问候动画，包含错误处理"""
        if self.pet is None:
            self._log_warning("宠物对象不可用，无法执行问候")
            return
        
        try:
            self.pet.greet()
        except Exception as e:
            self._log_error(f"问候动画失败: {e}")
            # 显示错误提示但不影响其他功能
            QMessageBox.information(None, "提示", "问候功能暂时不可用，请稍后重试")
    
    def _show_user_panel(self) -> None:
        """
        显示用户设置面板
        
        打开用户设置对话框，允许用户修改哈罗的配置。
        如果用户点击确定按钮，会触发问候动画作为确认反馈。
        
        Returns:
            None
            
        Raises:
            Exception: 如果用户面板创建失败或执行失败
        """
        try:
            panel = UserPanel(None)
            result = panel.exec_()
            
            if result == QDialog.Accepted:
                # 用户确认了设置，执行问候动画
                if self.pet is not None:
                    self.pet.greet()
                else:
                    self._log_warning("无法执行问候：宠物对象不可用")
            
        except Exception as e:
            import traceback
            self._log_error(f"打开用户面板失败: {e}")
            self._log_debug(f"错误详情: {traceback.format_exc()}")
            
            # 显示用户友好的错误提示
            error_message = f"无法打开设置面板: {str(e)}"
            QMessageBox.critical(None, "设置错误", error_message)
    
    def _log_debug(self, message: str) -> None:
        """记录调试日志"""
        logger = logging.getLogger('Haropet.SystemTray')
        logger.debug(message)
    
    def _cleanup_resources(self) -> None:
        """
        清理系统托盘资源
        
        释放缓存、停止计时器、清理图标资源等。
        确保应用程序退出时没有资源泄漏。
        """
        try:
            # 清理缓存
            self._cached_icons.clear()
            self._cached_states.clear()
            
            # 停止自动清理计时器
            if hasattr(self, '_cleanup_timer') and self._cleanup_timer:
                self._cleanup_timer.stop()
                self._cleanup_timer.deleteLater()
            
            # 清理用户面板
            if self._user_panel:
                self._user_panel.close()
                self._user_panel = None
            
            self._log_debug("系统托盘资源清理完成")
            
        except Exception as e:
            # 资源清理失败不应该阻止程序退出
            logger = logging.getLogger('Haropet.SystemTray')
            logger.warning(f"资源清理失败: {e}")
    
    def closeEvent(self, event) -> None:
        """
        系统托盘关闭事件处理
        
        确保在关闭时清理所有资源。
        
        Args:
            event: 关闭事件
        """
        try:
            # 清理资源
            self._cleanup_resources()
            
            # 调用父类关闭事件
            super().closeEvent(event)
            
        except Exception as e:
            logger = logging.getLogger('Haropet.SystemTray')
            logger.error(f"关闭事件处理失败: {e}")
            # 即使关闭事件处理失败，也要确保资源被清理
            try:
                self._cleanup_resources()
            except:
                pass  # 忽略清理过程中的错误
    
    def _quit_app(self) -> None:
        """退出应用程序，包含错误处理"""
        try:
            if self.pet is not None:
                self.pet.save_position()
        except Exception as e:
            self._log_error(f"保存位置失败: {e}")
            # 即使保存失败，也应该退出应用程序
            pass
        finally:
            QApplication.quit()

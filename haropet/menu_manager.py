# -*- coding: utf-8 -*-
"""
菜单管理器
负责系统托盘菜单的统一管理
"""

import logging
from typing import Optional, Callable
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon
from PyQt5.QtCore import Qt


class MenuManager:
    """
    菜单管理器类
    负责统一管理系统托盘菜单
    """
    
    def __init__(self, tray_icon: QSystemTrayIcon, logger_name: str = "Haropet.MenuManager"):
        self.tray_icon = tray_icon
        self.logger = logging.getLogger(logger_name)
        self.menu = None
        self.actions = {}
    
    def create_menu(self, follow_initial_state: bool = False) -> None:
        """
        创建系统托盘菜单
        
        Args:
            follow_initial_state: 跟随模式的初始状态
        """
        try:
            self.menu = QMenu()
            
            # 创建菜单动作
            self._create_menu_actions(follow_initial_state)
            
            # 设置菜单
            self.tray_icon.setContextMenu(self.menu)
            
        except Exception as e:
            self.logger.error(f"创建菜单失败: {e}")
            raise RuntimeError(f"无法创建系统托盘菜单: {e}") from e
    
    def _create_menu_actions(self, follow_initial_state: bool) -> None:
        """
        创建菜单动作
        
        Args:
            follow_initial_state: 跟随模式的初始状态
        """
        # 状态显示动作
        self.actions['status'] = QAction("哈罗haro", self.menu)
        self.actions['status'].setEnabled(False)
        self.menu.addAction(self.actions['status'])
        
        self.menu.addSeparator()
        
        # 跟随指针动作
        self.actions['follow'] = QAction("跟随指针", self.menu)
        self.actions['follow'].setCheckable(True)
        self.actions['follow'].setChecked(follow_initial_state)
        self.menu.addAction(self.actions['follow'])
        
        self.menu.addSeparator()
        
        # 打招呼动作
        self.actions['greet'] = QAction("🗣️ 打招呼", self.menu)
        self.menu.addAction(self.actions['greet'])
        
        self.menu.addSeparator()
        
        # 用户设置动作
        self.actions['user'] = QAction("👤 用户设置", self.menu)
        self.menu.addAction(self.actions['user'])
        
        self.menu.addSeparator()
        
        # 关于动作
        self.actions['about'] = QAction("ℹ️ 关于", self.menu)
        self.menu.addAction(self.actions['about'])
        
        self.menu.addSeparator()
        
        # 退出动作
        self.actions['quit'] = QAction("❌ 退出", self.menu)
        self.menu.addAction(self.actions['quit'])
    
    def connect_actions(self, 
                       follow_callback: Callable,
                       greet_callback: Callable,
                       user_callback: Callable,
                       about_callback: Callable,
                       quit_callback: Callable) -> None:
        """
        连接菜单动作的回调函数
        
        Args:
            follow_callback: 跟随指针动作的回调
            greet_callback: 打招呼动作的回调
            user_callback: 用户设置动作的回调
            about_callback: 关于动作的回调
            quit_callback: 退出动作的回调
        """
        try:
            # 连接菜单动作
            self.actions['follow'].toggled.connect(follow_callback)
            self.actions['greet'].triggered.connect(greet_callback)
            self.actions['user'].triggered.connect(user_callback)
            self.actions['about'].triggered.connect(about_callback)
            self.actions['quit'].triggered.connect(quit_callback)
            
        except Exception as e:
            self.logger.error(f"连接菜单动作失败: {e}")
    
    def update_status(self, status_text: str) -> None:
        """
        更新状态显示
        
        Args:
            status_text: 要显示的状态文本
        """
        try:
            if 'status' in self.actions and self.actions['status']:
                self.actions['status'].setText(status_text)
        except Exception as e:
            self.logger.error(f"更新状态显示失败: {e}")
    
    def update_follow_state(self, is_following: bool) -> None:
        """
        更新跟随状态
        
        Args:
            is_following: 是否处于跟随状态
        """
        try:
            if 'follow' in self.actions and self.actions['follow']:
                self.actions['follow'].setChecked(is_following)
        except Exception as e:
            self.logger.error(f"更新跟随状态失败: {e}")

# -*- coding: utf-8 -*-
"""
用户设置面板
提供用户名称编辑和用户中心功能
"""

import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from haropet.config_manager import config_manager


class UserPanel(QDialog):
    
    _logger = logging.getLogger('Haropet.UserPanel')
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户中心")
        self.setFixedSize(360, 220)
        self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #50b450;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                color: #333333;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #8cdc78;
            }
            QPushButton {
                min-width: 80px;
                min-height: 32px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton#save_button {
                background-color: #50b450;
                color: white;
                border: none;
            }
            QPushButton#save_button:hover {
                background-color: #64c864;
            }
            QPushButton#cancel_button {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
            }
            QPushButton#cancel_button:hover {
                background-color: #cccccc;
            }
        """)
        
        self._user_name = ""
        self._load_user_name()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #50b450; border-radius: 8px;")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 12, 15, 12)
        
        title_label = QLabel("👤 用户中心")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("编辑您的个人名称")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.85);")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        name_section_layout = QVBoxLayout()
        name_section_layout.setSpacing(8)
        
        name_title = QLabel("您的名称")
        name_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #666666;")
        name_section_layout.addWidget(name_title)
        
        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        
        self._name_edit = QLineEdit()
        self._name_edit.setText(self._user_name)
        self._name_edit.setPlaceholderText("输入您的名称")
        self._name_edit.setMaxLength(30)
        self._name_edit.setFocus()
        name_layout.addWidget(self._name_edit)
        
        layout.addLayout(name_section_layout)
        layout.addLayout(name_layout)
        
        preview_label = QLabel(f"打招呼时显示：你好，我是{self._user_name or '哈罗'}！")
        preview_label.setStyleSheet("font-size: 12px; color: #888888;")
        preview_label.setWordWrap(True)
        self._preview_label = preview_label
        layout.addWidget(preview_label)
        
        self._name_edit.textChanged.connect(self._update_preview)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self._cancel_button = QPushButton("取消")
        self._cancel_button.setObjectName("cancel_button")
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_button)
        
        self._save_button = QPushButton("保存")
        self._save_button.setObjectName("save_button")
        self._save_button.clicked.connect(self._save_user_name)
        button_layout.addWidget(self._save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _update_preview(self, text):
        display_name = text.strip() if text.strip() else "哈罗"
        self._preview_label.setText(f"打招呼时显示：你好，我是{display_name}！")
    
    def _get_config_dir(self):
        """获取适合当前系统的配置目录"""
        # 尝试多个备选目录
        config_dirs = []
        
        if os.name == 'nt':  # Windows
            # 首选：APPDATA目录
            appdata = os.environ.get('APPDATA')
            if appdata:
                config_dirs.append(os.path.join(appdata, 'Haropet'))
            # 备选：文档目录
            docs = os.environ.get('DOCUMENTS', os.path.join(os.path.expanduser("~"), 'Documents'))
            config_dirs.append(os.path.join(docs, 'Haropet'))
            # 备选：应用程序当前目录
            config_dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
        elif os.name == 'posix':  # Linux/Mac
            # 首选：用户主目录
            config_dirs.append(os.path.join(os.path.expanduser("~"), '.haropet'))
            # 备选：应用程序当前目录
            config_dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
        else:
            # 其他系统：当前目录
            config_dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))
        
        # 选择第一个可写的目录
        for config_dir in config_dirs:
            try:
                # 尝试创建目录
                os.makedirs(config_dir, exist_ok=True)
                # 检查权限
                test_file = os.path.join(config_dir, 'test_permission.txt')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                return config_dir
            except:
                continue
        
        # 如果所有目录都失败，返回当前目录
        return os.path.dirname(os.path.abspath(__file__))
    
    def _check_permissions(self, directory):
        """检查目录权限"""
        try:
            # 检查是否可写
            test_file = os.path.join(directory, 'test_permission.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except:
            return False
    
    def _load_user_name(self):
        config_dir = self._get_config_dir()
        config_file = os.path.join(config_dir, "user_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._user_name = config.get("user_name", "")
            except Exception as e:
                self._logger.warning(f"加载用户名失败: {e}")
                self._user_name = ""
    
    def _save_user_name(self):
        user_name = self._name_edit.text().strip()
        
        config_dir = self._get_config_dir()
        
        try:
            # 确保目录存在
            os.makedirs(config_dir, exist_ok=True)
            
            # 检查权限
            if not self._check_permissions(config_dir):
                self._logger.error(f"配置目录无写入权限: {config_dir}")
                QMessageBox.warning(self, "权限错误", "无法保存设置：配置目录无写入权限。请检查文件夹权限设置。")
                return
            
            config_file = os.path.join(config_dir, "user_config.json")
            config = {
                "user_name": user_name
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 更新ConfigManager中的内存数据，确保打招呼功能立即使用新名称
            config_manager.set_user_name(user_name)
            
            self.accept()
        except Exception as e:
            self._logger.error(f"保存用户名失败: {e}")
            error_msg = f"保存失败: {str(e)}\n\n请确保您有足够的权限访问用户目录。"
            QMessageBox.warning(self, "错误", error_msg)
    
    def get_user_name(self):
        return self._user_name or "用户"

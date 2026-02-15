# -*- coding: utf-8 -*-
"""
配置管理模块
统一管理应用配置和常量
"""

import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger('Haropet.ConfigManager')

class ConfigManager:
    """配置管理器，使用单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
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
                logger.info(f"选择配置目录: {config_dir}")
                return config_dir
            except Exception as e:
                logger.warning(f"配置目录不可用: {config_dir}, 错误: {e}")
                continue
        
        # 如果所有目录都失败，返回当前目录
        fallback_dir = os.path.dirname(os.path.abspath(__file__))
        logger.warning(f"所有配置目录都不可用，使用回退目录: {fallback_dir}")
        return fallback_dir
    
    def __init__(self):
        if self._initialized:
            return
        
        # 应用基本配置
        self.app_name = "哈罗桌面宠物"
        self.version = "1.0"
        self.author = "Haropet"
        
        # 窗口和宠物大小
        self.WINDOW_SIZE = 400
        self.PET_SIZE = 200
        
        # 动画相关常量
        self.TURN_ANIMATION_TOTAL_FRAMES = 16
        self.TURN_ANIMATION_DURATION = 800  # ms
        self.SWAY_DURATION = 40
        self.SWAY_AMPLITUDE = 15
        self.BUBBLE_DURATION = 2000  # ms
        
        # 跟随相关常量
        self.FOLLOW_DISTANCE_THRESHOLD_CLOSE = 100
        self.FOLLOW_DISTANCE_THRESHOLD_MEDIUM = 300
        self.FOLLOW_EASING_CLOSE = 0.05
        self.FOLLOW_EASING_MEDIUM = 0.03
        self.FOLLOW_EASING_FAR = 0.02
        self.MOUSE_MOVEMENT_THRESHOLD = 10
        self.FOLLOW_MARGIN = 50
        
        # 点击相关常量
        self.CLICK_DOUBLE_THRESHOLD = 0.5  # seconds
        self.CLICK_RESET_TIMEOUT = 1500  # ms
        self.CLICK_COUNT_FOR_TURN_AROUND = 3
        
        # 颜色配置
        self.COLORS = {
            "body": (80, 180, 80),
            "body_light": (140, 220, 120),
            "body_dark": (50, 140, 50),
            "eye": (200, 50, 50),
            "blush": (255, 150, 150, 80),
            "shadow": (0, 0, 0, 30),
            "text": (255, 255, 255)
        }
        
        # 用户配置文件路径 - 使用智能目录选择
        self._config_dir = self._get_config_dir()
        self._user_config_file = os.path.join(self._config_dir, "user_config.json")
        self._position_config_file = os.path.join(self._config_dir, "config.json")
        
        # 用户配置
        self.user_config = {
            "user_name": "用户",
            "follow_enabled": False,
            "auto_start": False,
            "sound_enabled": True
        }
        
        # 位置配置
        self.position_config = {
            "x": 100,
            "y": 100,
            "state": "normal"
        }
        
        # 初始化
        self._create_config_dir()
        self.load_config()
        
        self._initialized = True
    
    def _create_config_dir(self):
        """创建配置目录"""
        try:
            if not os.path.exists(self._config_dir):
                os.makedirs(self._config_dir)
                logger.info(f"创建配置目录: {self._config_dir}")
        except Exception as e:
            logger.error(f"创建配置目录失败: {e}")
    
    def load_config(self):
        """加载配置文件"""
        self._load_user_config()
        self._load_position_config()
    
    def _load_user_config(self):
        """加载用户配置"""
        try:
            if os.path.exists(self._user_config_file):
                with open(self._user_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.user_config.update(loaded_config)
                    logger.info(f"加载用户配置: {self._user_config_file}")
        except Exception as e:
            logger.error(f"加载用户配置失败: {e}")
    
    def _load_position_config(self):
        """加载位置配置"""
        try:
            if os.path.exists(self._position_config_file):
                with open(self._position_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.position_config.update(loaded_config)
                    logger.info(f"加载位置配置: {self._position_config_file}")
        except Exception as e:
            logger.error(f"加载位置配置失败: {e}")
    
    def save_user_config(self):
        """保存用户配置"""
        try:
            # 确保目录存在
            self._create_config_dir()
            
            # 使用临时文件写入，避免写入失败导致文件损坏
            temp_file = self._user_config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, ensure_ascii=False, indent=2)
            
            # 重命名临时文件为目标文件
            if os.path.exists(self._user_config_file):
                try:
                    os.remove(self._user_config_file)
                except Exception as e:
                    logger.warning(f"删除旧配置文件失败: {e}")
            
            os.rename(temp_file, self._user_config_file)
            logger.info(f"保存用户配置: {self._user_config_file}")
        except Exception as e:
            logger.error(f"保存用户配置失败: {e}")
    
    def save_position_config(self):
        """保存位置配置"""
        try:
            # 确保目录存在
            self._create_config_dir()
            
            # 使用临时文件写入，避免写入失败导致文件损坏
            temp_file = self._position_config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.position_config, f, ensure_ascii=False, indent=2)
            
            # 重命名临时文件为目标文件
            if os.path.exists(self._position_config_file):
                try:
                    os.remove(self._position_config_file)
                except Exception as e:
                    logger.warning(f"删除旧配置文件失败: {e}")
            
            os.rename(temp_file, self._position_config_file)
            logger.info(f"保存位置配置: {self._position_config_file}")
        except Exception as e:
            logger.error(f"保存位置配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.user_config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.user_config[key] = value
        self.save_user_config()
    
    def get_user_name(self) -> str:
        """获取用户名"""
        return self.user_config.get("user_name", "用户")
    
    def set_user_name(self, name: str):
        """设置用户名"""
        self.user_config["user_name"] = name
        self.save_user_config()
    
    def get_follow_enabled(self) -> bool:
        """获取跟随模式状态"""
        return self.user_config.get("follow_enabled", False)
    
    def set_follow_enabled(self, enabled: bool):
        """设置跟随模式状态"""
        self.user_config["follow_enabled"] = enabled
        self.save_user_config()
    
    def get_position(self) -> Dict[str, int]:
        """获取位置配置"""
        return {
            "x": self.position_config.get("x", 100),
            "y": self.position_config.get("y", 100)
        }
    
    def set_position(self, x: int, y: int):
        """设置位置配置"""
        self.position_config["x"] = x
        self.position_config["y"] = y
        self.save_position_config()
    
    def get_state(self) -> str:
        """获取宠物状态"""
        return self.position_config.get("state", "normal")
    
    def set_state(self, state: str):
        """设置宠物状态"""
        self.position_config["state"] = state
        self.save_position_config()
    
    def get_app_data_path(self) -> str:
        """获取应用数据路径"""
        return self._config_dir

# 创建全局配置管理器实例
config_manager = ConfigManager()

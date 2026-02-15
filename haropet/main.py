# -*- coding: utf-8 -*-
"""
哈罗桌面宠物 - 主程序入口
"""

import sys
import os
import logging
from typing import NoReturn

# 快速路径：首先检查命令行参数和基本环境
if len(sys.argv) > 1:
    # 处理命令行参数
    pass

# 延迟导入重量级模块
# 首先导入轻量级配置管理器
from haropet.config_manager import config_manager

# 设置日志（优化版）
def setup_logging():
    """设置日志系统"""
    try:
        # 使用更高效的日志配置
        log_file = os.path.join(os.path.dirname(__file__), 'haropet.log')
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', delay=True),  # 延迟创建文件
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger('Haropet')
    except Exception as e:
        # 如果日志配置失败，使用简单的控制台输出
        print(f"日志配置失败: {e}")
        return logging.getLogger('Haropet')

# 设置日志
logger = setup_logging()

# 延迟导入PyQt5模块
# 注意：在导入PyQt5之前，我们已经完成了所有轻量级的初始化工作



# 延迟导入PyQt5模块
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSharedMemory, QObject

class InstanceManager(QObject):
    """单实例管理器"""
    
    def __init__(self) -> None:
        super().__init__()
        self.shared_memory = QSharedMemory("Haropet_SingleInstance")
        self.is_primary_instance = self._check_instance()
    
    def _check_instance(self) -> bool:
        """检查是否已有一个实例在运行"""
        if self.shared_memory.isAttached():
            self.shared_memory.detach()
        
        if not self.shared_memory.create(1, QSharedMemory.ReadWrite):
            logger.warning("检测到另一个哈罗实例已在运行")
            return False
        
        logger.info("主实例启动成功")
        return True
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.shared_memory.isAttached():
            self.shared_memory.detach()
        logger.info("实例管理器清理完成")


def configure_application(app: QApplication) -> None:
    """配置应用程序基本设置"""
    # 使用配置管理器中的应用信息
    app.setApplicationName(config_manager.app_name)
    app.setApplicationDisplayName(config_manager.app_name)
    app.setApplicationVersion(config_manager.version)
    app.setOrganizationName(config_manager.author)
    app.setQuitOnLastWindowClosed(False)
    
    # 设置高DPI支持
    app.setAttribute(5)  # Qt.AA_EnableHighDpiScaling
    app.setAttribute(18)  # Qt.AA_UseHighDpiPixmaps


def preload_resources():
    """预加载资源（在后台线程中）"""
    try:
        import threading
        
        def _preload():
            """后台预加载函数"""
            try:
                # 预加载图标
                from haropet.icon_manager import IconManager
                icon_manager = IconManager()
                icon_manager.pre_cache_icons(["normal", "happy", "excited", "sleeping"])
                logger.info("资源预加载完成")
            except Exception as e:
                logger.error(f"资源预加载失败: {e}")
        
        # 创建后台线程
        preload_thread = threading.Thread(target=_preload, daemon=True)
        preload_thread.start()
        
    except Exception as e:
        logger.error(f"启动预加载线程失败: {e}")


def main() -> NoReturn:
    """主函数（优化版）"""
    try:
        # 快速路径：检查命令行参数
        if len(sys.argv) > 1:
            # 处理命令行参数
            pass
        
        # 检查单实例（轻量级操作）
        instance_manager = InstanceManager()
        # 临时禁用单实例检查，用于测试
        # if not instance_manager.is_primary_instance:
        #     logger.info("由于检测到已有实例，程序退出")
        #     sys.exit(1)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        configure_application(app)
        
        # 启动资源预加载（后台线程）
        preload_resources()
        
        # 延迟导入重量级组件
        from haropet.haro_pet import HaroPet
        from haropet.system_tray import HaroSystemTray
        
        # 初始化组件
        logger.info("正在初始化哈罗宠物...")
        pet = HaroPet()
        
        logger.info("正在初始化系统托盘...")
        tray = HaroSystemTray(pet)
        tray.show()
        
        logger.info("哈罗桌面宠物启动完成")
        
        # 运行应用程序
        exit_code = app.exec_()
        
        # 清理资源
        instance_manager.cleanup()
        
        logger.info(f"哈罗桌面宠物已关闭，退出代码: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.exception(f"应用程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

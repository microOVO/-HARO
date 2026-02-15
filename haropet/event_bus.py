# -*- coding: utf-8 -*-
"""
事件总线模块
实现组件间的解耦通信
"""

import logging
import threading
from typing import Callable, Dict, List, Any, Tuple

logger = logging.getLogger('Haropet.EventBus')

class EventBus:
    """事件总线，使用单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 事件订阅者字典
        # 格式: {event_type: [(callback, priority, unique_id), ...]}
        self._subscribers: Dict[str, List[Tuple[Callable, int, str]]] = {}
        
        # 用于生成唯一ID的计数器
        self._callback_id_counter = 0
        
        # 线程锁，确保线程安全
        self._lock = threading.RLock()
        
        self._initialized = True
    
    def subscribe(self, event_type: str, callback: Callable, priority: int = 0) -> str:
        """
        订阅事件
        
        :param event_type: 事件类型
        :param callback: 事件处理函数
        :param priority: 优先级，值越大优先级越高
        :return: 订阅ID，用于取消订阅
        """
        with self._lock:
            # 生成唯一ID
            self._callback_id_counter += 1
            callback_id = f"callback_{self._callback_id_counter}"
            
            # 添加到订阅者列表
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            self._subscribers[event_type].append((callback, priority, callback_id))
            
            # 按优先级排序
            self._subscribers[event_type].sort(key=lambda x: x[1], reverse=True)
            
            logger.debug(f"订阅事件: {event_type}, 回调ID: {callback_id}, 优先级: {priority}")
            return callback_id
    
    def unsubscribe(self, callback_id: str) -> bool:
        """
        取消订阅
        
        :param callback_id: 订阅ID
        :return: 是否取消成功
        """
        with self._lock:
            for event_type, subscribers in self._subscribers.items():
                for i, (_, _, id) in enumerate(subscribers):
                    if id == callback_id:
                        del subscribers[i]
                        logger.debug(f"取消订阅事件: {event_type}, 回调ID: {callback_id}")
                        # 如果该事件类型没有订阅者了，删除该事件类型
                        if not subscribers:
                            del self._subscribers[event_type]
                        return True
            
            logger.warning(f"未找到订阅ID: {callback_id}")
            return False
    
    def unsubscribe_by_event_type(self, event_type: str, callback: Callable) -> bool:
        """
        取消特定事件类型的订阅
        
        :param event_type: 事件类型
        :param callback: 事件处理函数
        :return: 是否取消成功
        """
        with self._lock:
            if event_type not in self._subscribers:
                logger.warning(f"未找到事件类型: {event_type}")
                return False
            
            original_length = len(self._subscribers[event_type])
            self._subscribers[event_type] = [
                (cb, prio, id) for cb, prio, id in self._subscribers[event_type] 
                if cb is not callback
            ]
            
            # 如果该事件类型没有订阅者了，删除该事件类型
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
            
            is_removed = len(self._subscribers.get(event_type, [])) < original_length
            if is_removed:
                logger.debug(f"取消订阅事件类型: {event_type}, 回调: {callback.__name__}")
            else:
                logger.warning(f"未找到回调函数: {callback.__name__} 订阅事件类型: {event_type}")
            
            return is_removed
    
    def publish(self, event_type: str, **kwargs) -> None:
        """
        发布事件
        
        :param event_type: 事件类型
        :param kwargs: 事件数据
        """
        logger.debug(f"发布事件: {event_type}, 数据: {kwargs}")
        
        with self._lock:
            subscribers = self._subscribers.get(event_type, [])
            # 创建订阅者列表的副本，以防止在处理事件时修改列表
            subscribers_copy = subscribers.copy()
        
        # 在锁外执行回调，避免死锁
        for callback, _, callback_id in subscribers_copy:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"处理事件 {event_type} 时出错，回调ID: {callback_id}: {e}", exc_info=True)
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """
        获取订阅者数量
        
        :param event_type: 事件类型，如果为None则返回所有事件类型的订阅者总数
        :return: 订阅者数量
        """
        with self._lock:
            if event_type is None:
                return sum(len(subscribers) for subscribers in self._subscribers.values())
            return len(self._subscribers.get(event_type, []))
    
    def list_event_types(self) -> List[str]:
        """
        列出所有事件类型
        
        :return: 事件类型列表
        """
        with self._lock:
            return list(self._subscribers.keys())
    
    def clear(self, event_type: str = None) -> None:
        """
        清除事件订阅
        
        :param event_type: 事件类型，如果为None则清除所有事件订阅
        """
        with self._lock:
            if event_type is None:
                self._subscribers.clear()
                logger.info("清除所有事件订阅")
            else:
                if event_type in self._subscribers:
                    del self._subscribers[event_type]
                    logger.info(f"清除事件类型 {event_type} 的所有订阅")

# 创建全局事件总线实例
event_bus = EventBus()

# 常用事件类型常量
class EventTypes:
    """事件类型常量"""
    PET_STATE_CHANGED = "pet_state_changed"
    PET_GREETED = "pet_greeted"
    FOLLOW_MODE_CHANGED = "follow_mode_changed"
    PET_MOVED = "pet_moved"
    APP_QUIT = "app_quit"
    USER_NAME_UPDATED = "user_name_updated"
    ICON_UPDATED = "icon_updated"
    MENU_ACTION_TRIGGERED = "menu_action_triggered"
    ANIMATION_STARTED = "animation_started"
    ANIMATION_ENDED = "animation_ended"
    BUBBLE_SHOWN = "bubble_shown"
    BUBBLE_HIDDEN = "bubble_hidden"

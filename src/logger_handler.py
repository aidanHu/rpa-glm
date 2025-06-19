"""
GUI日志处理器
将loguru日志输出重定向到GUI界面
"""

import logging
from loguru import logger
from PyQt6.QtCore import QObject, pyqtSignal


class GuiLogHandler(QObject):
    """GUI日志处理器"""
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
    def emit(self, message):
        """发射日志信号"""
        try:
            # loguru会传递已格式化的字符串消息
            self.log_signal.emit(str(message).strip())
        except Exception as e:
            # 静默忽略错误，避免递归日志
            pass


# 全局日志处理器实例
gui_log_handler = GuiLogHandler()


def setup_gui_logging():
    """设置GUI日志"""
    # 移除默认的控制台输出
    logger.remove()
    
    # 添加GUI处理器到loguru
    logger.add(
        gui_log_handler.emit,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    ) 
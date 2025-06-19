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
        
    def emit(self, record):
        """发射日志信号"""
        try:
            message = record.get('message', '')
            level = record.get('level', {}).get('name', 'INFO')
            time_str = record.get('time', '').strftime('%H:%M:%S') if record.get('time') else ''
            
            formatted_message = f"[{time_str}] {level}: {message}"
            self.log_signal.emit(formatted_message)
        except Exception:
            pass


# 全局日志处理器实例
gui_log_handler = GuiLogHandler()


def setup_gui_logging():
    """设置GUI日志"""
    # 添加GUI处理器到loguru
    logger.add(
        gui_log_handler.emit,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    ) 
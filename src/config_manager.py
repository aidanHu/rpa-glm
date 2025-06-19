"""
配置管理器
负责加载和管理用户配置和网页元素配置
"""

import yaml
import os
from pathlib import Path
from loguru import logger


class ConfigManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.user_config = None
        self.web_elements_config = None
        self.load_web_elements_config()
    
    def load_web_elements_config(self):
        """加载网页元素配置"""
        try:
            web_elements_path = self.project_root / "config" / "web_elements.yaml"
            with open(web_elements_path, 'r', encoding='utf-8') as f:
                self.web_elements_config = yaml.safe_load(f)
            logger.info("网页元素配置加载成功")
        except Exception as e:
            logger.error(f"网页元素配置加载失败: {e}")
            raise
    
    def set_user_config(self, config_data):
        """直接设置用户配置数据（从GUI传入）"""
        self.user_config = config_data
        logger.info("用户配置已从GUI更新")
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            'root_directory': '',
            'prompt_column': 3,
            'status_column': 5,
            'completed_status': '已生成视频',
            'bit_browser_id': '',
            'headless': False,
            'timeout': 30000,
            'video_generation_timeout': 300000,
            'video_options': {
                'quality': '速度更快',
                'framerate': '帧率60',
                'resolution': '4k'
            },
            'smart_delay': {
                'min': 1.0,
                'max': 2.0,
                'upload_after': 2.0,
                'input_after': 1.0,
                'click_after': 1.5
            },
            'download_timeout': 60
        }
    
    def get_user_config(self, key=None):
        """获取用户配置"""
        if self.user_config is None:
            self.user_config = self.get_default_config()
        
        if key:
            return self.user_config.get(key)
        return self.user_config
    
    def get_web_element(self, element_path):
        """
        获取网页元素配置
        element_path: 元素路径，如 'elements.creation_history_btn'
        """
        keys = element_path.split('.')
        config = self.web_elements_config
        
        for key in keys:
            config = config.get(key)
            if config is None:
                logger.error(f"未找到元素配置: {element_path}")
                return None
        
        return config
    
    def get_target_url(self):
        """获取目标网站URL"""
        return self.web_elements_config.get('target_url')
    
    def get_wait_time(self, wait_type):
        """获取等待时间配置"""
        return self.web_elements_config.get('wait_times', {}).get(wait_type, 2000)
    
    def get_status_text(self, status_type):
        """获取状态文本配置"""
        return self.web_elements_config.get('status_texts', {}).get(status_type)
    
    def get_smart_delay(self, delay_type=None):
        """
        获取智能延时配置
        delay_type: 延时类型 ('upload_after', 'input_after', 'click_after') 或 None(随机延时)
        """
        import random
        
        smart_delay_config = self.get_user_config('smart_delay')
        if not smart_delay_config:
            # 默认配置
            smart_delay_config = {
                'min': 1.0,
                'max': 2.0,
                'upload_after': 2.0,
                'input_after': 1.0,
                'click_after': 1.5
            }
        
        if delay_type and delay_type in smart_delay_config:
            return smart_delay_config[delay_type]
        else:
            # 返回随机延时
            min_delay = smart_delay_config.get('min', 1.0)
            max_delay = smart_delay_config.get('max', 2.0)
            return random.uniform(min_delay, max_delay)
    
    def validate_root_directory(self):
        """验证根目录是否存在"""
        root_dir = self.get_user_config('root_directory')
        if not root_dir or not os.path.exists(root_dir):
            logger.error(f"根目录不存在或未设置: {root_dir}")
            return False
        return True


# 全局配置管理器实例
config_manager = ConfigManager() 
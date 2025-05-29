"""
任务处理器
负责协调整个自动化流程，管理任务队列和执行流程
"""

import asyncio
from typing import List, Dict
from loguru import logger
from src.config_manager import config_manager
from src.file_manager import file_manager
from src.browser_controller import browser_controller


class TaskProcessor:
    def __init__(self):
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
    
    async def initialize(self):
        """初始化任务处理器"""
        try:
            # 验证配置
            if not config_manager.validate_root_directory():
                raise Exception("根目录配置无效")
            
            # 初始化浏览器
            await browser_controller.initialize()
            
            # 导航到目标网站
            await browser_controller.navigate_to_target()
            
            # 设置初始参数
            await browser_controller.setup_initial_settings()
            
            logger.info("任务处理器初始化完成")
            
        except Exception as e:
            logger.error(f"任务处理器初始化失败: {e}")
            await self.cleanup()
            raise
    
    async def process_all_tasks(self):
        """处理所有任务"""
        try:
            # 获取所有任务文件夹
            task_folders = file_manager.get_all_task_folders()
            
            if not task_folders:
                logger.warning("未找到任何任务文件夹")
                return
            
            logger.info(f"找到 {len(task_folders)} 个任务文件夹，开始处理...")
            
            # 逐个处理文件夹
            for folder_path in task_folders:
                await self.process_folder_tasks(folder_path)
            
            # 输出最终统计
            self.print_final_statistics()
            
        except Exception as e:
            logger.error(f"处理所有任务失败: {e}")
            raise
    
    async def process_folder_tasks(self, folder_path: str):
        """处理单个文件夹中的所有任务"""
        try:
            logger.info(f"开始处理文件夹: {folder_path}")
            
            # 获取待处理任务
            pending_tasks = file_manager.get_pending_tasks(folder_path)
            
            if not pending_tasks:
                logger.info(f"文件夹 {folder_path} 中没有待处理任务")
                return
            
            logger.info(f"文件夹 {folder_path} 中有 {len(pending_tasks)} 个待处理任务")
            self.total_tasks += len(pending_tasks)
            
            # 逐个处理任务
            for task in pending_tasks:
                success = await self.process_single_task(folder_path, task)
                
                if success:
                    self.completed_tasks += 1
                    logger.info(f"任务完成: {task['image_index']} - {task['prompt'][:50]}...")
                else:
                    self.failed_tasks += 1
                    logger.error(f"任务失败: {task['image_index']} - {task['prompt'][:50]}...")
                
                # 任务间智能延时，避免请求过于频繁
                delay_time = config_manager.get_smart_delay()
                logger.debug(f"任务间延时: {delay_time:.2f}秒")
                await asyncio.sleep(delay_time)
            
            logger.info(f"文件夹 {folder_path} 处理完成")
            
        except Exception as e:
            logger.error(f"处理文件夹任务失败: {e}")
    
    async def process_single_task(self, folder_path: str, task: Dict) -> bool:
        """
        处理单个任务
        返回是否成功
        """
        try:
            logger.info(f"处理任务: 图片 {task['image_index']} - {task['prompt']}")
            
            # 使用浏览器控制器处理任务
            video_url = await browser_controller.process_single_task(
                task['image_path'], 
                task['prompt']
            )
            
            if video_url:
                # 下载并保存视频
                video_path = file_manager.save_video_file(
                    video_url, 
                    folder_path, 
                    task['image_index'],
                    task['prompt']
                )
                
                if video_path:
                    # 更新Excel状态
                    file_manager.update_task_status(
                        folder_path, 
                        task['excel_row']
                    )
                    
                    logger.info(f"任务完成: 视频已保存到 {video_path}")
                    return True
                else:
                    logger.error("视频下载失败")
                    return False
            else:
                logger.error("未获取到视频链接")
                return False
                
        except Exception as e:
            logger.error(f"处理单个任务失败: {e}")
            return False
    
    def print_final_statistics(self):
        """打印最终统计信息"""
        logger.info("=" * 50)
        logger.info("任务处理完成统计:")
        logger.info(f"总任务数: {self.total_tasks}")
        logger.info(f"成功完成: {self.completed_tasks}")
        logger.info(f"失败任务: {self.failed_tasks}")
        
        if self.total_tasks > 0:
            success_rate = (self.completed_tasks / self.total_tasks) * 100
            logger.info(f"成功率: {success_rate:.1f}%")
        
        logger.info("=" * 50)
    
    async def cleanup(self):
        """清理资源"""
        try:
            await browser_controller.cleanup()
            logger.info("任务处理器清理完成")
            
        except Exception as e:
            logger.error(f"清理任务处理器失败: {e}")


# 全局任务处理器实例
task_processor = TaskProcessor() 
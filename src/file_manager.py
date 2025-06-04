"""
文件管理器
负责处理Excel文件读写、图片文件扫描等文件操作
"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from loguru import logger
from src.config_manager import config_manager


class FileManager:
    def __init__(self):
        self.root_directory = config_manager.get_user_config('root_directory')
        self.prompt_column = config_manager.get_user_config('prompt_column')
        self.status_column = config_manager.get_user_config('status_column')
        self.completed_status = config_manager.get_user_config('completed_status')
    
    def find_excel_file(self, folder_path: str) -> Optional[str]:
        """
        在文件夹中查找Excel文件
        返回Excel文件的完整路径，如果没找到返回None
        """
        try:
            excel_extensions = ['.xlsx', '.xls']
            for filename in os.listdir(folder_path):
                if any(filename.lower().endswith(ext) for ext in excel_extensions):
                    excel_path = os.path.join(folder_path, filename)
                    logger.debug(f"找到Excel文件: {excel_path}")
                    return excel_path
            
            logger.warning(f"文件夹 {folder_path} 中未找到Excel文件")
            return None
            
        except Exception as e:
            logger.error(f"查找Excel文件失败: {e}")
            return None
    
    def get_all_task_folders(self) -> List[str]:
        """获取所有任务文件夹"""
        try:
            folders = []
            for item in os.listdir(self.root_directory):
                folder_path = os.path.join(self.root_directory, item)
                if os.path.isdir(folder_path):
                    # 检查文件夹中是否有Excel文件
                    excel_file = self.find_excel_file(folder_path)
                    if excel_file:
                        folders.append(folder_path)
            
            logger.info(f"找到 {len(folders)} 个任务文件夹")
            return folders
            
        except Exception as e:
            logger.error(f"获取任务文件夹失败: {e}")
            return []
    
    def get_images_in_folder(self, folder_path: str) -> List[Tuple[int, str]]:
        """
        获取文件夹中的图片文件，按序号排序
        返回: [(序号, 图片路径), ...]
        """
        try:
            images = []
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
            
            for filename in os.listdir(folder_path):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    # 提取文件名前面的序号
                    try:
                        index = int(filename.split('_')[0])
                        image_path = os.path.join(folder_path, filename)
                        images.append((index, image_path))
                    except (ValueError, IndexError):
                        logger.warning(f"图片文件名格式不正确，跳过: {filename}")
            
            # 按序号排序
            images.sort(key=lambda x: x[0])
            logger.info(f"文件夹 {folder_path} 中找到 {len(images)} 张图片")
            return images
            
        except Exception as e:
            logger.error(f"获取图片文件失败: {e}")
            return []
    
    def read_excel_tasks(self, folder_path: str) -> pd.DataFrame:
        """读取Excel任务列表"""
        try:
            excel_path = self.find_excel_file(folder_path)
            if not excel_path:
                logger.error(f"文件夹 {folder_path} 中未找到Excel文件")
                return pd.DataFrame()
            
            df = pd.read_excel(excel_path)
            logger.info(f"读取Excel文件成功: {excel_path}")
            return df
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            return pd.DataFrame()
    
    def get_pending_tasks(self, folder_path: str) -> List[Dict]:
        """
        获取待处理的任务
        返回: [{'index': 行号, 'image_index': 图片序号, 'image_path': 图片路径, 'prompt': 提示词}, ...]
        """
        try:
            df = self.read_excel_tasks(folder_path)
            if df.empty:
                return []
            
            images = self.get_images_in_folder(folder_path)
            image_dict = {index: path for index, path in images}
            
            pending_tasks = []
            
            for idx, row in df.iterrows():
                # 检查状态列是否已完成
                status = row.iloc[self.status_column - 1] if len(row) >= self.status_column else None
                if pd.isna(status) or status != self.completed_status:
                    prompt = row.iloc[self.prompt_column - 1] if len(row) >= self.prompt_column else None
                    if pd.notna(prompt):
                        # 修改：使用 Excel 行号作为图片序号
                        image_index = idx + 1  # Excel 行号从 2 开始（第1行是标题），对应 idx + 1
                        image_path = image_dict.get(image_index)
                        if image_path:
                            pending_tasks.append({
                                'excel_row': idx,
                                'image_index': image_index,
                                'image_path': image_path,
                                'prompt': str(prompt).strip()
                            })
                        else:
                            logger.warning(f"未找到序号为 {image_index} 的图片")
            
            logger.info(f"文件夹 {folder_path} 中有 {len(pending_tasks)} 个待处理任务")
            return pending_tasks
            
        except Exception as e:
            logger.error(f"获取待处理任务失败: {e}")
            return []
    
    def update_task_status(self, folder_path: str, excel_row: int, status: str = None):
        """更新任务状态到Excel"""
        try:
            excel_path = self.find_excel_file(folder_path)
            if not excel_path:
                logger.error(f"文件夹 {folder_path} 中未找到Excel文件")
                return
            
            df = pd.read_excel(excel_path)
            
            # 确保状态列存在
            while len(df.columns) < self.status_column:
                df[f'Column_{len(df.columns) + 1}'] = None
            
            # 更新状态
            status = status or self.completed_status
            df.iloc[excel_row, self.status_column - 1] = status
            
            # 保存Excel
            df.to_excel(excel_path, index=False)
            logger.info(f"更新任务状态成功: 行 {excel_row + 1} -> {status}")
            
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")
    
    def save_video_file(self, video_url: str, folder_path: str, image_index: int, prompt: str) -> Optional[str]:
        """
        下载并保存视频文件
        返回保存的文件路径
        """
        try:
            import requests
            import re
            
            # 清理提示词，移除不适合文件名的字符
            clean_prompt = re.sub(r'[<>:"/\\|?*\[\].,!?;:，。！？；：]', '', prompt)  # 移除不支持的字符和标点符号
            clean_prompt = re.sub(r'\s+', '_', clean_prompt)  # 将空格替换为下划线
            clean_prompt = clean_prompt.strip('_')[:10]  # 移除首尾下划线，限制长度为10个字符
            
            # 生成视频文件名：序号_提示词.mp4
            video_filename = f"{image_index}_{clean_prompt}.mp4"
            video_path = os.path.join(folder_path, video_filename)
            
            # 最大重试次数
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 下载视频
                    timeout = config_manager.get_user_config('download_timeout')
                    response = requests.get(video_url, timeout=timeout, stream=True)
                    response.raise_for_status()
                    
                    # 获取文件大小
                    total_size = int(response.headers.get('content-length', 0))
                    if total_size == 0:
                        raise Exception("无法获取文件大小")
                    
                    # 下载并保存文件
                    downloaded_size = 0
                    with open(video_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                    
                    # 验证文件大小
                    if downloaded_size != total_size:
                        os.remove(video_path)  # 删除不完整的文件
                        raise Exception(f"文件下载不完整: 已下载 {downloaded_size} 字节，预期 {total_size} 字节")
                    
                    # 验证文件是否为有效的视频文件
                    if not self._is_valid_video_file(video_path):
                        os.remove(video_path)  # 删除无效的视频文件
                        raise Exception("下载的文件不是有效的视频文件")
                    
                    logger.info(f"视频保存成功: {video_path}")
                    return video_path
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"第 {retry_count} 次下载失败: {e}，正在重试...")
                        # 如果文件存在，删除它
                        if os.path.exists(video_path):
                            os.remove(video_path)
                        # 等待一段时间后重试
                        import time
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        logger.error(f"下载失败，已达到最大重试次数 ({max_retries}): {e}")
                        raise
            
            return None
            
        except Exception as e:
            logger.error(f"保存视频文件失败: {e}")
            return None
    
    def _is_valid_video_file(self, file_path: str) -> bool:
        """
        验证文件是否为有效的视频文件
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # 小于1KB的文件可能不是有效的视频
                return False
            
            # 检查文件头部标识
            with open(file_path, 'rb') as f:
                header = f.read(12)  # 读取文件头部
                # 检查是否为MP4文件（ftyp box）
                if header[4:8] == b'ftyp':
                    return True
                # 检查是否为其他常见视频格式
                if header.startswith(b'\x00\x00\x00\x18ftypmp42'):  # MP4
                    return True
                if header.startswith(b'\x00\x00\x00\x20ftypisom'):  # MP4
                    return True
                if header.startswith(b'\x00\x00\x00\x20ftypM4V'):  # M4V
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"验证视频文件失败: {e}")
            return False


# 全局文件管理器实例
file_manager = FileManager() 
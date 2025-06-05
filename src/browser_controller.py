"""
浏览器控制器
负责使用Playwright控制Chrome浏览器进行网页操作
"""

import asyncio
import time
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from loguru import logger
from src.config_manager import config_manager
from bit_api import openBrowser, closeBrowser


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_initialized = False
        self.basic_params_set = False  # 标记基础参数是否已设置
    
    async def smart_delay(self, delay_type=None):
        """智能延时"""
        delay_time = config_manager.get_smart_delay(delay_type)
        logger.debug(f"智能延时: {delay_time:.2f}秒")
        await asyncio.sleep(delay_time)
    
    async def initialize(self):
        """初始化浏览器 - 连接到指定比特浏览器窗口"""
        try:
            self.playwright = await async_playwright().start()
            # 从配置读取窗口ID
            bit_browser_id = config_manager.get_user_config('bit_browser_id')
            if not bit_browser_id or bit_browser_id == "请填写比特浏览器窗口ID":
                raise Exception("请在user_config.yaml中配置bit_browser_id为比特浏览器窗口ID")
            # 打开指定窗口，获取ws地址
            open_res = openBrowser(bit_browser_id)
            logger.info(f"open_res: {open_res}")
            # 自动适配ws_url的获取方式
            ws_data = open_res.get('data', {}).get('ws')
            if isinstance(ws_data, dict):
                ws_url = ws_data.get('selenium')
            else:
                ws_url = ws_data
            if not ws_url:
                raise Exception(f"未获取到比特浏览器ws地址，open_res: {open_res}")
            self._bit_browser_id = bit_browser_id  # 保存ID用于后续关闭
            self.browser = await self.playwright.chromium.connect_over_cdp(ws_url)
            logger.info(f"成功连接到比特浏览器: {ws_url}")
            # 获取浏览器上下文
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                logger.info("使用现有的浏览器上下文")
            else:
                self.context = await self.browser.new_context()
                logger.info("创建新的浏览器上下文")
            pages = self.context.pages
            if pages:
                self.page = pages[0]
                logger.info("使用现有的浏览器页面")
            else:
                self.page = await self.context.new_page()
                logger.info("创建新的浏览器页面")
            self.page.set_default_timeout(config_manager.get_user_config('timeout'))
            self.is_initialized = True
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            await self.cleanup()
            raise
    
    async def navigate_to_target(self):
        """导航到目标网站，并关闭其他标签页"""
        try:
            target_url = config_manager.get_target_url()
            current_url = self.page.url
            # 检查是否已经在目标网站
            if "chatglm.cn/video" in current_url:
                logger.info(f"已在目标网站: {current_url}")
            else:
                # 导航到目标网站
                await self.page.goto(target_url)
                # 等待页面加载
                await asyncio.sleep(config_manager.get_wait_time('page_load') / 1000)
                logger.info(f"成功导航到: {target_url}")
            # 关闭其他标签页
            for p in self.context.pages:
                if p != self.page:
                    await p.close()
            logger.info("已关闭其他标签页，仅保留目标页面")
        except Exception as e:
            logger.error(f"导航失败: {e}")
            raise
    
    async def setup_initial_settings(self):
        """设置初始参数（只在第一次运行时执行）"""
        if self.basic_params_set:
            logger.info("基础参数已设置，跳过")
            return
        try:
            # 1. 点击创作历史按钮
            await self.click_creation_history()
            # 不再在此处设置self.basic_params_set
            logger.info("初始设置完成")
        except Exception as e:
            logger.error(f"初始设置失败: {e}")
            raise
    
    async def click_creation_history(self):
        """点击创作历史按钮"""
        try:
            xpath = config_manager.get_web_element('elements.creation_history_btn')
            await self.page.click(xpath)
            
            # 等待页面加载
            await asyncio.sleep(config_manager.get_wait_time('page_load') / 1000)
            # 智能延时
            await self.smart_delay('click_after')
            logger.info("点击创作历史按钮成功")
            
        except Exception as e:
            logger.error(f"点击创作历史按钮失败: {e}")
            raise
    
    async def setup_basic_params(self):
        """设置基础参数，支持用户自定义选项，确保在弹窗内查找并等待元素"""
        try:
            video_options = config_manager.get_user_config('video_options') or {}
            quality = video_options.get('quality', '质量更佳')
            framerate = video_options.get('framerate', '帧率60')
            resolution = video_options.get('resolution', '4K')
            # 点击基础参数按钮
            basic_params_botton = config_manager.get_web_element('elements.basic_params_button')
            await self.page.click(basic_params_botton)
            # 等待弹窗出现
            popup_xpath = config_manager.get_web_element('elements.basic_params_popup')
            await self.page.wait_for_selector(popup_xpath, timeout=10000)
            # 在弹窗内查找参数选项
            def in_popup(xpath):
                # 保证在弹窗下任意深度查找
                return f"{popup_xpath}//{xpath.lstrip('/')}"
            # 选择质量
            if quality == "质量更佳":
                quality_xpath = config_manager.get_web_element('elements.quality_options.better')
            else:
                quality_xpath = config_manager.get_web_element('elements.quality_options.faster')
            quality_xpath = in_popup(quality_xpath)
            await self.page.wait_for_selector(quality_xpath, timeout=5000)
            await self.page.click(quality_xpath)
            # 选择帧率
            if framerate == "帧率60":
                framerate_xpath = config_manager.get_web_element('elements.fps_options.fps_60')
            else:
                framerate_xpath = config_manager.get_web_element('elements.fps_options.fps_30')
            framerate_xpath = in_popup(framerate_xpath)
            await self.page.wait_for_selector(framerate_xpath, timeout=5000)
            await self.page.click(framerate_xpath)
            # 选择分辨率
            if resolution == "4K":
                resolution_xpath = config_manager.get_web_element('elements.resolution_options.resolution_4k')
            else:
                resolution_xpath = config_manager.get_web_element('elements.resolution_options.resolution_1080p')
            resolution_xpath = in_popup(resolution_xpath)
            await self.page.wait_for_selector(resolution_xpath, timeout=5000)
            await self.page.click(resolution_xpath)
            # 再次点击基础参数按钮关闭浮窗
            await self.page.click(basic_params_botton)
            # 智能延时
            await self.smart_delay('click_after')
            logger.info(f"基础参数设置成功: 质量={quality}, 帧率={framerate}, 分辨率={resolution}")
            self.basic_params_set = True
        except Exception as e:
            logger.error(f"设置基础参数失败: {e}")
            raise
    
    async def upload_image(self, image_path: str):
        """上传图片"""
        try:
            uploader_xpath = config_manager.get_web_element('elements.image_uploader')
            file_input_selector = config_manager.get_web_element('elements.file_input')
            upload_btn_xpath = config_manager.get_web_element('elements.upload_btn')
            
            # 查找文件输入元素
            file_input = await self.page.query_selector(file_input_selector)
            if file_input:
                await file_input.set_input_files(image_path)
            else:
                # 如果没有找到文件输入，尝试点击上传区域
                await self.page.click(uploader_xpath)
                await asyncio.sleep(5)  # 增加等待时间
                file_input = await self.page.query_selector(file_input_selector)
                if file_input:
                    await file_input.set_input_files(image_path)
                else:
                    raise Exception("未找到文件上传输入元素")
            
            # 新增：点击上传按钮
            await self.page.click(upload_btn_xpath)
            
            # 增加上传后的等待时间
            await asyncio.sleep(2)  # 等待上传按钮点击响应
            await self.smart_delay('click_after')

            # 等待上传完成
            await asyncio.sleep(config_manager.get_wait_time('upload_complete') / 1000)
            # 智能延时
            await self.smart_delay('upload_after')
            
            # 验证上传是否成功
            await self.verify_upload(image_path)
            
            logger.info(f"图片上传成功: {image_path}")
            
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            raise
    
    async def verify_upload(self, image_path: str) -> bool:
        """验证图片是否上传成功，只判断preview-box出现，出现即返回"""
        try:
            preview_box_xpath = config_manager.get_web_element('elements.preview_box')
            max_wait = 10  # 最多等10秒
            interval = 0.2  # 检查间隔0.2秒
            waited = 0
            while waited < max_wait:
                preview_box = await self.page.query_selector(preview_box_xpath)
                if preview_box:
                    return True
                await asyncio.sleep(interval)
                waited += interval
            raise Exception("上传后未检测到图片预览框元素（preview-box），图片可能未上传成功")
        except Exception as e:
            logger.error(f"验证上传失败: {e}")
            raise
    
    async def input_prompt(self, prompt: str):
        """输入提示词"""
        try:
            textarea_xpath = config_manager.get_web_element('elements.prompt_textarea')
            
            # 清空并输入提示词
            await self.page.fill(textarea_xpath, prompt)
            
            # 智能延时
            await self.smart_delay('input_after')
            logger.info(f"提示词输入成功: {prompt}")
            
        except Exception as e:
            logger.error(f"提示词输入失败: {e}")
            raise
    
    async def click_generate(self):
        """点击生成按钮"""
        try:
            generate_btn_xpath = config_manager.get_web_element('elements.generate_btn')
            await self.page.click(generate_btn_xpath)
            
            # 增加点击后的初始延时
            await asyncio.sleep(5)  # 等待5秒，确保生成开始
            
            # 智能延时
            await self.smart_delay('click_after')
            logger.info("点击生成按钮成功")
            
        except Exception as e:
            logger.error(f"点击生成按钮失败: {e}")
            raise
    
    async def wait_for_generation_complete(self) -> Optional[str]:
        """
        等待视频生成完成并获取视频URL
        返回视频下载链接，如果失败返回None
        """
        try:
            generation_card_xpath = config_manager.get_web_element('elements.generation_card')
            timeout = config_manager.get_user_config('video_generation_timeout')
            check_interval = config_manager.get_wait_time('generation_check') / 1000
            
            start_time = time.time()
            last_video_url = None  # 记录上一次获取到的视频URL
            generation_started = False  # 标记是否已经开始生成
            
            while time.time() - start_time < timeout / 1000:
                try:
                    # 检查生成卡片是否存在
                    card_element = await self.page.query_selector(generation_card_xpath)
                    if not card_element:
                        if not generation_started:
                            # 如果还没开始生成，继续等待
                            await asyncio.sleep(check_interval)
                            continue
                        else:
                            # 如果已经开始生成但卡片消失了，说明生成失败
                            logger.error("生成卡片消失，可能生成失败")
                            return None
                    
                    # 获取卡片内容
                    card_html = await card_element.inner_html()
                    
                    # 检查是否还在生成中
                    if "视频生成中" in card_html or "processing" in card_html or "loadding" in card_html:
                        if not generation_started:
                            generation_started = True
                            logger.info("视频开始生成...")
                        else:
                            logger.info("视频生成中，继续等待...")
                        await asyncio.sleep(check_interval)
                        continue
                    
                    # 检查是否生成完成 - 查找video-container loaded类
                    if "video-container loaded" in card_html or "finished" in card_html:
                        # 查找视频源链接 - 优先从source标签获取
                        source_element = await card_element.query_selector('source[type="video/mp4"]')
                        if source_element:
                            video_url = await source_element.get_attribute('src')
                            if video_url and video_url != last_video_url:
                                # 验证视频元素是否是新生成的
                                video_element = await card_element.query_selector('video')
                                if video_element:
                                    # 检查视频元素是否可见
                                    is_visible = await video_element.is_visible()
                                    if is_visible:
                                        # 额外等待2秒，确保视频完全加载
                                        await asyncio.sleep(2)
                                        logger.info(f"视频生成完成，获取到新的下载链接: {video_url}")
                                        return video_url
                        
                        # 如果没有找到source，尝试从video元素的src属性获取
                        video_element = await card_element.query_selector('video.video-container')
                        if video_element:
                            video_url = await video_element.get_attribute('src')
                            if video_url and video_url != last_video_url:
                                # 验证视频元素是否是新生成的
                                is_visible = await video_element.is_visible()
                                if is_visible:
                                    # 额外等待2秒，确保视频完全加载
                                    await asyncio.sleep(2)
                                    logger.info(f"视频生成完成，获取到新的下载链接: {video_url}")
                                    return video_url
                        
                        # 最后尝试从任何video元素获取
                        video_element = await card_element.query_selector('video')
                        if video_element:
                            video_url = await video_element.get_attribute('src')
                            if video_url and video_url != last_video_url:
                                # 验证视频元素是否是新生成的
                                is_visible = await video_element.is_visible()
                                if is_visible:
                                    # 额外等待2秒，确保视频完全加载
                                    await asyncio.sleep(2)
                                    logger.info(f"视频生成完成，获取到新的下载链接: {video_url}")
                                    return video_url
                    
                    await asyncio.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"检查生成状态时出错: {e}")
                    await asyncio.sleep(check_interval)
            
            logger.error("视频生成超时")
            return None
            
        except Exception as e:
            logger.error(f"等待视频生成完成失败: {e}")
            return None
    
    async def process_single_task(self, image_path: str, prompt: str) -> Optional[str]:
        """
        处理单个任务：上传图片、输入提示词、生成视频
        返回视频下载链接
        """
        try:
            logger.info(f"开始处理任务: {image_path} -> {prompt}")
            # 1. 上传图片
            await self.upload_image(image_path)
            # 2. 设置基础参数（每次上传图片后都设置）
            await self.setup_basic_params()
            # 3. 输入提示词
            await self.input_prompt(prompt)
            # 4. 点击生成
            await self.click_generate()
            # 5. 等待生成完成
            video_url = await self.wait_for_generation_complete()
            if video_url:
                logger.info("任务处理成功")
                return video_url
            else:
                logger.error("任务处理失败：未获取到视频链接")
                return None
        except Exception as e:
            logger.error(f"处理任务失败: {e}")
            return None
    
    async def cleanup(self):
        """清理资源，只关闭Playwright资源，不关闭浏览器窗口"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            # 不再关闭self.browser和比特浏览器窗口
            if self.playwright:
                await self.playwright.stop()
            logger.info("Playwright资源清理完成（浏览器窗口未关闭）")
        except Exception as e:
            logger.error(f"清理浏览器资源失败: {e}")


# 全局浏览器控制器实例
browser_controller = BrowserController() 
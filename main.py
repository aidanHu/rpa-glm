"""
视频生成自动化主程序
使用Playwright控制Chrome浏览器自动化生成视频
"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger
from src.task_processor import task_processor


def setup_logging():
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 添加文件输出
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "video_generator_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        encoding="utf-8"
    )


async def main():
    """主函数"""
    try:
        logger.info("=" * 60)
        logger.info("视频生成自动化程序启动")
        logger.info("=" * 60)
        # 直接初始化任务处理器
        await task_processor.initialize()
        await task_processor.process_all_tasks()
        logger.info("程序执行完成")
    except KeyboardInterrupt:
        logger.warning("用户中断程序执行")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise
    finally:
        await task_processor.cleanup()
        logger.info("程序退出")


def run():
    """运行程序的入口函数"""
    # 设置日志
    setup_logging()
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        sys.exit(1)
    
    try:
        # 运行异步主函数
        asyncio.run(main())
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run() 
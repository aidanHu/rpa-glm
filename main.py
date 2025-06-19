#!/usr/bin/env python3
"""
ChatGLM视频自动生成工具 - GUI版本
使用PyQt6图形界面
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查关键依赖"""
    try:
        from PyQt6.QtWidgets import QApplication
        import yaml
        import pandas
        import requests
        import loguru
        return True
    except ImportError as e:
        print(f"错误：缺少必要依赖 - {e}")
        print("\n请运行以下命令安装依赖：")
        print("pip install -r requirements.txt")
        print("\n或者运行检测脚本：")
        print("python test_install.py")
        return False

def main():
    """主函数"""
    print("ChatGLM视频自动生成工具启动中...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        print(f"当前版本：{sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 导入并启动GUI
    try:
        from gui_main import main as gui_main
        print("正在启动图形界面...")
        gui_main()
    except Exception as e:
        print(f"启动GUI失败: {e}")
        print("\n请尝试以下解决方案：")
        print("1. 运行: python test_install.py")
        print("2. 重新安装依赖: pip install -r requirements.txt")
        print("3. 检查Python版本是否 >= 3.8")
        sys.exit(1)

if __name__ == "__main__":
    main() 
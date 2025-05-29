"""
安装脚本
用于快速设置项目环境
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def main():
    """主安装函数"""
    print("=" * 50)
    print("视频生成自动化工具 - 环境设置")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖包
    if not run_command("pip install -r requirements.txt", "安装Python依赖包"):
        print("请手动运行: pip install -r requirements.txt")
        return
    
    # 安装Playwright浏览器
    if not run_command("playwright install chromium", "安装Playwright浏览器"):
        print("请手动运行: playwright install chromium")
        return
    
    # 创建必要的目录
    directories = ["logs", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 检查配置文件
    config_file = Path("config/user_config.yaml")
    if config_file.exists():
        print("✅ 配置文件已存在")
    else:
        print("⚠️  请编辑 config/user_config.yaml 配置根目录路径")
    
    print("\n" + "=" * 50)
    print("环境设置完成！")
    print("=" * 50)
    print("\n下一步操作：")
    print("1. 编辑 config/user_config.yaml 设置任务根目录")
    print("2. 准备好图片和Excel文件")
    print("3. 运行程序: python main.py")
    print("   (程序会自动处理Chrome浏览器启动和登录提示)")
    print("\n详细说明请查看 README.md")


if __name__ == "__main__":
    main() 
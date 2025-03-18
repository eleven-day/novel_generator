# main.py - 主程序入口

import os
import sys
from dotenv import load_dotenv
from ui.cli import CLI
from utils.logger import Logger

def check_dependencies():
    """检查依赖项是否安装"""
    required_packages = ['openai', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包，请安装：")
        for package in missing_packages:
            print(f"- {package}")
        print("\n可以通过运行以下命令安装：")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """检查环境变量"""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 未设置OPENAI_API_KEY环境变量")
        print("\n请通过以下方式之一设置API密钥：")
        print("1. 创建.env文件并添加：OPENAI_API_KEY=your_api_key_here")
        print("2. 在操作系统中设置环境变量OPENAI_API_KEY")
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    dirs = ['saves', 'exports', 'logs']
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"已创建目录: {directory}")

def main():
    """主函数"""
    print("=" * 60)
    print("基于人物驱动的小说生成系统")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 检查环境变量
    if not check_environment():
        sys.exit(1)
    
    # 创建日志
    logger = Logger()
    logger.info("程序启动")
    
    try:
        # 启动CLI
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        logger.info("程序被用户中断")
    except Exception as e:
        print(f"\n程序出现错误: {e}")
        logger.error(f"程序出现错误: {e}")
    finally:
        logger.info("程序结束")
        print("\n程序已结束")

if __name__ == "__main__":
    main()
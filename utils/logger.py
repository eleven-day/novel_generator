# utils/logger.py - 日志工具

import logging
import os
from datetime import datetime

class Logger:
    """日志记录工具"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志文件
        log_file = os.path.join(log_dir, f"novel_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # 配置日志
        self.logger = logging.getLogger("novel_generator")
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """记录信息"""
        self.logger.info(message)
    
    def error(self, message):
        """记录错误"""
        self.logger.error(message)
    
    def warning(self, message):
        """记录警告"""
        self.logger.warning(message)
    
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)
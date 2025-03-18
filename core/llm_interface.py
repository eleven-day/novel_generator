# core/llm_interface.py - LLM接口

import os
import time
import openai
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMInterface:
    """LLM交互接口"""
    
    def __init__(self, model="gpt-4"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("未设置OPENAI_API_KEY环境变量")
        
        openai.api_key = self.api_key
    
    def generate_response(self, prompt: str, temperature=0.7, max_tokens=2000):
        """调用OpenAI API获取响应"""
        retries = 3
        while retries > 0:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a creative novelist AI that generates structured novel content."},
                              {"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"API调用错误: {e}")
                retries -= 1
                if retries > 0:
                    print(f"尝试重新连接，剩余尝试次数: {retries}")
                    time.sleep(2)
                else:
                    raise Exception("无法连接到LLM API")
    
    def set_model(self, model: str):
        """更改LLM模型"""
        self.model = model
        print(f"已切换到模型: {model}")
    
    def get_available_models(self):
        """获取可用的模型列表"""
        try:
            models = openai.Model.list()
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return ["gpt-4", "gpt-3.5-turbo"]
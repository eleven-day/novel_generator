import json
import time

def save_article(content: str, filename: str):
    """保存文章到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"文章已保存至 {filename}")
    except Exception as e:
        print(f"保存文章时出错: {e}")

def save_mapping(content_dict: dict, filename: str):
    """保存大纲与生成内容的映射关系到 JSON 文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content_dict, f, ensure_ascii=False, indent=2)
        print(f"内容映射已保存至 {filename}")
    except Exception as e:
        print(f"保存映射关系时出错: {e}")
# utils/file_utils.py - 文件操作工具

import os
import json
from typing import Optional, Dict, Any, List
from core.models import Novel
from utils.xml_utils import novel_to_xml, xml_to_novel

def save_novel_to_xml(novel: Novel, path: str) -> bool:
    """保存小说到XML文件"""
    try:
        xml_data = novel_to_xml(novel)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_data)
            
        return True
    except Exception as e:
        print(f"保存XML文件失败: {e}")
        return False

def load_novel_from_xml(path: str) -> Optional[Novel]:
    """从XML文件加载小说"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            xml_data = f.read()
            
        return xml_to_novel(xml_data)
    except Exception as e:
        print(f"加载XML文件失败: {e}")
        return None

def export_to_text(novel: Novel, path: str) -> bool:
    """导出小说为可阅读的文本文件"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"《{novel.title}》\n\n")
            f.write(f"类型: {novel.genre}\n")
            f.write(f"背景: {novel.setting}\n\n")
            
            f.write("主要角色:\n")
            for char_id, char in novel.characters.items():
                f.write(f"- {char.name}: {char.age}岁, {char.gender}\n")
                f.write(f"  背景: {char.background[:100]}...\n\n")
            
            f.write("\n--- 正文 ---\n\n")
            
            for chapter in novel.chapters:
                f.write(f"\n第{chapter.number}章: {chapter.title}\n\n")
                f.write(chapter.content)
                f.write("\n\n")
                
        return True
    except Exception as e:
        print(f"导出文本文件失败: {e}")
        return False

def list_saved_novels(directory: str = "saves") -> List[Dict[str, Any]]:
    """列出保存的小说文件"""
    result = []
    
    # 确保目录存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            path = os.path.join(directory, filename)
            try:
                novel = load_novel_from_xml(path)
                if novel:
                    result.append({
                        "filename": filename,
                        "title": novel.title,
                        "genre": novel.genre,
                        "chapters": len(novel.chapters),
                        "last_modified": novel.last_modified
                    })
            except Exception:
                # 读取失败的文件跳过
                pass
    
    return result
# middleware/outline_manager.py - 大纲管理中间件

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from core.models import Novel, Outline, OutlineArc
from core.llm_interface import LLMInterface
from config.prompts import OUTLINE_GENERATION_PROMPT

class OutlineManager:
    """大纲管理中间件"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
    
    def create_outline(self, novel: Novel, overview: str) -> Outline:
        """手动创建大纲"""
        outline = Outline.create(overview)
        novel.outline = outline
        novel.update_modified()
        return outline
    
    def generate_outline(self, novel: Novel) -> Outline:
        """使用LLM生成大纲"""
        # 提取角色信息
        characters_info = []
        for char_id, char in novel.characters.items():
            char_info = f"{char.name}: {char.age}岁, {char.gender}, 背景: {char.background[:100]}..."
            characters_info.append(char_info)
        
        # 获取上下文
        context = novel.context.global_context
        
        # 构建提示
        prompt = OUTLINE_GENERATION_PROMPT.format(
            title=novel.title,
            genre=novel.genre,
            setting=novel.setting,
            characters_info="\n".join(characters_info),
            context=context
        )
        
        # 调用LLM
        response = self.llm.generate_response(prompt)
        
        try:
            # 解析XML响应
            root = ET.fromstring(response)
            
            overview = root.find("overview").text
            
            # 创建大纲
            outline = Outline.create(overview)
            
            # 解析情节弧
            for arc_elem in root.findall("arc"):
                name = arc_elem.find("name").text
                description = arc_elem.find("description").text
                
                arc = OutlineArc(name=name, description=description)
                
                # 解析关键事件
                key_events_elem = arc_elem.find("key_events")
                if key_events_elem is not None:
                    for event_elem in key_events_elem.findall("event"):
                        arc.key_events.append(event_elem.text)
                
                outline.arcs.append(arc)
            
            # 更新小说
            novel.outline = outline
            novel.update_modified()
            
            return outline
            
        except Exception as e:
            print(f"解析大纲XML时出错: {e}")
            print(f"原始响应: {response}")
            # 创建一个基本大纲作为备选
            outline = Outline.create("生成失败的大纲")
            novel.outline = outline
            novel.update_modified()
            return outline
    
    def update_outline(self, novel: Novel, data: Dict[str, Any]) -> Optional[Outline]:
        """更新大纲信息"""
        if novel.outline is None:
            return None
        
        # 更新概述
        if "overview" in data:
            novel.outline.overview = data["overview"]
        
        # 更新情节弧
        if "arcs" in data:
            novel.outline.arcs = []
            for arc_data in data["arcs"]:
                arc = OutlineArc(
                    name=arc_data["name"],
                    description=arc_data["description"],
                    key_events=arc_data.get("key_events", [])
                )
                novel.outline.arcs.append(arc)
        
        novel.update_modified()
        return novel.outline
    
    def add_arc(self, novel: Novel, name: str, description: str) -> Optional[OutlineArc]:
        """添加情节弧"""
        if novel.outline is None:
            novel.outline = Outline.create("默认大纲")
        
        arc = OutlineArc(name=name, description=description)
        novel.outline.arcs.append(arc)
        
        novel.update_modified()
        return arc
    
    def delete_arc(self, novel: Novel, arc_index: int) -> bool:
        """删除情节弧"""
        if novel.outline is None or arc_index >= len(novel.outline.arcs):
            return False
        
        novel.outline.arcs.pop(arc_index)
        novel.update_modified()
        return True
    
    def get_outline(self, novel: Novel) -> Optional[Outline]:
        """获取大纲"""
        return novel.outline
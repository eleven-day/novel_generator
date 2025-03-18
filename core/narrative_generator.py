# core/narrative_generator.py - 叙事生成器

from typing import List, Dict, Any
from .llm_interface import LLMInterface
from .models import Novel, Character, Event, Chapter
from config.prompts import CHAPTER_GENERATION_PROMPT

class NarrativeGenerator:
    """叙事生成器 - 负责生成小说内容"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
    
    def generate_chapter(self, novel: Novel, events: List[Event], focus_characters: List[Character]) -> Dict[str, str]:
        """生成章节内容"""
        # 提取章节相关信息
        chapter_number = novel.current_chapter + 1
        previous_summary = ""
        if novel.chapters and novel.current_chapter > 0:
            previous_summary = novel.chapters[novel.current_chapter - 1].summary
        
        # 获取大纲信息
        outline = ""
        if novel.outline:
            # 根据章节选择合适的大纲弧段
            if novel.outline.arcs:
                arc_index = min(len(novel.outline.arcs) - 1, (chapter_number - 1) // ((len(novel.chapters) or 10) // len(novel.outline.arcs) + 1))
                outline = f"{novel.outline.arcs[arc_index].description}\n关键事件: {', '.join(novel.outline.arcs[arc_index].key_events)}"
        
        # 构建角色信息
        character_info = []
        for char in focus_characters:
            traits_info = ", ".join([t.name for t in char.traits[:3]])
            relations = []
            for rel_id, rel in char.relationships.items():
                if rel.target_id in novel.characters:
                    target_name = novel.characters[rel.target_id].name
                    relations.append(f"{target_name}({rel.relationship_type}, 强度:{rel.strength:.1f})")
            
            rel_info = "; ".join(relations[:3])
            char_info = f"{char.name}: {char.age}岁, {char.gender}, 特质: {traits_info}, 关系: {rel_info}"
            character_info.append(char_info)
        
        # 构建事件信息
        event_info = []
        for event in events:
            event_info.append(f"{event.name}: {event.description}")
        
        # 获取上下文
        context = novel.context.get_context_for_chapter(chapter_number)
        
        # 构建提示
        prompt = CHAPTER_GENERATION_PROMPT.format(
            chapter_number=chapter_number,
            title=novel.title,
            genre=novel.genre,
            setting=novel.setting,
            outline=outline,
            previous_summary=previous_summary,
            character_info="\n".join(character_info),
            event_info="\n".join(event_info),
            context=context
        )
        
        # 调用LLM生成章节
        response = self.llm.generate_response(prompt, max_tokens=4000)
        
        try:
            # 解析XML响应
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response)
            
            chapter_title = root.find("title").text
            chapter_content = root.find("content").text
            chapter_summary = root.find("summary").text
            
            return {
                "title": chapter_title,
                "content": chapter_content,
                "summary": chapter_summary
            }
            
        except Exception as e:
            print(f"解析章节XML时出错: {e}")
            print(f"原始响应: {response}")
            # 返回基本结构
            return {
                "title": f"第{chapter_number}章",
                "content": "内容生成失败，请重试。",
                "summary": "章节解析错误。"
            }
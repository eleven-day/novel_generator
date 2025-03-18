# middleware/event_manager.py - 事件管理中间件

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from core.models import Event, Novel
from core.llm_interface import LLMInterface
from config.prompts import EVENT_GENERATION_PROMPT

class EventManager:
    """事件管理中间件"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
    
    def create_event(self, novel: Novel, name: str, description: str) -> Event:
        """手动创建事件"""
        event = Event.create(name, description)
        novel.events_library[event.id] = event
        novel.update_modified()
        return event
    
    def generate_events(self, novel: Novel, num_events: int = 5) -> List[Event]:
        """使用LLM生成事件"""
        # 提取角色信息
        characters_info = []
        for char_id, char in novel.characters.items():
            char_info = f"{char.name}(ID:{char_id}): {char.age}岁, {char.gender}, 背景: {char.background[:100]}..."
            characters_info.append(char_info)
        
        # 获取上下文
        context = novel.context.global_context
        
        # 构建提示
        prompt = EVENT_GENERATION_PROMPT.format(
            title=novel.title,
            genre=novel.genre,
            setting=novel.setting,
            current_chapter=novel.current_chapter,
            characters_info="\n".join(characters_info),
            context=context,
            num_events=num_events
        )
        
        # 调用LLM
        response = self.llm.generate_response(prompt)
        
        try:
            # 解析XML响应
            root = ET.fromstring(response)
            events = []
            
            for event_elem in root.findall("event"):
                event_id = event_elem.find("id").text
                name = event_elem.find("name").text
                description = event_elem.find("description").text
                
                # 创建事件
                event = Event.create(name, description)
                
                # 解析触发条件
                triggers = {}
                triggers_elem = event_elem.find("triggers")
                if triggers_elem is not None:
                    for trigger in triggers_elem.findall("trigger"):
                        trigger_type = trigger.get("type")
                        trigger_value = trigger.get("value")
                        triggers[trigger_type] = trigger_value
                
                event.triggers = triggers
                
                # 解析效果
                effects = []
                effects_elem = event_elem.find("effects")
                if effects_elem is not None:
                    for effect in effects_elem.findall("effect"):
                        effect_target = effect.get("target")
                        effect_value = float(effect.get("value"))
                        effects.append({
                            "target": effect_target,
                            "value": effect_value
                        })
                
                event.effects = effects
                
                # 解析叙事模板
                narrative_templates = []
                for template in event_elem.findall("narrative_template"):
                    narrative_templates.append(template.text)
                
                event.narrative_templates = narrative_templates
                
                # 添加到小说
                novel.events_library[event.id] = event
                events.append(event)
            
            novel.update_modified()
            return events
            
        except Exception as e:
            print(f"解析事件XML时出错: {e}")
            print(f"原始响应: {response}")
            # 创建一个基本事件作为备选
            event = Event.create("默认事件", "因解析错误生成的事件")
            novel.events_library[event.id] = event
            novel.update_modified()
            return [event]
    
    def update_event(self, novel: Novel, event_id: str, 
                    data: Dict[str, Any]) -> Optional[Event]:
        """更新事件信息"""
        if event_id not in novel.events_library:
            return None
        
        event = novel.events_library[event_id]
        
        # 更新基本信息
        for field in ["name", "description", "notes"]:
            if field in data:
                setattr(event, field, data[field])
        
        # 更新触发条件
        if "triggers" in data:
            event.triggers = data["triggers"]
        
        # 更新效果
        if "effects" in data:
            event.effects = data["effects"]
        
        # 更新叙事模板
        if "narrative_templates" in data:
            event.narrative_templates = data["narrative_templates"]
        
        novel.update_modified()
        return event
    
    def delete_event(self, novel: Novel, event_id: str) -> bool:
        """删除事件"""
        if event_id not in novel.events_library:
            return False
        
        # 删除事件
        del novel.events_library[event_id]
        
        # 从章节中移除该事件
        for chapter in novel.chapters:
            if event_id in chapter.events:
                chapter.events.remove(event_id)
        
        novel.update_modified()
        return True
    
    def get_all_events(self, novel: Novel) -> List[Event]:
        """获取所有事件"""
        return list(novel.events_library.values())
    
    def get_event(self, novel: Novel, event_id: str) -> Optional[Event]:
        """获取特定事件"""
        return novel.events_library.get(event_id)
    
    def search_events(self, novel: Novel, query: str) -> List[Event]:
        """搜索事件"""
        query = query.lower()
        results = []
        
        for event in novel.events_library.values():
            if (query in event.name.lower() or 
                query in event.description.lower()):
                results.append(event)
        
        return results
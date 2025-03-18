# core/event_engine.py - 事件引擎

import random
from typing import List, Dict, Any
from .models import Novel, Character, Event

class EventEngine:
    """事件引擎 - 负责选择和触发事件"""
    
    def select_events_for_chapter(self, novel: Novel, max_events: int = 3) -> List[Event]:
        """为当前章节选择合适的事件"""
        # 选择潜在事件
        potential_events = list(novel.events_library.values())
        
        if not potential_events:
            return []
        
        # 过滤和评分事件
        scored_events = []
        for event in potential_events:
            score = self._calculate_event_score(event, novel)
            if score > 0:
                scored_events.append((event, score))
        
        # 按分数排序并选择前几个
        scored_events.sort(key=lambda x: x[1], reverse=True)
        num_events = min(len(scored_events), max_events)
        
        return [event for event, _ in scored_events[:num_events]]
    
    def _calculate_event_score(self, event: Event, novel: Novel) -> float:
        """计算事件的适合度分数"""
        # 示例评分逻辑，可以根据需要扩展
        score = 1.0  # 基础分
        
        # 添加一些随机性
        score += random.uniform(0, 0.5)
        
        return score
    
    def apply_event_effects(self, event: Event, novel: Novel, affected_characters: List[Character]):
        """应用事件的效果"""
        for effect in event.effects:
            # 解析效果类型和值
            effect_type = effect.get("target")
            effect_value = effect.get("value", 0.0)
            
            if effect_type == "character_relation":
                # 更新角色关系
                for i, char1 in enumerate(affected_characters):
                    for char2 in affected_characters[i+1:]:
                        char1.update_relationship(
                            char2.id, "受事件影响", float(effect_value),
                            f"事件'{event.name}'影响了关系"
                        )
                        char2.update_relationship(
                            char1.id, "受事件影响", float(effect_value),
                            f"事件'{event.name}'影响了关系"
                        )
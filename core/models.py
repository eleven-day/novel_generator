# core/models.py - 数据模型

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Union, Tuple
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid

@dataclass
class Trait:
    """角色特质"""
    id: str
    name: str
    description: str
    impact: Dict[str, float] = field(default_factory=dict)  # 对其他属性的影响
    
    @classmethod
    def create(cls, name: str, description: str, impact: Dict[str, float] = None):
        """创建新特质"""
        return cls(
            id=f"trait_{str(uuid.uuid4())[:8]}",
            name=name,
            description=description,
            impact=impact or {}
        )

@dataclass
class Relationship:
    """角色间关系"""
    target_id: str
    relationship_type: str  # 如：朋友、敌人、爱人等
    strength: float  # -1.0 到 1.0
    history: List[Dict[str, str]] = field(default_factory=list)  # 关系历史，包含时间和事件描述
    
    def add_history_entry(self, event_description: str):
        """添加关系历史记录"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "description": event_description
        })

@dataclass
class Character:
    """角色模型"""
    id: str
    name: str
    age: int
    gender: str
    background: str
    appearance: str = ""
    personality: Dict[str, float] = field(default_factory=dict)  # 性格属性
    traits: List[Trait] = field(default_factory=list)  # 特质列表
    relationships: Dict[str, Relationship] = field(default_factory=dict)  # 与其他角色的关系
    status: Dict[str, Union[str, float]] = field(default_factory=dict)  # 当前状态
    story_arcs: List[str] = field(default_factory=list)  # 角色经历的故事情节
    goals: List[str] = field(default_factory=list)  # 角色目标
    notes: str = ""  # 用户备注
    
    @classmethod
    def create(cls, name: str, age: int, gender: str, background: str):
        """创建新角色"""
        return cls(
            id=f"char_{str(uuid.uuid4())[:8]}",
            name=name,
            age=age,
            gender=gender,
            background=background
        )
    
    def add_trait(self, trait: Trait):
        """添加特质并更新影响"""
        self.traits.append(trait)
        for attr, value in trait.impact.items():
            if attr in self.personality:
                self.personality[attr] += value
            else:
                self.personality[attr] = value
    
    def update_relationship(self, target_id: str, rel_type: str, 
                           strength_change: float, event: str):
        """更新与另一角色的关系"""
        if target_id not in self.relationships:
            self.relationships[target_id] = Relationship(
                target_id=target_id,
                relationship_type=rel_type,
                strength=0.0
            )
        
        rel = self.relationships[target_id]
        rel.strength = max(-1.0, min(1.0, rel.strength + strength_change))
        if rel.relationship_type != rel_type:
            rel.relationship_type = rel_type
        rel.add_history_entry(event)
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)
    
    def to_brief_info(self):
        """简要信息"""
        return f"{self.name}(ID:{self.id}): {self.age}岁, {self.gender}, 背景: {self.background[:100]}..."

@dataclass
class Event:
    """事件模型"""
    id: str
    name: str
    description: str
    triggers: Dict[str, Union[str, List[str]]]  # 触发条件
    effects: List[Dict[str, Union[str, float]]]  # 效果
    narrative_templates: List[str]  # 叙事模板
    user_editable: bool = True  # 是否由用户编辑
    notes: str = ""  # 用户备注
    
    @classmethod
    def create(cls, name: str, description: str):
        """创建新事件"""
        return cls(
            id=f"event_{str(uuid.uuid4())[:8]}",
            name=name,
            description=description,
            triggers={},
            effects=[],
            narrative_templates=[]
        )
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)

@dataclass
class OutlineArc:
    """故事大纲中的情节弧"""
    name: str
    description: str
    key_events: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)

@dataclass
class Outline:
    """小说大纲"""
    id: str
    overview: str
    arcs: List[OutlineArc] = field(default_factory=list)
    
    @classmethod
    def create(cls, overview: str):
        """创建新大纲"""
        return cls(
            id=f"outline_{str(uuid.uuid4())[:8]}",
            overview=overview
        )
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)

@dataclass
class Chapter:
    """章节模型"""
    id: str
    number: int
    title: str
    events: List[str] = field(default_factory=list)  # 事件ID列表
    character_focus: List[str] = field(default_factory=list)  # 本章重点角色ID列表
    content: str = ""  # 章节内容
    summary: str = ""  # 章节摘要
    user_edited: bool = False  # 是否由用户编辑
    notes: str = ""  # 用户备注
    
    @classmethod
    def create(cls, number: int, title: str):
        """创建新章节"""
        return cls(
            id=f"chapter_{str(uuid.uuid4())[:8]}",
            number=number,
            title=title
        )
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)

@dataclass
class Context:
    """上下文管理"""
    global_context: str = ""  # 全局上下文
    chapter_context: Dict[int, str] = field(default_factory=dict)  # 章节特定上下文
    
    def get_context_for_chapter(self, chapter_number: int) -> str:
        """获取特定章节的上下文"""
        context = self.global_context
        if chapter_number in self.chapter_context:
            context += "\n" + self.chapter_context[chapter_number]
        return context
    
    def set_chapter_context(self, chapter_number: int, context: str):
        """设置特定章节的上下文"""
        self.chapter_context[chapter_number] = context

@dataclass
class Novel:
    """小说模型"""
    id: str
    title: str
    genre: str
    setting: str
    characters: Dict[str, Character] = field(default_factory=dict)
    chapters: List[Chapter] = field(default_factory=list)
    events_library: Dict[str, Event] = field(default_factory=dict)
    timeline: List[Dict[str, Union[str, int]]] = field(default_factory=list)  # 时间线
    current_chapter: int = 0
    outline: Optional[Outline] = None
    context: Context = field(default_factory=Context)
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def create(cls, title: str, genre: str, setting: str):
        """创建新小说"""
        return cls(
            id=f"novel_{str(uuid.uuid4())[:8]}",
            title=title,
            genre=genre,
            setting=setting
        )
    
    def update_modified(self):
        """更新最后修改时间"""
        self.last_modified = datetime.now().isoformat()
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "setting": self.setting,
            "current_chapter": self.current_chapter,
            "creation_date": self.creation_date,
            "last_modified": self.last_modified,
            "character_count": len(self.characters),
            "chapter_count": len(self.chapters),
            "event_count": len(self.events_library),
            "has_outline": self.outline is not None
        }
# middleware/character_manager.py - 角色管理中间件

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any
from core.models import Character, Trait, Novel
from core.llm_interface import LLMInterface
from config.prompts import CHARACTER_CREATION_PROMPT

class CharacterManager:
    """角色管理中间件"""
    
    def __init__(self, llm_interface: LLMInterface):
        self.llm = llm_interface
    
    def create_character(self, novel: Novel, name: str, age: int, gender: str, background: str) -> Character:
        """手动创建角色"""
        character = Character.create(name, age, gender, background)
        novel.characters[character.id] = character
        novel.update_modified()
        return character
    
    def generate_character(self, novel: Novel) -> Character:
        """使用LLM生成角色"""
        # 获取上下文
        context = novel.context.global_context
        
        # 构建提示
        background_info = f"这个角色生活在{novel.setting}世界中，这是一部{novel.genre}类型的小说。"
        prompt = CHARACTER_CREATION_PROMPT.format(
            genre=novel.genre,
            background_info=background_info,
            context=context
        )
        
        # 调用LLM
        response = self.llm.generate_response(prompt)
        
        try:
            # 解析XML响应
            root = ET.fromstring(response)
            
            name = root.find("name").text
            age = int(root.find("age").text)
            gender = root.find("gender").text
            background = root.find("background").text
            appearance = root.find("appearance").text if root.find("appearance") is not None else ""
            
            # 创建角色
            character = Character.create(name, age, gender, background)
            character.appearance = appearance
            
            # 解析性格特征
            for trait_elem in root.find("personality").findall("trait"):
                trait_name = trait_elem.get("name")
                trait_value = float(trait_elem.text)
                character.personality[trait_name] = trait_value
            
            # 解析目标
            goals_elem = root.find("goals")
            if goals_elem is not None:
                for goal_elem in goals_elem.findall("goal"):
                    character.goals.append(goal_elem.text)
            
            # 添加到小说
            novel.characters[character.id] = character
            novel.update_modified()
            
            return character
            
        except Exception as e:
            print(f"解析角色XML时出错: {e}")
            print(f"原始响应: {response}")
            # 创建一个基本角色作为备选
            character = Character.create("未知角色", 30, "未指定", "因解析错误生成的角色")
            novel.characters[character.id] = character
            novel.update_modified()
            return character
    
    def update_character(self, novel: Novel, character_id: str, 
                        data: Dict[str, Any]) -> Optional[Character]:
        """更新角色信息"""
        if character_id not in novel.characters:
            return None
        
        character = novel.characters[character_id]
        
        # 更新基本信息
        for field in ["name", "age", "gender", "background", "appearance", "notes"]:
            if field in data:
                setattr(character, field, data[field])
        
        # 更新性格属性
        if "personality" in data:
            character.personality.update(data["personality"])
        
        # 更新目标
        if "goals" in data:
            character.goals = data["goals"]
        
        novel.update_modified()
        return character
    
    def delete_character(self, novel: Novel, character_id: str) -> bool:
        """删除角色"""
        if character_id not in novel.characters:
            return False
        
        # 删除角色
        del novel.characters[character_id]
        
        # 删除其他角色与该角色的关系
        for char in novel.characters.values():
            if character_id in char.relationships:
                del char.relationships[character_id]
        
        novel.update_modified()
        return True
    
    def add_trait(self, novel: Novel, character_id: str, 
                 name: str, description: str, impact: Dict[str, float] = None) -> Optional[Trait]:
        """为角色添加特质"""
        if character_id not in novel.characters:
            return None
        
        character = novel.characters[character_id]
        trait = Trait.create(name, description, impact)
        character.add_trait(trait)
        
        novel.update_modified()
        return trait
    
    def update_relationship(self, novel: Novel, character_id: str, target_id: str,
                           rel_type: str, strength_change: float, event: str) -> bool:
        """更新角色关系"""
        if character_id not in novel.characters or target_id not in novel.characters:
            return False
        
        character = novel.characters[character_id]
        character.update_relationship(target_id, rel_type, strength_change, event)
        
        novel.update_modified()
        return True
    
    def get_all_characters(self, novel: Novel) -> List[Character]:
        """获取所有角色"""
        return list(novel.characters.values())
    
    def get_character(self, novel: Novel, character_id: str) -> Optional[Character]:
        """获取特定角色"""
        return novel.characters.get(character_id)
    
    def search_characters(self, novel: Novel, query: str) -> List[Character]:
        """搜索角色"""
        query = query.lower()
        results = []
        
        for character in novel.characters.values():
            if (query in character.name.lower() or 
                query in character.background.lower()):
                results.append(character)
        
        return results
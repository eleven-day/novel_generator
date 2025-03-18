# utils/xml_utils.py - XML处理工具

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Any, Optional
from core.models import Novel

def novel_to_xml(novel: Novel) -> str:
    """将小说数据转换为XML格式"""
    root = ET.Element("novel")
    
    # 基本信息
    ET.SubElement(root, "id").text = novel.id
    ET.SubElement(root, "title").text = novel.title
    ET.SubElement(root, "genre").text = novel.genre
    ET.SubElement(root, "setting").text = novel.setting
    ET.SubElement(root, "current_chapter").text = str(novel.current_chapter)
    ET.SubElement(root, "creation_date").text = novel.creation_date
    ET.SubElement(root, "last_modified").text = novel.last_modified
    
    # 上下文
    context_elem = ET.SubElement(root, "context")
    ET.SubElement(context_elem, "global_context").text = novel.context.global_context
    chapter_context_elem = ET.SubElement(context_elem, "chapter_contexts")
    for chapter_num, context_text in novel.context.chapter_context.items():
        chapter_elem = ET.SubElement(chapter_context_elem, "chapter_context")
        chapter_elem.set("number", str(chapter_num))
        chapter_elem.text = context_text
    
    # 大纲
    if novel.outline:
        outline_elem = ET.SubElement(root, "outline")
        ET.SubElement(outline_elem, "id").text = novel.outline.id
        ET.SubElement(outline_elem, "overview").text = novel.outline.overview
        
        arcs_elem = ET.SubElement(outline_elem, "arcs")
        for arc in novel.outline.arcs:
            arc_elem = ET.SubElement(arcs_elem, "arc")
            ET.SubElement(arc_elem, "name").text = arc.name
            ET.SubElement(arc_elem, "description").text = arc.description
            
            key_events_elem = ET.SubElement(arc_elem, "key_events")
            for event in arc.key_events:
                ET.SubElement(key_events_elem, "event").text = event
    
    # 角色
    characters_elem = ET.SubElement(root, "characters")
    for char_id, char in novel.characters.items():
        char_elem = ET.SubElement(characters_elem, "character")
        char_elem.set("id", char.id)
        ET.SubElement(char_elem, "name").text = char.name
        ET.SubElement(char_elem, "age").text = str(char.age)
        ET.SubElement(char_elem, "gender").text = char.gender
        ET.SubElement(char_elem, "background").text = char.background
        ET.SubElement(char_elem, "appearance").text = char.appearance
        ET.SubElement(char_elem, "notes").text = char.notes
        
        # 性格
        personality_elem = ET.SubElement(char_elem, "personality")
        for trait, value in char.personality.items():
            trait_elem = ET.SubElement(personality_elem, "trait")
            trait_elem.set("name", trait)
            trait_elem.text = str(value)
        
        # 特质
        traits_elem = ET.SubElement(char_elem, "traits")
        for trait in char.traits:
            trait_elem = ET.SubElement(traits_elem, "trait")
            trait_elem.set("id", trait.id)
            ET.SubElement(trait_elem, "name").text = trait.name
            ET.SubElement(trait_elem, "description").text = trait.description
            
            impact_elem = ET.SubElement(trait_elem, "impact")
            for attr, value in trait.impact.items():
                impact_attr = ET.SubElement(impact_elem, "attribute")
                impact_attr.set("name", attr)
                impact_attr.text = str(value)
        
        # 关系
        relationships_elem = ET.SubElement(char_elem, "relationships")
        for rel_id, rel in char.relationships.items():
            rel_elem = ET.SubElement(relationships_elem, "relationship")
            rel_elem.set("target_id", rel.target_id)
            ET.SubElement(rel_elem, "type").text = rel.relationship_type
            ET.SubElement(rel_elem, "strength").text = str(rel.strength)
            
            history_elem = ET.SubElement(rel_elem, "history")
            for entry in rel.history:
                entry_elem = ET.SubElement(history_elem, "entry")
                entry_elem.set("timestamp", entry["timestamp"])
                entry_elem.text = entry["description"]
        
        # 目标
        goals_elem = ET.SubElement(char_elem, "goals")
        for goal in char.goals:
            ET.SubElement(goals_elem, "goal").text = goal
    
    # 事件库
    events_elem = ET.SubElement(root, "events_library")
    for event_id, event in novel.events_library.items():
        event_elem = ET.SubElement(events_elem, "event")
        event_elem.set("id", event.id)
        ET.SubElement(event_elem, "name").text = event.name
        ET.SubElement(event_elem, "description").text = event.description
        ET.SubElement(event_elem, "user_editable").text = str(event.user_editable)
        ET.SubElement(event_elem, "notes").text = event.notes
        
        # 触发条件
        triggers_elem = ET.SubElement(event_elem, "triggers")
        for trigger_type, trigger_value in event.triggers.items():
            trigger_elem = ET.SubElement(triggers_elem, "trigger")
            trigger_elem.set("type", trigger_type)
            trigger_elem.set("value", str(trigger_value))
        
        # 效果
        effects_elem = ET.SubElement(event_elem, "effects")
        for effect in event.effects:
            effect_elem = ET.SubElement(effects_elem, "effect")
            effect_elem.set("target", effect["target"])
            effect_elem.set("value", str(effect["value"]))
        
        # 叙事模板
        templates_elem = ET.SubElement(event_elem, "narrative_templates")
        for template in event.narrative_templates:
            ET.SubElement(templates_elem, "template").text = template
    
    # 章节
    chapters_elem = ET.SubElement(root, "chapters")
    for chapter in novel.chapters:
        chapter_elem = ET.SubElement(chapters_elem, "chapter")
        chapter_elem.set("id", chapter.id)
        chapter_elem.set("number", str(chapter.number))
        ET.SubElement(chapter_elem, "title").text = chapter.title
        ET.SubElement(chapter_elem, "user_edited").text = str(chapter.user_edited)
        ET.SubElement(chapter_elem, "notes").text = chapter.notes
        
        events_elem = ET.SubElement(chapter_elem, "events")
        for event_id in chapter.events:
            event_elem = ET.SubElement(events_elem, "event")
            event_elem.text = event_id
        
        focus_elem = ET.SubElement(chapter_elem, "character_focus")
        for char_id in chapter.character_focus:
            char_elem = ET.SubElement(focus_elem, "character")
            char_elem.text = char_id
        
        if chapter.content:
            ET.SubElement(chapter_elem, "content").text = chapter.content
        
        if chapter.summary:
            ET.SubElement(chapter_elem, "summary").text = chapter.summary
    
    # 时间线
    timeline_elem = ET.SubElement(root, "timeline")
    for event in novel.timeline:
        event_elem = ET.SubElement(timeline_elem, "event")
        for key, value in event.items():
            ET.SubElement(event_elem, key).text = str(value)
    
    # 转为字符串
    xml_string = ET.tostring(root, encoding='utf-8')
    return minidom.parseString(xml_string).toprettyxml(indent="  ")

def xml_to_novel(xml_string: str) -> Optional[Novel]:
    """从XML字符串构建小说对象"""
    from core.models import Novel, Character, Trait, Relationship
    from core.models import Event, Chapter, Outline, OutlineArc, Context
    
    try:
        root = ET.fromstring(xml_string)
        
        # 基本信息
        novel_id = root.find("id").text
        title = root.find("title").text
        genre = root.find("genre").text
        setting = root.find("setting").text
        current_chapter = int(root.find("current_chapter").text)
        creation_date = root.find("creation_date").text
        last_modified = root.find("last_modified").text
        
        # 创建小说对象
        novel = Novel(
            id=novel_id,
            title=title,
            genre=genre,
            setting=setting,
            current_chapter=current_chapter,
            creation_date=creation_date,
            last_modified=last_modified
        )
        
        # 解析上下文
        context_elem = root.find("context")
        if context_elem is not None:
            global_context = context_elem.find("global_context").text or ""
            novel.context.global_context = global_context
            
            chapter_contexts_elem = context_elem.find("chapter_contexts")
            if chapter_contexts_elem is not None:
                for chapter_context in chapter_contexts_elem.findall("chapter_context"):
                    chapter_num = int(chapter_context.get("number"))
                    novel.context.chapter_context[chapter_num] = chapter_context.text or ""
        
        # 解析大纲
        outline_elem = root.find("outline")
        if outline_elem is not None:
            outline_id = outline_elem.find("id").text
            overview = outline_elem.find("overview").text
            
            outline = Outline(
                id=outline_id,
                overview=overview
            )
            
            arcs_elem = outline_elem.find("arcs")
            if arcs_elem is not None:
                for arc_elem in arcs_elem.findall("arc"):
                    name = arc_elem.find("name").text
                    description = arc_elem.find("description").text
                    
                    arc = OutlineArc(name=name, description=description)
                    
                    key_events_elem = arc_elem.find("key_events")
                    if key_events_elem is not None:
                        for event_elem in key_events_elem.findall("event"):
                            arc.key_events.append(event_elem.text)
                    
                    outline.arcs.append(arc)
            
            novel.outline = outline
        
        # 解析角色
        for char_elem in root.find("characters").findall("character"):
            char_id = char_elem.get("id")
            name = char_elem.find("name").text
            age = int(char_elem.find("age").text)
            gender = char_elem.find("gender").text
            background = char_elem.find("background").text
            
            character = Character(
                id=char_id,
                name=name,
                age=age,
                gender=gender,
                background=background
            )
            
            # 外貌
            appearance_elem = char_elem.find("appearance")
            if appearance_elem is not None and appearance_elem.text:
                character.appearance = appearance_elem.text
            
            # 备注
            notes_elem = char_elem.find("notes")
            if notes_elem is not None and notes_elem.text:
                character.notes = notes_elem.text
            
            # 解析性格
            personality_elem = char_elem.find("personality")
            if personality_elem is not None:
                for trait_elem in personality_elem.findall("trait"):
                    trait_name = trait_elem.get("name")
                    character.personality[trait_name] = float(trait_elem.text)
            
            # 解析特质
            traits_elem = char_elem.find("traits")
            if traits_elem is not None:
                for trait_elem in traits_elem.findall("trait"):
                    trait_id = trait_elem.get("id")
                    trait_name = trait_elem.find("name").text
                    trait_desc = trait_elem.find("description").text
                    
                    trait = Trait(
                        id=trait_id,
                        name=trait_name,
                        description=trait_desc
                    )
                    
                    # 解析影响
                    impact_elem = trait_elem.find("impact")
                    if impact_elem is not None:
                        for attr_elem in impact_elem.findall("attribute"):
                            attr_name = attr_elem.get("name")
                            attr_value = float(attr_elem.text)
                            trait.impact[attr_name] = attr_value
                    
                    character.traits.append(trait)
            
            # 解析关系
            rel_elem = char_elem.find("relationships")
            if rel_elem is not None:
                for rel in rel_elem.findall("relationship"):
                    target_id = rel.get("target_id")
                    rel_type = rel.find("type").text
                    strength = float(rel.find("strength").text)
                    
                    relationship = Relationship(
                        target_id=target_id,
                        relationship_type=rel_type,
                        strength=strength
                    )
                    
                    # 解析历史
                    history_elem = rel.find("history")
                    if history_elem is not None:
                        for entry_elem in history_elem.findall("entry"):
                            timestamp = entry_elem.get("timestamp")
                            description = entry_elem.text
                            relationship.history.append({
                                "timestamp": timestamp,
                                "description": description
                            })
                    
                    character.relationships[target_id] = relationship
            
            # 解析目标
            goals_elem = char_elem.find("goals")
            if goals_elem is not None:
                for goal_elem in goals_elem.findall("goal"):
                    character.goals.append(goal_elem.text)
            
            novel.characters[char_id] = character
        
        # 解析事件库
        events_elem = root.find("events_library")
        if events_elem is not None:
            for event_elem in events_elem.findall("event"):
                event_id = event_elem.get("id")
                name = event_elem.find("name").text
                description = event_elem.find("description").text
                
                event = Event(
                    id=event_id,
                    name=name,
                    description=description,
                    triggers={},
                    effects=[],
                    narrative_templates=[]
                )
                
                # 可编辑性
                user_editable_elem = event_elem.find("user_editable")
                if user_editable_elem is not None:
                    event.user_editable = user_editable_elem.text.lower() == "true"
                
                # 备注
                notes_elem = event_elem.find("notes")
                if notes_elem is not None and notes_elem.text:
                    event.notes = notes_elem.text
                
                # 解析触发条件
                triggers_elem = event_elem.find("triggers")
                if triggers_elem is not None:
                    for trigger in triggers_elem.findall("trigger"):
                        trigger_type = trigger.get("type")
                        trigger_value = trigger.get("value")
                        event.triggers[trigger_type] = trigger_value
                
                # 解析效果
                effects_elem = event_elem.find("effects")
                if effects_elem is not None:
                    for effect in effects_elem.findall("effect"):
                        target = effect.get("target")
                        value = float(effect.get("value"))
                        event.effects.append({
                            "target": target,
                            "value": value
                        })
                
                # 解析叙事模板
                templates_elem = event_elem.find("narrative_templates")
                if templates_elem is not None:
                    for template in templates_elem.findall("template"):
                        event.narrative_templates.append(template.text)
                
                novel.events_library[event_id] = event
        
        # 解析章节
        for chapter_elem in root.find("chapters").findall("chapter"):
            chapter_id = chapter_elem.get("id")
            number = int(chapter_elem.get("number"))
            title = chapter_elem.find("title").text
            
            chapter = Chapter(
                id=chapter_id,
                number=number,
                title=title,
                events=[],
                character_focus=[]
            )
            
            # 用户编辑标记
            user_edited_elem = chapter_elem.find("user_edited")
            if user_edited_elem is not None:
                chapter.user_edited = user_edited_elem.text.lower() == "true"
            
            # 备注
            notes_elem = chapter_elem.find("notes")
            if notes_elem is not None and notes_elem.text:
                chapter.notes = notes_elem.text
            
            # 解析事件
            events_elem = chapter_elem.find("events")
            if events_elem is not None:
                for event_elem in events_elem.findall("event"):
                    chapter.events.append(event_elem.text)
            
            # 解析焦点角色
            focus_elem = chapter_elem.find("character_focus")
            if focus_elem is not None:
                for char_elem in focus_elem.findall("character"):
                    chapter.character_focus.append(char_elem.text)
            
            # 内容
            content_elem = chapter_elem.find("content")
            if content_elem is not None and content_elem.text:
                chapter.content = content_elem.text
            
            # 摘要
            summary_elem = chapter_elem.find("summary")
            if summary_elem is not None and summary_elem.text:
                chapter.summary = summary_elem.text
            
            novel.chapters.append(chapter)
        
        # 解析时间线
        timeline_elem = root.find("timeline")
        if timeline_elem is not None:
            for event_elem in timeline_elem.findall("event"):
                event = {}
                for elem in event_elem:
                    tag = elem.tag
                    if tag == "chapter":
                        event[tag] = int(elem.text)
                    else:
                        event[tag] = elem.text
                novel.timeline.append(event)
        
        return novel
        
    except Exception as e:
        print(f"解析XML时出错: {e}")
        return None
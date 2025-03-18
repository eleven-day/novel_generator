# middleware/chapter_manager.py - 章节管理中间件

from typing import List, Dict, Optional, Any, Tuple
from core.models import Novel, Chapter, Character, Event
from core.event_engine import EventEngine
from core.narrative_generator import NarrativeGenerator

class ChapterManager:
    """章节管理中间件"""
    
    def __init__(self, narrative_generator: NarrativeGenerator, event_engine: EventEngine):
        self.narrative_generator = narrative_generator
        self.event_engine = event_engine
    
    def create_chapter(self, novel: Novel, title: str) -> Chapter:
        """手动创建章节"""
        chapter_number = novel.current_chapter + 1
        chapter = Chapter.create(chapter_number, title)
        chapter.user_edited = True
        
        novel.chapters.append(chapter)
        novel.current_chapter = chapter_number
        novel.update_modified()
        
        # 更新时间线
        novel.timeline.append({
            "chapter": chapter_number,
            "title": chapter.title
        })
        
        return chapter
    
    def generate_chapter(self, novel: Novel) -> Chapter:
        """生成新章节"""
        # 选择焦点角色
        focus_characters = self._select_focus_characters(novel)
        focus_character_ids = [char.id for char in focus_characters]
        
        # 选择章节事件
        events = self.event_engine.select_events_for_chapter(novel)
        if not events and novel.events_library:
            # 随机选择事件
            import random
            events = random.sample(list(novel.events_library.values()), 
                                  min(3, len(novel.events_library)))
        
        event_ids = [event.id for event in events]
        
        # 生成章节内容
        chapter_data = self.narrative_generator.generate_chapter(novel, events, focus_characters)
        
        # 创建章节对象
        chapter_number = novel.current_chapter + 1
        chapter = Chapter.create(chapter_number, chapter_data["title"])
        chapter.events = event_ids
        chapter.character_focus = focus_character_ids
        chapter.content = chapter_data["content"]
        chapter.summary = chapter_data["summary"]
        
        # 更新小说状态
        novel.chapters.append(chapter)
        novel.current_chapter = chapter_number
        
        # 更新时间线
        novel.timeline.append({
            "chapter": chapter_number,
            "title": chapter.title,
            "summary": chapter.summary
        })
        
        novel.update_modified()
        return chapter
    
    def update_chapter(self, novel: Novel, chapter_number: int,
                      data: Dict[str, Any]) -> Optional[Chapter]:
        """更新章节信息"""
        if chapter_number <= 0 or chapter_number > len(novel.chapters):
            return None
        
        chapter = novel.chapters[chapter_number - 1]
        
        # 更新基本信息
        for field in ["title", "content", "summary", "notes"]:
            if field in data:
                setattr(chapter, field, data[field])
        
        # 更新焦点角色
        if "character_focus" in data:
            chapter.character_focus = data["character_focus"]
        
        # 更新事件
        if "events" in data:
            chapter.events = data["events"]
        
        # 标记为用户编辑
        chapter.user_edited = True
        
        # 更新时间线
        for item in novel.timeline:
            if item.get("chapter") == chapter_number:
                item["title"] = chapter.title
                item["summary"] = chapter.summary
                break
        
        novel.update_modified()
        return chapter
    
    def delete_chapter(self, novel: Novel, chapter_number: int) -> bool:
        """删除章节"""
        if chapter_number <= 0 or chapter_number > len(novel.chapters):
            return False
        
        # 删除章节
        novel.chapters.pop(chapter_number - 1)
        
        # 重新编号后续章节
        for i, chapter in enumerate(novel.chapters[chapter_number - 1:], chapter_number):
            chapter.number = i
        
        # 更新当前章节
        novel.current_chapter = max(0, len(novel.chapters))
        
        # 更新时间线
        novel.timeline = [item for item in novel.timeline if item.get("chapter") != chapter_number]
        for item in novel.timeline:
            if item.get("chapter") > chapter_number:
                item["chapter"] -= 1
        
        novel.update_modified()
        return True
    
    def get_all_chapters(self, novel: Novel) -> List[Chapter]:
        """获取所有章节"""
        return novel.chapters
    
    def get_chapter(self, novel: Novel, chapter_number: int) -> Optional[Chapter]:
        """获取特定章节"""
        if chapter_number <= 0 or chapter_number > len(novel.chapters):
            return None
        return novel.chapters[chapter_number - 1]
    
    def search_chapters(self, novel: Novel, query: str) -> List[Tuple[int, Chapter]]:
        """搜索章节"""
        query = query.lower()
        results = []
        
        for i, chapter in enumerate(novel.chapters, 1):
            if (query in chapter.title.lower() or 
                query in chapter.content.lower() or
                query in chapter.summary.lower()):
                results.append((i, chapter))
        
        return results
    
    def _select_focus_characters(self, novel: Novel) -> List[Character]:
        """选择本章节的焦点角色"""
        # 简单逻辑：随机选择2-3个角色作为焦点
        import random
        characters = list(novel.characters.values())
        if not characters:
            return []
            
        num_focus = min(len(characters), random.randint(2, 3))
        return random.sample(characters, num_focus)
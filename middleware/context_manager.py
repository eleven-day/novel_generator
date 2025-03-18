# middleware/context_manager.py - 上下文管理中间件

from typing import Optional
from core.models import Novel

class ContextManager:
    """上下文管理中间件"""
    
    def set_global_context(self, novel: Novel, context: str) -> bool:
        """设置全局上下文"""
        novel.context.global_context = context
        novel.update_modified()
        return True
    
    def get_global_context(self, novel: Novel) -> str:
        """获取全局上下文"""
        return novel.context.global_context
    
    def set_chapter_context(self, novel: Novel, chapter_number: int, context: str) -> bool:
        """设置特定章节的上下文"""
        novel.context.set_chapter_context(chapter_number, context)
        novel.update_modified()
        return True
    
    def get_chapter_context(self, novel: Novel, chapter_number: int) -> str:
        """获取特定章节的上下文"""
        return novel.context.get_context_for_chapter(chapter_number)
    
    def clear_chapter_context(self, novel: Novel, chapter_number: int) -> bool:
        """清除特定章节的上下文"""
        if chapter_number in novel.context.chapter_context:
            del novel.context.chapter_context[chapter_number]
            novel.update_modified()
            return True
        return False
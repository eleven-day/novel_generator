# ui/cli.py - 命令行界面

import os
import sys
from typing import Dict, Any, List, Optional
from core.models import Novel, Character, Event, Chapter
from core.llm_interface import LLMInterface
from core.event_engine import EventEngine
from core.narrative_generator import NarrativeGenerator
from middleware.character_manager import CharacterManager
from middleware.event_manager import EventManager
from middleware.outline_manager import OutlineManager
from middleware.chapter_manager import ChapterManager
from middleware.context_manager import ContextManager
from utils.file_utils import save_novel_to_xml, load_novel_from_xml, export_to_text, list_saved_novels
from utils.logger import Logger

class CLI:
    """命令行界面"""
    
    def __init__(self):
        # 初始化日志
        self.logger = Logger()
        
        # 初始化LLM接口
        try:
            self.llm = LLMInterface()
        except ValueError as e:
            self.logger.error(f"初始化LLM接口失败: {e}")
            print("错误: 请确保设置了OPENAI_API_KEY环境变量")
            sys.exit(1)
        
        # 初始化其他组件
        self.event_engine = EventEngine()
        self.narrative_generator = NarrativeGenerator(self.llm)
        
        # 初始化中间件
        self.character_manager = CharacterManager(self.llm)
        self.event_manager = EventManager(self.llm)
        self.outline_manager = OutlineManager(self.llm)
        self.chapter_manager = ChapterManager(self.narrative_generator, self.event_engine)
        self.context_manager = ContextManager()
        
        # 当前小说
        self.current_novel = None
        
        # 保存目录
        self.save_dir = "saves"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 导出目录
        self.export_dir = "exports"
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def run(self):
        """运行CLI"""
        print("欢迎使用小说生成系统")
        
        while True:
            self._show_main_menu()
            choice = input("请输入选项: ").strip()
            
            if choice == "1":
                self._create_novel_menu()
            elif choice == "2":
                self._load_novel_menu()
            elif choice == "3":
                if not self._check_novel():
                    continue
                self._manage_characters_menu()
            elif choice == "4":
                if not self._check_novel():
                    continue
                self._manage_events_menu()
            elif choice == "5":
                if not self._check_novel():
                    continue
                self._manage_outline_menu()
            elif choice == "6":
                if not self._check_novel():
                    continue
                self._manage_chapters_menu()
            elif choice == "7":
                if not self._check_novel():
                    continue
                self._manage_context_menu()
            elif choice == "8":
                if not self._check_novel():
                    continue
                self._save_novel_menu()
            elif choice == "9":
                if not self._check_novel():
                    continue
                self._export_novel_menu()
            elif choice == "10":
                self._settings_menu()
            elif choice == "0":
                print("感谢使用，再见！")
                break
            else:
                print("无效选项，请重新选择")
    
    def _check_novel(self):
        """检查当前是否有小说"""
        if self.current_novel is None:
            print("请先创建或加载小说")
            return False
        return True
    
    def _show_main_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("小说生成系统 - 主菜单")
        print("="*50)
        
        if self.current_novel:
            print(f"当前小说: 《{self.current_novel.title}》({self.current_novel.genre}) - {len(self.current_novel.chapters)}章")
        
        print("\n1. 创建新小说")
        print("2. 加载小说")
        
        if self.current_novel:
            print("3. 管理角色")
            print("4. 管理事件")
            print("5. 管理大纲")
            print("6. 管理章节")
            print("7. 管理上下文")
            print("8. 保存小说")
            print("9. 导出小说")
        
        print("10. 设置")
        print("0. 退出")
        print("-"*50)
    
    def _create_novel_menu(self):
        """创建新小说菜单"""
        print("\n" + "="*50)
        print("创建新小说")
        print("="*50)
        
        title = input("请输入小说标题: ").strip()
        if not title:
            print("标题不能为空")
            return
            
        genre = input("请输入小说类型(如奇幻、科幻、悬疑等): ").strip()
        if not genre:
            print("类型不能为空")
            return
            
        setting = input("请输入小说背景设定: ").strip()
        if not setting:
            print("背景设定不能为空")
            return
        
        self.current_novel = Novel.create(title, genre, setting)
        self.logger.info(f"创建了新小说: {title}")
        print(f"\n已创建新小说: 《{title}》")
        
        # 询问是否生成角色
        if input("\n是否立即生成角色? (y/n): ").strip().lower() == 'y':
            self._generate_characters_menu()
        
        # 询问是否生成大纲
        if input("\n是否生成故事大纲? (y/n): ").strip().lower() == 'y':
            self._generate_outline()
    
    def _load_novel_menu(self):
        """加载小说菜单"""
        print("\n" + "="*50)
        print("加载小说")
        print("="*50)
        
        saved_novels = list_saved_novels(self.save_dir)
        
        if not saved_novels:
            print("没有找到保存的小说")
            return
        
        print("\n可用的小说文件:")
        for i, novel_info in enumerate(saved_novels, 1):
            print(f"{i}. {novel_info['title']} - {novel_info['genre']} ({novel_info['chapters']}章)")
        
        print("0. 返回")
        
        choice = input("\n请选择要加载的小说: ").strip()
        if choice == "0":
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(saved_novels):
                filename = saved_novels[index]["filename"]
                path = os.path.join(self.save_dir, filename)
                
                novel = load_novel_from_xml(path)
                if novel:
                    self.current_novel = novel
                    self.logger.info(f"加载了小说: {novel.title}")
                    print(f"已加载小说: 《{novel.title}》")
                else:
                    print("加载小说失败")
            else:
                print("无效选项")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_characters_menu(self):
        """管理角色菜单"""
        while True:
            print("\n" + "="*50)
            print("管理角色")
            print("="*50)
            
            characters = self.character_manager.get_all_characters(self.current_novel)
            
            print("\n当前角色:")
            for i, char in enumerate(characters, 1):
                print(f"{i}. {char.name} ({char.gender}, {char.age}岁)")
            
            print("\n1. 查看角色详情")
            print("2. 手动创建角色")
            print("3. 生成新角色")
            print("4. 编辑角色")
            print("5. 删除角色")
            print("6. 管理角色关系")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._view_character_details(characters)
            elif choice == "2":
                self._create_character_manually()
            elif choice == "3":
                self._generate_characters_menu()
            elif choice == "4":
                self._edit_character(characters)
            elif choice == "5":
                self._delete_character(characters)
            elif choice == "6":
                self._manage_character_relationships(characters)
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _view_character_details(self, characters: List[Character]):
        """查看角色详情"""
        if not characters:
            print("没有可查看的角色")
            return
        
        print("\n选择要查看的角色:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char.name}")
        
        choice = input("\n请输入角色编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(characters):
                char = characters[index]
                
                print("\n" + "="*50)
                print(f"角色详情: {char.name}")
                print("="*50)
                print(f"ID: {char.id}")
                print(f"年龄: {char.age}岁")
                print(f"性别: {char.gender}")
                print(f"外貌: {char.appearance}")
                print(f"背景: {char.background}")
                
                print("\n性格特征:")
                for trait, value in char.personality.items():
                    print(f"- {trait}: {value:.2f}")
                
                print("\n特质:")
                for trait in char.traits:
                    print(f"- {trait.name}: {trait.description}")
                
                print("\n目标:")
                for goal in char.goals:
                    print(f"- {goal}")
                
                print("\n关系:")
                for rel_id, rel in char.relationships.items():
                    if rel.target_id in self.current_novel.characters:
                        target_name = self.current_novel.characters[rel.target_id].name
                        print(f"- 与{target_name}: {rel.relationship_type} (强度: {rel.strength:.2f})")
                
                print("\n备注:")
                print(char.notes or "(无)")
                
                input("\n按Enter继续...")
            else:
                print("无效的角色编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _create_character_manually(self):
        """手动创建角色"""
        print("\n" + "="*50)
        print("手动创建角色")
        print("="*50)
        
        name = input("角色名: ").strip()
        if not name:
            print("角色名不能为空")
            return
        
        try:
            age_input = input("年龄: ").strip()
            age = int(age_input) if age_input else 30
        except ValueError:
            print("年龄必须是数字，设为30")
            age = 30
        
        gender = input("性别: ").strip()
        background = input("背景故事: ").strip()
        appearance = input("外貌描述: ").strip()
        
        character = self.character_manager.create_character(
            self.current_novel, name, age, gender, background
        )
        character.appearance = appearance
        
        self.logger.info(f"手动创建了角色: {name}")
        print(f"\n已创建角色: {character.name}")
        
        # 添加性格特征
        print("\n添加性格特征 (输入空白行完成)")
        while True:
            trait = input("特征 (格式: 名称 数值): ").strip()
            if not trait:
                break
            
            parts = trait.rsplit(" ", 1)
            if len(parts) == 2:
                try:
                    trait_name = parts[0].strip()
                    trait_value = float(parts[1].strip())
                    character.personality[trait_name] = trait_value
                    print(f"已添加特征: {trait_name} = {trait_value}")
                except ValueError:
                    print("格式错误，示例: 勇气 0.7")
            else:
                print("格式错误，示例: 勇气 0.7")
        
        # 添加目标
        print("\n添加角色目标 (输入空白行完成)")
        while True:
            goal = input("目标: ").strip()
            if not goal:
                break
            
            character.goals.append(goal)
            print(f"已添加目标: {goal}")
    
    def _generate_characters_menu(self):
        """生成角色菜单"""
        print("\n" + "="*50)
        print("生成角色")
        print("="*50)
        
        try:
            num_chars = int(input("要生成多少个角色? (1-5): ").strip())
            num_chars = max(1, min(5, num_chars))
        except ValueError:
            print("输入无效，将生成1个角色")
            num_chars = 1
        
        print("\n生成角色中...")
        
        for i in range(num_chars):
            try:
                character = self.character_manager.generate_character(self.current_novel)
                print(f"已生成角色: {character.name}")
            except Exception as e:
                self.logger.error(f"生成角色失败: {e}")
                print(f"生成第{i+1}个角色时出错，跳过")
        
        self.logger.info(f"生成了{num_chars}个角色")
        print(f"\n成功生成角色")
    
    def _edit_character(self, characters: List[Character]):
        """编辑角色"""
        if not characters:
            print("没有可编辑的角色")
            return
        
        print("\n选择要编辑的角色:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char.name}")
        
        choice = input("\n请输入角色编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(characters):
                char = characters[index]
                
                print("\n" + "="*50)
                print(f"编辑角色: {char.name}")
                print("="*50)
                print("(直接按Enter保留原值)")
                
                name = input(f"角色名 [{char.name}]: ").strip() or char.name
                
                age_str = input(f"年龄 [{char.age}]: ").strip()
                age = int(age_str) if age_str else char.age
                
                gender = input(f"性别 [{char.gender}]: ").strip() or char.gender
                
                background = input(f"背景 (输入'.'保留原值)\n[{char.background[:50]}...]: ").strip()
                if background == ".":
                    background = char.background
                
                appearance = input(f"外貌 (输入'.'保留原值)\n[{char.appearance[:50]}...]: ").strip()
                if appearance == ".":
                    appearance = char.appearance
                
                notes = input(f"备注 (输入'.'保留原值)\n[{char.notes[:50]}...]: ").strip()
                if notes == ".":
                    notes = char.notes
                
                # 更新角色
                data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "background": background,
                    "appearance": appearance,
                    "notes": notes
                }
                
                updated_char = self.character_manager.update_character(self.current_novel, char.id, data)
                
                self.logger.info(f"编辑了角色: {updated_char.name}")
                print(f"\n已更新角色: {updated_char.name}")
            else:
                print("无效的角色编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _delete_character(self, characters: List[Character]):
        """删除角色"""
        if not characters:
            print("没有可删除的角色")
            return
        
        print("\n选择要删除的角色:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char.name}")
        
        choice = input("\n请输入角色编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(characters):
                char = characters[index]
                
                confirm = input(f"\n确定要删除 {char.name}? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.character_manager.delete_character(self.current_novel, char.id)
                    self.logger.info(f"删除了角色: {char.name}")
                    print(f"已删除角色: {char.name}")
                else:
                    print("已取消删除")
            else:
                print("无效的角色编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_character_relationships(self, characters: List[Character]):
        """管理角色关系"""
        if len(characters) < 2:
            print("需要至少两个角色才能管理关系")
            return
        
        print("\n" + "="*50)
        print("管理角色关系")
        print("="*50)
        
        print("\n选择要管理关系的角色:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char.name}")
        
        choice = input("\n请输入角色编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(characters):
                char1 = characters[index]
                
                print(f"\n{char1.name}的当前关系:")
                for rel_id, rel in char1.relationships.items():
                    if rel.target_id in self.current_novel.characters:
                        target_name = self.current_novel.characters[rel.target_id].name
                        print(f"- 与{target_name}: {rel.relationship_type} (强度: {rel.strength:.2f})")
                
                print("\n选择要管理关系的目标角色:")
                other_chars = [c for c in characters if c.id != char1.id]
                for i, char in enumerate(other_chars, 1):
                    print(f"{i}. {char.name}")
                
                target_choice = input("\n请输入目标角色编号(0返回): ").strip()
                if target_choice == "0":
                    return
                    
                target_index = int(target_choice) - 1
                if 0 <= target_index < len(other_chars):
                    char2 = other_chars[target_index]
                    
                    print(f"\n编辑 {char1.name} 与 {char2.name} 的关系")
                    
                    # 显示当前关系
                    current_rel = char1.relationships.get(char2.id)
                    if current_rel:
                        print(f"当前关系: {current_rel.relationship_type} (强度: {current_rel.strength:.2f})")
                    else:
                        print("当前没有直接关系")
                    
                    # 编辑关系
                    rel_type = input("关系类型 (如朋友/敌人/亲戚等): ").strip()
                    if not rel_type:
                        print("操作取消")
                        return
                    
                    try:
                        strength_input = input("关系强度 (-1.0到1.0): ").strip()
                        strength = float(strength_input)
                        if not (-1.0 <= strength <= 1.0):
                            raise ValueError("强度必须在-1.0到1.0之间")
                    except ValueError as e:
                        print(f"无效的强度值: {e}")
                        return
                    
                    event = input("关系变化原因: ").strip() or "手动设置关系"
                    
                    # 更新关系
                    if current_rel:
                        # 计算变化量
                        strength_change = strength - current_rel.strength
                    else:
                        # 新关系，直接设置
                        strength_change = strength
                    
                    self.character_manager.update_relationship(
                        self.current_novel, char1.id, char2.id, rel_type, strength_change, event
                    )
                    
                    # 更新对方到本人的关系(对称性)
                    if input("是否同时更新反向关系? (y/n): ").strip().lower() == 'y':
                        self.character_manager.update_relationship(
                            self.current_novel, char2.id, char1.id, rel_type, strength_change, event
                        )
                    
                    self.logger.info(f"更新了角色关系: {char1.name} - {char2.name}")
                    print(f"\n已更新 {char1.name} 与 {char2.name} 的关系")
                else:
                    print("无效的目标角色编号")
            else:
                print("无效的角色编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_events_menu(self):
        """管理事件菜单"""
        while True:
            print("\n" + "="*50)
            print("管理事件")
            print("="*50)
            
            events = self.event_manager.get_all_events(self.current_novel)
            
            print("\n当前事件:")
            for i, event in enumerate(events, 1):
                print(f"{i}. {event.name}")
            
            print("\n1. 查看事件详情")
            print("2. 手动创建事件")
            print("3. 生成新事件")
            print("4. 编辑事件")
            print("5. 删除事件")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._view_event_details(events)
            elif choice == "2":
                self._create_event_manually()
            elif choice == "3":
                self._generate_events_menu()
            elif choice == "4":
                self._edit_event(events)
            elif choice == "5":
                self._delete_event(events)
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _view_event_details(self, events: List[Event]):
        """查看事件详情"""
        if not events:
            print("没有可查看的事件")
            return
        
        print("\n选择要查看的事件:")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.name}")
        
        choice = input("\n请输入事件编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(events):
                event = events[index]
                
                print("\n" + "="*50)
                print(f"事件详情: {event.name}")
                print("="*50)
                print(f"ID: {event.id}")
                print(f"描述: {event.description}")
                
                print("\n触发条件:")
                if event.triggers:
                    for trig_type, trig_value in event.triggers.items():
                        print(f"- {trig_type}: {trig_value}")
                else:
                    print("(无触发条件)")
                
                print("\n效果:")
                if event.effects:
                    for effect in event.effects:
                        print(f"- {effect['target']}: {effect['value']}")
                else:
                    print("(无效果)")
                
                print("\n叙事模板:")
                if event.narrative_templates:
                    for i, template in enumerate(event.narrative_templates, 1):
                        print(f"{i}. {template[:100]}...")
                else:
                    print("(无叙事模板)")
                
                print("\n备注:")
                print(event.notes or "(无)")
                
                input("\n按Enter继续...")
            else:
                print("无效的事件编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _create_event_manually(self):
        """手动创建事件"""
        print("\n" + "="*50)
        print("手动创建事件")
        print("="*50)
        
        name = input("事件名称: ").strip()
        if not name:
            print("事件名称不能为空")
            return
            
        description = input("事件描述: ").strip()
        
        event = self.event_manager.create_event(self.current_novel, name, description)
        
        self.logger.info(f"手动创建了事件: {name}")
        print(f"\n已创建事件: {event.name}")
        
        # 添加触发条件
        print("\n添加触发条件 (输入空白行完成)")
        while True:
            trigger = input("触发条件 (格式: 类型 值): ").strip()
            if not trigger:
                break
            
            parts = trigger.split(" ", 1)
            if len(parts) == 2:
                trig_type = parts[0].strip()
                trig_value = parts[1].strip()
                event.triggers[trig_type] = trig_value
                print(f"已添加触发条件: {trig_type} = {trig_value}")
            else:
                print("格式错误，示例: character_relation 朋友")
        
        # 添加效果
        print("\n添加效果 (输入空白行完成)")
        while True:
            effect = input("效果 (格式: 目标 值): ").strip()
            if not effect:
                break
            
            parts = effect.rsplit(" ", 1)
            if len(parts) == 2:
                try:
                    effect_target = parts[0].strip()
                    effect_value = float(parts[1].strip())
                    event.effects.append({
                        "target": effect_target,
                        "value": effect_value
                    })
                    print(f"已添加效果: {effect_target} = {effect_value}")
                except ValueError:
                    print("格式错误，示例: character_relation 0.2")
            else:
                print("格式错误，示例: character_relation 0.2")
        
        # 添加叙事模板
        print("\n添加叙事模板 (输入空白行完成)")
        while True:
            template = input("模板: ").strip()
            if not template:
                break
            
            event.narrative_templates.append(template)
            print(f"已添加模板: {template[:50]}...")
    
    def _generate_events_menu(self):
        """生成事件菜单"""
        print("\n" + "="*50)
        print("生成事件")
        print("="*50)
        
        try:
            num_events = int(input("要生成多少个事件? (1-5): ").strip())
            num_events = max(1, min(5, num_events))
        except ValueError:
            print("输入无效，将生成3个事件")
            num_events = 3
        
        print("\n生成事件中...")
        
        try:
            events = self.event_manager.generate_events(self.current_novel, num_events)
            
            for event in events:
                print(f"已生成事件: {event.name}")
            
            self.logger.info(f"生成了{len(events)}个事件")
            print(f"\n成功生成了{len(events)}个事件")
        except Exception as e:
            self.logger.error(f"生成事件失败: {e}")
            print(f"生成事件时出错: {e}")
    
    def _edit_event(self, events: List[Event]):
        """编辑事件"""
        if not events:
            print("没有可编辑的事件")
            return
        
        print("\n选择要编辑的事件:")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.name}")
        
        choice = input("\n请输入事件编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(events):
                event = events[index]
                
                print("\n" + "="*50)
                print(f"编辑事件: {event.name}")
                print("="*50)
                print("(直接按Enter保留原值)")
                
                name = input(f"事件名称 [{event.name}]: ").strip() or event.name
                
                description = input(f"描述 (输入'.'保留原值)\n[{event.description[:50]}...]: ").strip()
                if description == ".":
                    description = event.description
                
                notes = input(f"备注 (输入'.'保留原值)\n[{event.notes[:50]}...]: ").strip()
                if notes == ".":
                    notes = event.notes
                
                # 编辑触发条件
                edit_triggers = input("\n是否编辑触发条件? (y/n): ").strip().lower()
                triggers = event.triggers.copy()
                
                if edit_triggers == 'y':
                    # 显示当前触发条件
                    print("\n当前触发条件:")
                    for trig_type, trig_value in triggers.items():
                        print(f"- {trig_type}: {trig_value}")
                    
                    # 清空还是编辑?
                    if input("清空当前触发条件? (y/n): ").strip().lower() == 'y':
                        triggers = {}
                    
                    # 添加新触发条件
                    print("\n添加触发条件 (输入空白行完成)")
                    while True:
                        trigger = input("触发条件 (格式: 类型 值): ").strip()
                        if not trigger:
                            break
                        
                        parts = trigger.split(" ", 1)
                        if len(parts) == 2:
                            trig_type = parts[0].strip()
                            trig_value = parts[1].strip()
                            triggers[trig_type] = trig_value
                            print(f"已添加触发条件: {trig_type} = {trig_value}")
                        else:
                            print("格式错误，示例: character_relation 朋友")
                
                # 编辑效果
                edit_effects = input("\n是否编辑效果? (y/n): ").strip().lower()
                effects = event.effects.copy()
                
                if edit_effects == 'y':
                    # 显示当前效果
                    print("\n当前效果:")
                    for effect in effects:
                        print(f"- {effect['target']}: {effect['value']}")
                    
                    # 清空还是编辑?
                    if input("清空当前效果? (y/n): ").strip().lower() == 'y':
                        effects = []
                    
                    # 添加新效果
                    print("\n添加效果 (输入空白行完成)")
                    while True:
                        effect = input("效果 (格式: 目标 值): ").strip()
                        if not effect:
                            break
                        
                        parts = effect.rsplit(" ", 1)
                        if len(parts) == 2:
                            try:
                                effect_target = parts[0].strip()
                                effect_value = float(parts[1].strip())
                                effects.append({
                                    "target": effect_target,
                                    "value": effect_value
                                })
                                print(f"已添加效果: {effect_target} = {effect_value}")
                            except ValueError:
                                print("格式错误，示例: character_relation 0.2")
                        else:
                            print("格式错误，示例: character_relation 0.2")
                
                # 编辑叙事模板
                edit_templates = input("\n是否编辑叙事模板? (y/n): ").strip().lower()
                templates = event.narrative_templates.copy()
                
                if edit_templates == 'y':
                    # 显示当前模板
                    print("\n当前叙事模板:")
                    for i, template in enumerate(templates, 1):
                        print(f"{i}. {template[:100]}...")
                    
                    # 清空还是编辑?
                    if input("清空当前叙事模板? (y/n): ").strip().lower() == 'y':
                        templates = []
                    
                    # 添加新模板
                    print("\n添加叙事模板 (输入空白行完成)")
                    while True:
                        template = input("模板: ").strip()
                        if not template:
                            break
                        
                        templates.append(template)
                        print(f"已添加模板: {template[:50]}...")
                
                # 更新事件
                data = {
                    "name": name,
                    "description": description,
                    "notes": notes,
                    "triggers": triggers,
                    "effects": effects,
                    "narrative_templates": templates
                }
                
                updated_event = self.event_manager.update_event(self.current_novel, event.id, data)
                
                self.logger.info(f"编辑了事件: {updated_event.name}")
                print(f"\n已更新事件: {updated_event.name}")
            else:
                print("无效的事件编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _delete_event(self, events: List[Event]):
        """删除事件"""
        if not events:
            print("没有可删除的事件")
            return
        
        print("\n选择要删除的事件:")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.name}")
        
        choice = input("\n请输入事件编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(events):
                event = events[index]
                
                confirm = input(f"\n确定要删除 {event.name}? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.event_manager.delete_event(self.current_novel, event.id)
                    self.logger.info(f"删除了事件: {event.name}")
                    print(f"已删除事件: {event.name}")
                else:
                    print("已取消删除")
            else:
                print("无效的事件编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_outline_menu(self):
        """管理大纲菜单"""
        while True:
            print("\n" + "="*50)
            print("管理大纲")
            print("="*50)
            
            if self.current_novel.outline:
                outline = self.current_novel.outline
                print(f"\n大纲概述: {outline.overview[:100]}...")
                
                print("\n情节弧:")
                for i, arc in enumerate(outline.arcs, 1):
                    print(f"{i}. {arc.name}: {arc.description[:50]}...")
            else:
                print("\n当前小说没有大纲")
            
            print("\n1. 查看完整大纲")
            print("2. 手动创建大纲")
            print("3. 生成大纲")
            print("4. 编辑大纲")
            print("5. 添加情节弧")
            print("6. 编辑情节弧")
            print("7. 删除情节弧")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._view_outline()
            elif choice == "2":
                self._create_outline_manually()
            elif choice == "3":
                self._generate_outline()
            elif choice == "4":
                self._edit_outline()
            elif choice == "5":
                self._add_arc()
            elif choice == "6":
                self._edit_arc()
            elif choice == "7":
                self._delete_arc()
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _view_outline(self):
        """查看完整大纲"""
        if not self.current_novel.outline:
            print("当前小说没有大纲")
            return
        
        outline = self.current_novel.outline
        
        print("\n" + "="*50)
        print("完整大纲")
        print("="*50)
        
        print(f"概述: {outline.overview}")
        
        print("\n情节弧:")
        for i, arc in enumerate(outline.arcs, 1):
            print(f"\n{i}. {arc.name}")
            print(f"   描述: {arc.description}")
            
            print("   关键事件:")
            for j, event in enumerate(arc.key_events, 1):
                print(f"   {j}) {event}")
        
        input("\n按Enter继续...")
    
    def _create_outline_manually(self):
        """手动创建大纲"""
        print("\n" + "="*50)
        print("手动创建大纲")
        print("="*50)
        
        overview = input("大纲概述: ").strip()
        if not overview:
            print("大纲概述不能为空")
            return
        
        outline = self.outline_manager.create_outline(self.current_novel, overview)
        
        self.logger.info("手动创建了大纲")
        print(f"\n已创建大纲")
        
        # 添加情节弧
        if input("是否现在添加情节弧? (y/n): ").strip().lower() == 'y':
            self._add_arc()
    
    def _generate_outline(self):
        """生成大纲"""
        print("\n生成大纲中...")
        
        try:
            outline = self.outline_manager.generate_outline(self.current_novel)
            
            self.logger.info("生成了大纲")
            print("\n大纲生成完成!")
            print(f"概述: {outline.overview[:100]}...")
            print(f"情节弧数量: {len(outline.arcs)}")
        except Exception as e:
            self.logger.error(f"生成大纲失败: {e}")
            print(f"生成大纲时出错: {e}")
    
    def _edit_outline(self):
        """编辑大纲"""
        if not self.current_novel.outline:
            print("当前小说没有大纲")
            return
        
        outline = self.current_novel.outline
        
        print("\n" + "="*50)
        print("编辑大纲")
        print("="*50)
        print("(直接按Enter保留原值)")
        
        overview = input(f"概述 (输入'.'保留原值)\n[{outline.overview[:50]}...]: ").strip()
        if overview == ".":
            overview = outline.overview
        
        # 更新大纲
        data = {
            "overview": overview
        }
        
        self.outline_manager.update_outline(self.current_novel, data)
        
        self.logger.info("编辑了大纲概述")
        print("\n已更新大纲")
    
    def _add_arc(self):
        """添加情节弧"""
        print("\n" + "="*50)
        print("添加情节弧")
        print("="*50)
        
        name = input("情节弧名称: ").strip()
        if not name:
            print("情节弧名称不能为空")
            return
            
        description = input("情节弧描述: ").strip()
        
        arc = self.outline_manager.add_arc(self.current_novel, name, description)
        
        self.logger.info(f"添加了情节弧: {name}")
        print(f"\n已添加情节弧: {arc.name}")
        
        # 添加关键事件
        print("\n添加关键事件 (输入空白行完成)")
        while True:
            event = input("关键事件: ").strip()
            if not event:
                break
            
            arc.key_events.append(event)
            print(f"已添加关键事件: {event}")
    
    def _edit_arc(self):
        """编辑情节弧"""
        if not self.current_novel.outline or not self.current_novel.outline.arcs:
            print("没有可编辑的情节弧")
            return
        
        print("\n选择要编辑的情节弧:")
        for i, arc in enumerate(self.current_novel.outline.arcs, 1):
            print(f"{i}. {arc.name}")
        
        choice = input("\n请输入情节弧编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.current_novel.outline.arcs):
                arc = self.current_novel.outline.arcs[index]
                
                print("\n" + "="*50)
                print(f"编辑情节弧: {arc.name}")
                print("="*50)
                print("(直接按Enter保留原值)")
                
                name = input(f"名称 [{arc.name}]: ").strip() or arc.name
                
                description = input(f"描述 (输入'.'保留原值)\n[{arc.description[:50]}...]: ").strip()
                if description == ".":
                    description = arc.description
                
                # 更新情节弧
                arc.name = name
                arc.description = description
                
                # 编辑关键事件
                edit_events = input("\n是否编辑关键事件? (y/n): ").strip().lower()
                if edit_events == 'y':
                    # 显示当前关键事件
                    print("\n当前关键事件:")
                    for i, event in enumerate(arc.key_events, 1):
                        print(f"{i}. {event}")
                    
                    # 清空还是编辑?
                    if input("清空当前关键事件? (y/n): ").strip().lower() == 'y':
                        arc.key_events = []
                    
                    # 添加新关键事件
                    print("\n添加关键事件 (输入空白行完成)")
                    while True:
                        event = input("关键事件: ").strip()
                        if not event:
                            break
                        
                        arc.key_events.append(event)
                        print(f"已添加关键事件: {event}")
                
                self.current_novel.update_modified()
                self.logger.info(f"编辑了情节弧: {arc.name}")
                print(f"\n已更新情节弧: {arc.name}")
            else:
                print("无效的情节弧编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _delete_arc(self):
        """删除情节弧"""
        if not self.current_novel.outline or not self.current_novel.outline.arcs:
            print("没有可删除的情节弧")
            return
        
        print("\n选择要删除的情节弧:")
        for i, arc in enumerate(self.current_novel.outline.arcs, 1):
            print(f"{i}. {arc.name}")
        
        choice = input("\n请输入情节弧编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.current_novel.outline.arcs):
                arc = self.current_novel.outline.arcs[index]
                
                confirm = input(f"\n确定要删除 {arc.name}? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.outline_manager.delete_arc(self.current_novel, index)
                    self.logger.info(f"删除了情节弧: {arc.name}")
                    print(f"已删除情节弧: {arc.name}")
                else:
                    print("已取消删除")
            else:
                print("无效的情节弧编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_chapters_menu(self):
        """管理章节菜单"""
        while True:
            print("\n" + "="*50)
            print("管理章节")
            print("="*50)
            
            chapters = self.chapter_manager.get_all_chapters(self.current_novel)
            
            print(f"\n当前章节数: {len(chapters)}")
            for i, chapter in enumerate(chapters, 1):
                print(f"{i}. {chapter.title}{' (用户编辑)' if chapter.user_edited else ''}")
            
            print("\n1. 查看章节内容")
            print("2. 手动创建章节")
            print("3. 生成新章节")
            print("4. 编辑章节")
            print("5. 删除章节")
            print("6. 重新生成章节")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._view_chapter_content(chapters)
            elif choice == "2":
                self._create_chapter_manually()
            elif choice == "3":
                self._generate_chapter()
            elif choice == "4":
                self._edit_chapter(chapters)
            elif choice == "5":
                self._delete_chapter(chapters)
            elif choice == "6":
                self._regenerate_chapter(chapters)
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _view_chapter_content(self, chapters: List[Chapter]):
        """查看章节内容"""
        if not chapters:
            print("没有可查看的章节")
            return
        
        print("\n选择要查看的章节:")
        for i, chapter in enumerate(chapters, 1):
            print(f"{i}. {chapter.title}")
        
        choice = input("\n请输入章节编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(chapters):
                chapter = chapters[index]
                
                print("\n" + "="*50)
                print(f"第{chapter.number}章: {chapter.title}")
                print("="*50)
                
                # 显示焦点角色
                focus_chars = []
                for char_id in chapter.character_focus:
                    if char_id in self.current_novel.characters:
                        focus_chars.append(self.current_novel.characters[char_id].name)
                
                if focus_chars:
                    print(f"焦点角色: {', '.join(focus_chars)}")
                
                # 显示事件
                events = []
                for event_id in chapter.events:
                    if event_id in self.current_novel.events_library:
                        events.append(self.current_novel.events_library[event_id].name)
                
                if events:
                    print(f"事件: {', '.join(events)}")
                
                print("\n" + "-"*50)
                print(chapter.content)
                print("-"*50)
                
                print(f"\n摘要: {chapter.summary}")
                
                if chapter.notes:
                    print(f"\n备注: {chapter.notes}")
                
                input("\n按Enter继续...")
            else:
                print("无效的章节编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _create_chapter_manually(self):
        """手动创建章节"""
        print("\n" + "="*50)
        print("手动创建章节")
        print("="*50)
        
        title = input("章节标题: ").strip()
        if not title:
            print("章节标题不能为空")
            return
        
        chapter = self.chapter_manager.create_chapter(self.current_novel, title)
        
        print(f"\n已创建第{chapter.number}章: {chapter.title}")
        
        # 设置章节内容
        print("\n输入章节内容 (可多行，输入END单独一行结束):")
        full_content = []
        while True:
            content = input()
            if content == "END":
                break
            full_content.append(content)
        
        chapter.content = "\n".join(full_content)
        
        # 设置章节摘要
        summary = input("\n章节摘要: ").strip()
        chapter.summary = summary
        
        # 选择焦点角色
        self._select_focus_characters_for_chapter(chapter)
        
        # 选择事件
        self._select_events_for_chapter(chapter)
        
        self.logger.info(f"手动创建了章节: {chapter.title}")
        print(f"\n已完成第{chapter.number}章的创建")
    
    def _generate_chapter(self):
        """生成新章节"""
        print("\n生成新章节中...")
        
        try:
            chapter = self.chapter_manager.generate_chapter(self.current_novel)
            
            self.logger.info(f"生成了章节: {chapter.title}")
            print(f"\n已生成第{chapter.number}章: {chapter.title}")
        except Exception as e:
            self.logger.error(f"生成章节失败: {e}")
            print(f"生成章节时出错: {e}")
    
    def _edit_chapter(self, chapters: List[Chapter]):
        """编辑章节"""
        if not chapters:
            print("没有可编辑的章节")
            return
        
        print("\n选择要编辑的章节:")
        for i, chapter in enumerate(chapters, 1):
            print(f"{i}. {chapter.title}")
        
        choice = input("\n请输入章节编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(chapters):
                chapter = chapters[index]
                
                print("\n" + "="*50)
                print(f"编辑第{chapter.number}章: {chapter.title}")
                print("="*50)
                print("(直接按Enter保留原值)")
                
                title = input(f"章节标题 [{chapter.title}]: ").strip() or chapter.title
                
                print(f"\n当前章节内容 (前100字):\n{chapter.content[:100]}...")
                edit_content = input("\n是否编辑内容? (y/n): ").strip().lower()
                
                content = chapter.content
                if edit_content == 'y':
                    print("\n输入新内容 (可多行，输入END单独一行结束):")
                    content_lines = []
                    while True:
                        line = input()
                        if line == "END":
                            break
                        content_lines.append(line)
                    
                    if content_lines:
                        content = "\n".join(content_lines)
                
                summary = input(f"\n章节摘要 [{chapter.summary}]: ").strip() or chapter.summary
                
                notes = input(f"\n备注 [{chapter.notes}]: ").strip() or chapter.notes
                
                # 更新章节
                data = {
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "notes": notes
                }
                
                updated_chapter = self.chapter_manager.update_chapter(
                    self.current_novel, chapter.number, data
                )
                
                # 是否更新焦点角色
                if input("\n是否更新焦点角色? (y/n): ").strip().lower() == 'y':
                    self._select_focus_characters_for_chapter(updated_chapter)
                
                # 是否更新事件
                if input("\n是否更新事件? (y/n): ").strip().lower() == 'y':
                    self._select_events_for_chapter(updated_chapter)
                
                self.logger.info(f"编辑了章节: {updated_chapter.title}")
                print(f"\n已更新第{updated_chapter.number}章: {updated_chapter.title}")
            else:
                print("无效的章节编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _delete_chapter(self, chapters: List[Chapter]):
        """删除章节"""
        if not chapters:
            print("没有可删除的章节")
            return
        
        print("\n选择要删除的章节:")
        for i, chapter in enumerate(chapters, 1):
            print(f"{i}. {chapter.title}")
        
        choice = input("\n请输入章节编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(chapters):
                chapter = chapters[index]
                
                confirm = input(f"\n确定要删除第{chapter.number}章: {chapter.title}? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.chapter_manager.delete_chapter(self.current_novel, chapter.number)
                    self.logger.info(f"删除了章节: {chapter.title}")
                    print(f"已删除第{chapter.number}章: {chapter.title}")
                else:
                    print("已取消删除")
            else:
                print("无效的章节编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _regenerate_chapter(self, chapters: List[Chapter]):
        """重新生成章节"""
        if not chapters:
            print("没有可重新生成的章节")
            return
        
        print("\n选择要重新生成的章节:")
        for i, chapter in enumerate(chapters, 1):
            print(f"{i}. {chapter.title}")
        
        choice = input("\n请输入章节编号(0返回): ").strip()
        if choice == "0":
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(chapters):
                chapter = chapters[index]
                
                confirm = input(f"\n确定要重新生成第{chapter.number}章: {chapter.title}? (y/n): ").strip().lower()
                if confirm == 'y':
                    print("\n重新生成章节中...")
                    
                    # 保存原章节编号和焦点角色/事件
                    chapter_number = chapter.number
                    focus_chars = chapter.character_focus
                    events = chapter.events
                    
                    # 删除原章节
                    self.chapter_manager.delete_chapter(self.current_novel, chapter_number)
                    
                    # 确保current_chapter是正确的
                    self.current_novel.current_chapter = chapter_number - 1
                    
                    # 生成新章节
                    try:
                        new_chapter = self.chapter_manager.generate_chapter(self.current_novel)
                        
                        self.logger.info(f"重新生成了章节: {new_chapter.title}")
                        print(f"\n已重新生成第{new_chapter.number}章: {new_chapter.title}")
                    except Exception as e:
                        self.logger.error(f"重新生成章节失败: {e}")
                        print(f"重新生成章节时出错: {e}")
                else:
                    print("已取消重新生成")
            else:
                print("无效的章节编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _select_focus_characters_for_chapter(self, chapter: Chapter):
        """为章节选择焦点角色"""
        characters = self.character_manager.get_all_characters(self.current_novel)
        
        if not characters:
            print("没有可选择的角色")
            return
        
        print("\n选择焦点角色 (输入编号,用逗号分隔):")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char.name}")
        
        choice = input("\n请输入角色编号(0跳过): ").strip()
        if choice == "0":
            return
            
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            
            focus_char_ids = []
            for index in indices:
                if 0 <= index < len(characters):
                    focus_char_ids.append(characters[index].id)
            
            # 更新焦点角色
            chapter.character_focus = focus_char_ids
            
            # 更新角色名单
            focus_chars = [self.current_novel.characters[char_id].name 
                          for char_id in focus_char_ids 
                          if char_id in self.current_novel.characters]
            
            print(f"已设置焦点角色: {', '.join(focus_chars)}")
        except ValueError:
            print("请输入有效的数字")
    
    def _select_events_for_chapter(self, chapter: Chapter):
        """为章节选择事件"""
        events = self.event_manager.get_all_events(self.current_novel)
        
        if not events:
            print("没有可选择的事件")
            return
        
        print("\n选择章节事件 (输入编号,用逗号分隔):")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.name}")
        
        choice = input("\n请输入事件编号(0跳过): ").strip()
        if choice == "0":
            return
            
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            
            event_ids = []
            for index in indices:
                if 0 <= index < len(events):
                    event_ids.append(events[index].id)
            
            # 更新事件
            chapter.events = event_ids
            
            # 更新事件名单
            event_names = [self.current_novel.events_library[event_id].name 
                          for event_id in event_ids 
                          if event_id in self.current_novel.events_library]
            
            print(f"已设置事件: {', '.join(event_names)}")
        except ValueError:
            print("请输入有效的数字")
    
    def _manage_context_menu(self):
        """管理上下文菜单"""
        while True:
            print("\n" + "="*50)
            print("管理上下文")
            print("="*50)
            
            global_context = self.context_manager.get_global_context(self.current_novel)
            print(f"\n全局上下文: {global_context[:100]}..." if global_context else "\n无全局上下文")
            
            print("\n1. 查看全局上下文")
            print("2. 编辑全局上下文")
            print("3. 查看特定章节上下文")
            print("4. 编辑特定章节上下文")
            print("5. 清除特定章节上下文")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._view_global_context()
            elif choice == "2":
                self._edit_global_context()
            elif choice == "3":
                self._view_chapter_context()
            elif choice == "4":
                self._edit_chapter_context()
            elif choice == "5":
                self._clear_chapter_context()
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _view_global_context(self):
        """查看全局上下文"""
        context = self.context_manager.get_global_context(self.current_novel)
        
        print("\n" + "="*50)
        print("全局上下文")
        print("="*50)
        
        if context:
            print(context)
        else:
            print("无全局上下文")
        
        input("\n按Enter继续...")
    
    def _edit_global_context(self):
        """编辑全局上下文"""
        current_context = self.context_manager.get_global_context(self.current_novel)
        
        print("\n" + "="*50)
        print("编辑全局上下文")
        print("="*50)
        
        if current_context:
            print(f"当前上下文:\n{current_context}")
        
        print("\n输入新的全局上下文 (可多行，输入END单独一行结束):")
        context_lines = []
        while True:
            line = input()
            if line == "END":
                break
            context_lines.append(line)
        
        if context_lines:
            context = "\n".join(context_lines)
            self.context_manager.set_global_context(self.current_novel, context)
            self.logger.info("更新了全局上下文")
            print("\n已更新全局上下文")
        else:
            print("\n未更改全局上下文")
    
    def _view_chapter_context(self):
        """查看特定章节上下文"""
        try:
            chapter_num = int(input("\n请输入章节编号(0返回): ").strip())
            if chapter_num == 0:
                return
                
            if chapter_num < 0 or chapter_num > len(self.current_novel.chapters) + 1:
                print("无效的章节编号")
                return
            
            context = self.context_manager.get_chapter_context(self.current_novel, chapter_num)
            
            print("\n" + "="*50)
            print(f"第{chapter_num}章上下文")
            print("="*50)
            
            if context:
                print(context)
            else:
                print("该章节无特定上下文")
            
            input("\n按Enter继续...")
        except ValueError:
            print("请输入有效的数字")
    
    def _edit_chapter_context(self):
        """编辑特定章节上下文"""
        try:
            chapter_num = int(input("\n请输入章节编号(0返回): ").strip())
            if chapter_num == 0:
                return
                
            if chapter_num < 0 or chapter_num > len(self.current_novel.chapters) + 1:
                print("无效的章节编号")
                return
            
            current_context = self.context_manager.get_chapter_context(self.current_novel, chapter_num)
            
            print("\n" + "="*50)
            print(f"编辑第{chapter_num}章上下文")
            print("="*50)
            
            if current_context:
                print(f"当前上下文:\n{current_context}")
            
            print("\n输入新的章节上下文 (可多行，输入END单独一行结束):")
            context_lines = []
            while True:
                line = input()
                if line == "END":
                    break
                context_lines.append(line)
            
            if context_lines:
                context = "\n".join(context_lines)
                self.context_manager.set_chapter_context(self.current_novel, chapter_num, context)
                self.logger.info(f"更新了第{chapter_num}章上下文")
                print(f"\n已更新第{chapter_num}章上下文")
            else:
                print(f"\n未更改第{chapter_num}章上下文")
        except ValueError:
            print("请输入有效的数字")
    
    def _clear_chapter_context(self):
        """清除特定章节上下文"""
        try:
            chapter_num = int(input("\n请输入章节编号(0返回): ").strip())
            if chapter_num == 0:
                return
                
            if chapter_num <= 0:
                print("无效的章节编号")
                return
            
            if self.context_manager.clear_chapter_context(self.current_novel, chapter_num):
                self.logger.info(f"清除了第{chapter_num}章上下文")
                print(f"\n已清除第{chapter_num}章上下文")
            else:
                print(f"\n第{chapter_num}章没有特定上下文")
        except ValueError:
            print("请输入有效的数字")
    
    def _save_novel_menu(self):
        """保存小说菜单"""
        print("\n" + "="*50)
        print("保存小说")
        print("="*50)
        
        filename = input(f"请输入文件名 [默认: {self.current_novel.title}]: ").strip()
        
        if not filename:
            filename = self.current_novel.title
        
        # 移除不合法字符
        filename = "".join(c for c in filename if c.isalnum() or c in " _-")
        
        # 保存路径
        path = os.path.join(self.save_dir, f"{filename}.xml")
        
        # 检查文件是否存在
        if os.path.exists(path):
            confirm = input(f"文件 {path} 已存在，是否覆盖? (y/n): ").strip().lower()
            if confirm != 'y':
                print("保存已取消")
                return
        
        # 保存小说
        if save_novel_to_xml(self.current_novel, path):
            self.logger.info(f"保存了小说: {self.current_novel.title} 到 {path}")
            print(f"小说已保存到: {path}")
        else:
            self.logger.error(f"保存小说失败: {path}")
            print("保存小说失败")
    
    def _export_novel_menu(self):
        """导出小说菜单"""
        print("\n" + "="*50)
        print("导出小说")
        print("="*50)
        
        filename = input(f"请输入文件名 [默认: {self.current_novel.title}]: ").strip()
        
        if not filename:
            filename = self.current_novel.title
        
        # 移除不合法字符
        filename = "".join(c for c in filename if c.isalnum() or c in " _-")
        
        # 导出路径
        path = os.path.join(self.export_dir, f"{filename}.txt")
        
        # 检查文件是否存在
        if os.path.exists(path):
            confirm = input(f"文件 {path} 已存在，是否覆盖? (y/n): ").strip().lower()
            if confirm != 'y':
                print("导出已取消")
                return
        
        # 导出小说
        if export_to_text(self.current_novel, path):
            self.logger.info(f"导出了小说: {self.current_novel.title} 到 {path}")
            print(f"小说已导出到: {path}")
        else:
            self.logger.error(f"导出小说失败: {path}")
            print("导出小说失败")
    
    def _settings_menu(self):
        """设置菜单"""
        while True:
            print("\n" + "="*50)
            print("设置")
            print("="*50)
            
            print(f"\n当前LLM模型: {self.llm.model}")
            
            print("\n1. 更改LLM模型")
            print("2. 查看可用模型")
            print("0. 返回")
            
            choice = input("\n请输入选项: ").strip()
            
            if choice == "1":
                self._change_llm_model()
            elif choice == "2":
                self._view_available_models()
            elif choice == "0":
                break
            else:
                print("无效选项，请重新选择")
    
    def _change_llm_model(self):
        """更改LLM模型"""
        print("\n" + "="*50)
        print("更改LLM模型")
        print("="*50)
        
        print(f"当前模型: {self.llm.model}")
        
        model = input("\n请输入新模型名称 (如 gpt-4, gpt-3.5-turbo): ").strip()
        
        if model:
            try:
                self.llm.set_model(model)
                self.logger.info(f"更改了LLM模型: {model}")
                print(f"已切换到模型: {model}")
            except Exception as e:
                self.logger.error(f"更改模型失败: {e}")
                print(f"更改模型失败: {e}")
        else:
            print("未更改模型")
    
    def _view_available_models(self):
        """查看可用模型"""
        print("\n" + "="*50)
        print("可用LLM模型")
        print("="*50)
        
        try:
            models = self.llm.get_available_models()
            
            print("\n可用模型:")
            for model in models:
                print(f"- {model}")
            
            input("\n按Enter继续...")
        except Exception as e:
            self.logger.error(f"获取模型列表失败: {e}")
            print(f"获取模型列表失败: {e}")
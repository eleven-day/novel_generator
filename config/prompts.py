# config/prompts.py - 提示词配置

CHARACTER_CREATION_PROMPT = """
<task>请为一部{genre}类型的小说生成一个有深度的角色。</task>
<background>{background_info}</background>
<context>{context}</context>
<output_format>
请以下面的XML格式回复:
<character>
    <name>角色名</name>
    <age>年龄</age>
    <gender>性别</gender>
    <background>详细的背景故事</background>
    <appearance>外貌描述</appearance>
    <personality>
        <trait name="勇气">0.7</trait>
        <trait name="智慧">0.5</trait>
        <!-- 至少生成5个性格特征 -->
    </personality>
    <goals>
        <goal>角色的主要目标或动机</goal>
        <!-- 可以有多个 -->
    </goals>
</character>
</output_format>
"""

EVENT_GENERATION_PROMPT = """
<task>请为小说生成一系列潜在的事件，这些事件会在故事推进中触发。</task>
<novel_info>
    <title>{title}</title>
    <genre>{genre}</genre>
    <setting>{setting}</setting>
    <current_chapter>{current_chapter}</current_chapter>
</novel_info>
<characters>
{characters_info}
</characters>
<context>{context}</context>
<output_format>
请生成{num_events}个潜在事件，以下面的XML格式回复:
<events>
    <event>
        <id>event_id</id>
        <name>事件名称</name>
        <description>事件描述</description>
        <triggers>
            <trigger type="character_relation" value="朋友"/>
            <!-- 其他触发条件 -->
        </triggers>
        <effects>
            <effect target="character_relation" value="0.2"/>
            <!-- 其他效果 -->
        </effects>
        <narrative_template>这个事件在小说中的叙述模板，使用{character_name}作为占位符</narrative_template>
    </event>
    <!-- 更多事件 -->
</events>
</output_format>
"""

CHAPTER_GENERATION_PROMPT = """
<task>请为小说生成第{chapter_number}章的内容。</task>
<novel_info>
    <title>{title}</title>
    <genre>{genre}</genre>
    <setting>{setting}</setting>
</novel_info>
<outline>{outline}</outline>
<previous_summary>{previous_summary}</previous_summary>
<focus_characters>
{character_info}
</focus_characters>
<events>
{event_info}
</events>
<context>{context}</context>
<output_format>
请生成完整的章节内容，以下面的XML格式回复:
<chapter>
    <title>章节标题</title>
    <content>
        详细的章节内容，注重人物互动、关系发展和情节推进。请至少包含2000字的内容。
    </content>
    <summary>
        章节的简要总结，用于下一章的衔接
    </summary>
</chapter>
</output_format>
"""

OUTLINE_GENERATION_PROMPT = """
<task>请为一部{genre}类型的小说生成一个完整的故事大纲。</task>
<novel_info>
    <title>{title}</title>
    <setting>{setting}</setting>
</novel_info>
<characters>
{characters_info}
</characters>
<context>{context}</context>
<output_format>
请以下面的XML格式回复:
<outline>
    <overview>故事的整体概述和核心冲突</overview>
    <arc>
        <name>开端</name>
        <description>详细描述故事的开端阶段，包括世界设定、角色介绍和初始冲突</description>
        <key_events>
            <event>关键事件1</event>
            <event>关键事件2</event>
            <!-- 可以有多个 -->
        </key_events>
    </arc>
    <arc>
        <name>发展</name>
        <description>故事的发展阶段，冲突加剧</description>
        <key_events>
            <event>关键事件3</event>
            <event>关键事件4</event>
        </key_events>
    </arc>
    <arc>
        <name>高潮</name>
        <description>故事达到高潮，主要冲突面临解决</description>
        <key_events>
            <event>关键事件5</event>
            <event>关键事件6</event>
        </key_events>
    </arc>
    <arc>
        <name>结局</name>
        <description>故事的结局和收尾</description>
        <key_events>
            <event>关键事件7</event>
            <event>关键事件8</event>
        </key_events>
    </arc>
</outline>
</output_format>
"""
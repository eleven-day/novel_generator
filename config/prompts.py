# config/prompts.py - Prompt configurations

CHARACTER_CREATION_PROMPT = """
<task>Please generate a deep character for a novel in the {genre} genre.</task>
<background>{background_info}</background>
<context>{context}</context>
<output_format>
Please reply in the following XML format:
<character>
    <name>Character name</name>
    <age>Age</age>
    <gender>Gender</gender>
    <background>Detailed background story</background>
    <appearance>Appearance description</appearance>
    <personality>
        <trait name="Courage">0.7</trait>
        <trait name="Wisdom">0.5</trait>
        <!-- Generate at least 5 personality traits -->
    </personality>
    <goals>
        <goal>Character's main goal or motivation</goal>
        <!-- Can have multiple -->
    </goals>
</character>
</output_format>
"""

EVENT_GENERATION_PROMPT = """
<task>Please generate a series of potential events that will trigger during story progression for the novel.</task>
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
Please generate {num_events} potential events, replying in the following XML format:
<events>
    <event>
        <id>event_id</id>
        <name>Event name</name>
        <description>Event description</description>
        <triggers>
            <trigger type="character_relation" value="Friend"/>
            <!-- Other trigger conditions -->
        </triggers>
        <effects>
            <effect target="character_relation" value="0.2"/>
            <!-- Other effects -->
        </effects>
        <narrative_template>The narrative template for this event in the novel, using {character_name} as a placeholder</narrative_template>
    </event>
    <!-- More events -->
</events>
</output_format>
"""

CHAPTER_GENERATION_PROMPT = """
<task>Please generate the content for Chapter {chapter_number} of the novel.</task>
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
Please generate complete chapter content, replying in the following XML format:
<chapter>
    <title>Chapter title</title>
    <content>
        Detailed chapter content, focusing on character interactions, relationship development, and plot progression. Please include at least 2000 words of content.
    </content>
    <summary>
        Brief summary of the chapter for continuity with the next chapter
    </summary>
</chapter>
</output_format>
"""

OUTLINE_GENERATION_PROMPT = """
<task>Please generate a complete story outline for a novel in the {genre} genre.</task>
<novel_info>
    <title>{title}</title>
    <setting>{setting}</setting>
</novel_info>
<characters>
{characters_info}
</characters>
<context>{context}</context>
<output_format>
Please reply in the following XML format:
<outline>
    <overview>Overall story overview and core conflict</overview>
    <arc>
        <name>Beginning</name>
        <description>Detailed description of the story's beginning stage, including world-building, character introductions, and initial conflicts</description>
        <key_events>
            <event>Key event 1</event>
            <event>Key event 2</event>
            <!-- Can have multiple -->
        </key_events>
    </arc>
    <arc>
        <name>Development</name>
        <description>The development stage of the story, conflicts intensify</description>
        <key_events>
            <event>Key event 3</event>
            <event>Key event 4</event>
        </key_events>
    </arc>
    <arc>
        <name>Climax</name>
        <description>The story reaches its climax, main conflicts face resolution</description>
        <key_events>
            <event>Key event 5</event>
            <event>Key event 6</event>
        </key_events>
    </arc>
    <arc>
        <name>Ending</name>
        <description>The story's conclusion and wrap-up</description>
        <key_events>
            <event>Key event 7</event>
            <event>Key event 8</event>
        </key_events>
    </arc>
</outline>
</output_format>
"""

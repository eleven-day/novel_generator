import re
import xml.etree.ElementTree as ET
import openai

def get_outline(topic: str) -> str:
    """获取文章大纲（XML 格式）"""
    outline_prompt = """你是一个专业的文章大纲生成器。请根据以下主题生成一份结构清晰的文章大纲，并以XML格式输出：

<outline>
    <introduction>
        <context>背景介绍内容</context>
        <thesis>论点内容</thesis>
    </introduction>
    <body>
        <point>
            <title>分论点标题</title>
            <evidence>论据/例证内容</evidence>
        </point>
    </body>
    <conclusion>
        <summary>总结内容</summary>
        <remarks>结论/展望内容</remarks>
    </conclusion>
</outline>

主题：{topic}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": outline_prompt.format(topic=topic)}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"获取大纲时出错: {e}")
        return ""

def parse_outline(xml_content: str):
    """
    解析XML格式的大纲为列表，返回一个包含各级标题的列表。
    例如：
    [
        "1. 引言",
        "   1.1 背景介绍: xxx",
        "   1.2 论点: xxx",
        "2. 论述主体",
        "   2.1 分论点标题",
        "      2.1.1 论据: xxx",
        ...
        "3. 结论",
        ...
    ]
    """
    xml_match = re.search(r'<outline>.*</outline>', xml_content, re.DOTALL)
    if not xml_match:
        return []
    
    try:
        root = ET.fromstring(xml_match.group(0))
        result = []
        
        # 解析引言
        intro = root.find('introduction')
        if intro is not None:
            context = intro.find('context')
            thesis = intro.find('thesis')
            if context is not None:
                result.append("1. 引言")
                result.append(f"   1.1 背景介绍: {context.text}")
            if thesis is not None:
                result.append(f"   1.2 论点: {thesis.text}")
        
        # 解析主体
        body = root.find('body')
        if body is not None:
            result.append("2. 论述主体")
            for i, point in enumerate(body.findall('point'), 1):
                title = point.find('title')
                evidence = point.find('evidence')
                if title is not None:
                    result.append(f"   2.{i} {title.text}")
                if evidence is not None:
                    result.append(f"      2.{i}.1 论据: {evidence.text}")
        
        # 解析结论
        conclusion = root.find('conclusion')
        if conclusion is not None:
            result.append("3. 结论")
            summary = conclusion.find('summary')
            remarks = conclusion.find('remarks')
            if summary is not None:
                result.append(f"   3.1 总结: {summary.text}")
            if remarks is not None:
                result.append(f"   3.2 展望: {remarks.text}")
        
        return result
    except ET.ParseError:
        return []
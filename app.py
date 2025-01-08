import openai
import xml.etree.ElementTree as ET
import re
import time
import json
from typing import List, Dict

# 设置OpenAI API密钥
openai.api_key = 'your-api-key'

def get_outline(topic: str) -> str:
    """获取文章大纲"""
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

def parse_outline(xml_content: str) -> List[str]:
    """解析XML格式的大纲为列表"""
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
                result.append(f"1. 引言")
                result.append(f"   1.1 背景介绍: {context.text}")
            if thesis is not None:
                result.append(f"   1.2 论点: {thesis.text}")
        
        # 解析主体
        body = root.find('body')
        if body is not None:
            result.append(f"2. 论述主体")
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
            result.append(f"3. 结论")
            summary = conclusion.find('summary')
            remarks = conclusion.find('remarks')
            if summary is not None:
                result.append(f"   3.1 总结: {summary.text}")
            if remarks is not None:
                result.append(f"   3.2 展望: {remarks.text}")
        
        return result
    except ET.ParseError:
        return []

def generate_paragraph(outline_item: str) -> str:
    """根据大纲项生成对应段落"""
    paragraph_prompt = """请根据以下大纲项生成一段详细的文章内容（200-300字）：

大纲项：{outline_item}

请直接输出段落内容，无需添加其他说明。"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": paragraph_prompt.format(outline_item=outline_item)}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"生成段落时出错: {e}")
        return ""

def save_article(content: str, filename: str):
    """保存文章到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"文章已保存至 {filename}")
    except Exception as e:
        print(f"保存文章时出错: {e}")

def main(topic: str):
    # 1. 获取大纲
    print("正在生成大纲...")
    outline_xml = get_outline(topic)
    
    # 2. 解析大纲
    outline_list = parse_outline(outline_xml)
    if not outline_list:
        print("大纲生成失败")
        return
    
    # 3. 生成各段落内容
    print("正在生成文章内容...")
    content_dict = {}
    for item in outline_list:
        print(f"正在处理: {item}")
        content = generate_paragraph(item)
        content_dict[item] = content
        time.sleep(1)  # 避免API请求过于频繁
    
    # 4. 合并成最终文章
    final_article = ""
    for outline_item in outline_list:
        final_article += f"{outline_item}\n\n"
        final_article += f"{content_dict[outline_item]}\n\n"
    
    # 5. 保存文章
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"article_{timestamp}.txt"
    save_article(final_article, filename)
    
    # 6. 保存大纲和内容的映射关系
    mapping_filename = f"article_mapping_{timestamp}.json"
    try:
        with open(mapping_filename, 'w', encoding='utf-8') as f:
            json.dump(content_dict, f, ensure_ascii=False, indent=2)
        print(f"内容映射已保存至 {mapping_filename}")
    except Exception as e:
        print(f"保存映射关系时出错: {e}")

if __name__ == "__main__":
    topic = input("请输入文章主题：")
    main(topic)
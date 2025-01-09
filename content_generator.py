import openai

def generate_paragraph(outline_item: str) -> str:
    """根据大纲项生成对应段落（200-300字）"""
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
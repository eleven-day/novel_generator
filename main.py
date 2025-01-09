import os
import time
import openai
from dotenv import load_dotenv

from outline_manager import get_outline, parse_outline
from content_generator import generate_paragraph
from file_utils import save_article, save_mapping

def main(topic: str):
    """
    Generates a final article based on the provided topic.
    Steps:
    1) Retrieves an outline for the topic.
    2) Parses the outline into a list of outline items.
    3) Generates paragraph content for each outline item.
    4) Combines the outline items and their generated paragraphs into a final article.
    5) Saves the final article to a text file with a timestamped filename.
    6) Saves a mapping of outline items and corresponding content to a JSON file.
    :param topic: The subject matter for which outline and article will be generated.
    :return: None
    """
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
    save_mapping(content_dict, mapping_filename)

if __name__ == "__main__":
    # 先加载 .env 中的环境变量
    load_dotenv()

    # 在加载后，使用读取到的环境变量来设置 openai.api_key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    topic = input("请输入文章主题：")
    main(topic)
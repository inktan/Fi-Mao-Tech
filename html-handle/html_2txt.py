from bs4 import BeautifulSoup
import re

# 指定HTML文件路径
html_file_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archdaily_cn-20241012\龙南村党群中心___森上建筑___ArchDaily\index.html'

# 读取HTML文件内容
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(html_content, 'html.parser')

# 获取并输出解析后的文档内容
parsed_content = soup.get_text()
# print(parsed_content)
# parsed_content


def remove_extra_blank_paragraphs(text):
    # 使用正则表达式替换多个连续的空白字符为单个换行符
    cleaned_text = re.sub(r'\s+', '\n', text)
    return cleaned_text

# 清除多余的空白段落
cleaned_text = remove_extra_blank_paragraphs(parsed_content)

print(cleaned_text)

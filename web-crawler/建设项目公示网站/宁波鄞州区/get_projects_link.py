import re
import requests
import pandas as pd
import os
from pathlib import Path
from bs4 import BeautifulSoup
import re
import os
from pathlib import Path
import sys

# 获取当前文件的父目录的父目录（即上级目录）
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)  # 将上级目录加入 Python 路径

# 现在可以直接导入上级目录的模块
from file_utils import get_deepest_dirs, create_safe_dirname

root_directory = r"Y:\\GOA-项目公示数据\\建设项目公示信息\\宁波\\鄞州区"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def make_pudong_gov_request(url):
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 获取网页内容
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html_content = response.text.encode('latin-1').decode('utf-8')
    
    # 正则表达式匹配<li>标签并提取href、title和span内容
    pattern = re.compile(
        r'<li>\s*<a href="([^"]*)"[^>]*title="([^"]*)"[^>]*>.*?</a>\s*<span>([^<]*)</span>\s*</li>',
        re.DOTALL
    )

    # 查找所有匹配项
    matches = pattern.findall(html_content)

    # 处理并打印结果
    for i, (pro_url, title, time) in enumerate(matches, 1):
        try:
            pro_url = pro_url
            project_name = title.strip()
            publish_date = time.strip()

            try:
                year = int(publish_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
            except (ValueError, IndexError):
                year = 0  # 日期格式不符合预期

            # 只添加新链接且年份>=2025的数据
            if int(year) < 2025:
                continue
            if any(keyword in project_name for keyword in ['公示已到期','加装电梯','增设电梯','轨道交通']):
                continue

            safe_dirname = create_safe_dirname(project_name, publish_date)
            if safe_dirname in deepest_dir_names:
                # print(f"'{safe_dirname}' 已存在，跳过处理")
                continue
            project_dir = os.path.join(base_output_dir, safe_dirname)
            path = Path(project_dir)
            if path.exists() and path.is_dir():
                # print(f"文件夹 {project_dir} 已存在，跳过处理")
                # return True  # 或者 continue 如果在循环中
                continue
            os.makedirs(project_dir, exist_ok=True)
            
            # 设置输出文件路径
            output_file = os.path.join(project_dir, "项目详情.txt")
            
            domain = "https://www.nbyz.gov.cn/"
            if r'www.nbyz.gov.cn' not in pro_url:
                full_url = domain + pro_url
            else:
                full_url = pro_url
            print(f"项目完整URL: {full_url}")
            
            extract_project_info(full_url,project_dir, output_file)
        except Exception as e:
            print(f"发生错误: {e}")
            return pd.DataFrame()

def extract_project_info(url, project_dir, output_file):
    """提取项目信息并下载图片"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find(class_="main")
    if not content_div:
        content_div = soup.find(class_="content")
        if not content_div:
            print("未找到content_div的标签")
            return False

    # 获取所有文本内容（去除多余空白）
    content = content_div.get_text(separator='\n', strip=True)
    # 保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已保存到 {output_file}")
    # return

    # 初始化计数器
    image_counter = 1
    
    for img in content_div.find_all('img', src=True):
        src = img['src']
        file_url = r'https://www.nbyz.gov.cn/' + src
        try:
            # 获取文件
            response = requests.get(file_url,headers=headers,  stream=True)
            response.raise_for_status()
            
            # 获取文件名和扩展名
            if 'content-disposition' in response.headers:
                # 从响应头获取文件名
                filename = response.headers['content-disposition'].split('filename=')[-1].strip('"\'')
            else:
                # 从 URL 获取文件名
                filename = os.path.basename(file_url.split('?')[0])
            
            # 获取文件扩展名
            _, ext = os.path.splitext(filename.lower())
            ext = ext.lower()
            
            # 根据文件类型确定保存文件名
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
                # 图片文件命名为 公示图01, 公示图02...
                new_filename = f"公示图{image_counter:02d}{ext}"
                image_counter += 1
            
            # 保存文件
            save_path = os.path.join(project_dir, new_filename)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            print(f"已下载: {new_filename}")
            
        except Exception as e:
            print(f"下载 {file_url} 失败: {e}")

# 使用示例
base_output_dir = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\宁波\\鄞州区\\未分类项目"

# 使用示例
# 规划编制批前公示
number_of_pages = 3
for page in range(number_of_pages):
    url = f'https://www.nbyz.gov.cn/col/col1229134491/index.html?uid=7442802&pageNum={page+1}'

    print(url)
    make_pudong_gov_request(url)

# 规划编制批后公示
number_of_pages = 3
for page in range(number_of_pages):
    url = f'https://www.nbyz.gov.cn/col/col1229134492/index.html?uid=7442802&pageNum={page+1}'

    print(url)
    make_pudong_gov_request(url)

# 规划管理审批公示
number_of_pages = 3
for page in range(number_of_pages):
    url = f'https://www.nbyz.gov.cn/col/col1229134493/index.html?uid=7442802&pageNum={page+1}'

    print(url)
    make_pudong_gov_request(url)
import re
import requests
import pandas as pd
import os
from pathlib import Path
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 获取当前文件的父目录的父目录（即上级目录）
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)  # 将上级目录加入 Python 路径

# 现在可以直接导入上级目录的模块
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS,PageCount

root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def extract_project_info(url):
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        for li in soup.find_all('li'):
            # 查找日期span
            date_span = li.find('span', class_='time')
            if not date_span:
                continue
            # 查找链接a标签
            a_tag = li.find('a', target='_blank')
            if not a_tag:
                continue
            # 提取信息
            date = date_span.get_text(strip=True)
            title = a_tag.get('title', '').strip()
            href = a_tag.get('href', '').strip()
            
            clean_date = re.sub(r'\s+', '', date.strip())
            # 提取年份
            try:
                year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
            except (ValueError, IndexError):
                year = 0  # 日期格式不符合预期
            if year < 2025:
                continue
            if any(keyword in title for keyword in PROJECT_KEYWORDS):
                # print(project_name)
                continue

            safe_dirname = create_safe_dirname(title, clean_date)
            if safe_dirname in deepest_dir_names:
            #     print(f"'{safe_dirname}' 已存在，跳过处理")
                continue
            
            project_dir = os.path.join(base_output_dir, safe_dirname)
            path = Path(project_dir)
            if path.exists() and path.is_dir():
            #     print(f"文件夹 {project_dir} 已存在，跳过处理")
                continue
            os.makedirs(project_dir, exist_ok=True)

            # 构建完整项目URL
            full_url = f"https://www.shpt.gov.cn/" + href
            print(f"\n处理项目: {safe_dirname}",f"项目URL: {full_url}")
            try:
                response = requests.get(full_url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find(class_="Article_content")
            if content_div:
                # 获取所有文本内容（去除多余空白）
                content = content_div.get_text(separator='\n', strip=True)
                if content:
                    # 保存到txt文件
                    output_file = os.path.join(project_dir, "项目详情.txt")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"内容已保存到 {output_file}")

                img_tags = content_div.find_all('img')
                if img_tags:
                    for i, img in enumerate(img_tags, 1):
                        src = img.get('src')
                        if not src:
                            continue
                        # 构建完整URL
                        img_url = urljoin(r'https://www.shpt.gov.cn/', src)
                        # 获取图片扩展名
                        img_ext = os.path.splitext(src)[1]
                        if not img_ext:  # 如果没有扩展名，默认使用.jpg
                            img_ext = '.jpg'
                        # 生成图片文件名
                        img_name = f"公示图_{i}{img_ext}"
                        img_path = os.path.join(project_dir, img_name)
                        try:
                            img_data = requests.get(img_url, headers=headers).content
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            print(f"已下载: {img_name} (来自: {img_url})")
                        except Exception as e:
                            print(f"下载图片失败: {src} - {e}")

                for a_tag in content_div.find_all('a'):
                    href = a_tag.get('href')
                    file_name = a_tag.get_text().strip()
                    if not file_name or not href.lower().endswith('.pdf'):
                        continue
                    # 构建完整URL
                    file_url = urljoin(r'https://www.shpt.gov.cn/', href)
                    file_path = os.path.join(project_dir, file_name)
                    try:
                        file_data = requests.get(file_url, headers=headers).content
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        print(f"已下载: {file_name} (来自: {file_url})")
                    except Exception as e:
                        print(f"下载文件失败: {file_url} - {e}")

    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
for page in range(1, PageCount + 1):
    if page > 1:
        # 构造URL
        url = f"https://www.shpt.gov.cn/gtj-zfbm/fangan-gtj/index_{page}.html"
    else:
        # 第一页的URL
        url = r"https://www.shpt.gov.cn/gtj-zfbm/fangan-gtj/index.html"

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\普陀区\未分类项目"
    extract_project_info(url)
    # break

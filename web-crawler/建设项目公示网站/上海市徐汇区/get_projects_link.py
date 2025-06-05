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
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS

root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def extract_project_info(url):
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        # 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        ul = soup.find('ul', class_='list border')
        li_elements = ul.find_all('li') if ul else []

        # 遍历每个 li 元素并提取信息
        for li in li_elements:
            a_tag = li.find('a')
            if a_tag:
                # 提取 href
                href = a_tag.get('href', '')
                # 提取 p 标签的文本
                title = a_tag.find('p').get_text(strip=True) if a_tag.find('p') else ''
                # 提取 b 标签的文本（日期）
                date = a_tag.find('b').get_text(strip=True) if a_tag.find('b') else ''

                clean_date = re.sub(r'\s+', '', date.strip())
                try:
                    year = int(clean_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
                except (ValueError, IndexError):
                    year = 0  # 日期格式不符合预期

                # 只添加新链接且年份>=2025的数据
                if year < 2025:
                    continue
                if any(keyword in title for keyword in PROJECT_KEYWORDS):
                    # print(project_name)
                    continue
                try:
                    safe_dirname = create_safe_dirname(title, clean_date)
                    if safe_dirname in deepest_dir_names:
                    #     # print(f"公示项目文件夹 {safe_dirname} 已存在，跳过处理")
                        continue
                
                    project_dir = os.path.join(base_output_dir, safe_dirname)
                    path = Path(project_dir)
                    if path.exists() and path.is_dir():
                    #     # print(f"公示项目文件夹 {project_dir} 已存在，跳过处理")
                        continue
                    os.makedirs(project_dir, exist_ok=True)

                    # 构建完整URL
                    full_url = f"https://www.xuhui.gov.cn/{href}"
                    print(f"\n处理项目: {safe_dirname}",f"项目URL: {full_url}")

                    try:
                        response = requests.get(full_url, headers=headers, timeout=10)
                        response.encoding = 'utf-8'
                        response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        print(f"请求失败: {e}")
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')
                    content_div = soup.find(class_="article_part")
                    if content_div:
                        # 获取所有文本内容（去除多余空白）
                        content = content_div.get_text(separator='\n', strip=True)
                        # 保存到txt文件
                        output_file = os.path.join(project_dir, "项目详情.txt")
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"文本内容已保存到 {output_file}")

                    img_count = 0
                    img_tags = content_div.find_all('img')
                    if img_tags:
                        print(f"找到 {len(img_tags)} 张图片")
                        
                        for i, img in enumerate(img_tags, 1):
                            # 原始图片 URL
                            src_url = img.get('src')
                            # 1. 发送请求并获取重定向后的 URL
                            response = requests.get(src_url, allow_redirects=True)
                            final_image_url = response.url  # 获取最终重定向的 URL
                            try:
                                # 2. 下载图片
                                image_data = requests.get(final_image_url).content
                                # 保存图片到本地
                                filename = f"公示图_{i:02d}.{ final_image_url.split(".")[-1]}"  # 保留原始文件扩展名

                                save_path = os.path.join(project_dir, filename)
                                with open(save_path, "wb") as f:
                                    f.write(image_data)

                                print(f"已保存: {save_path} (来自: {full_url})")
                                img_count += 1
                            except Exception as e:
                                print(f"下载 {src_url} 失败: {e}")
                        
                        print(f"共下载 {img_count} 张图片")
                    
                    # 查找所有class="xx_attach"的元素
                    attachments = soup.find_all(class_="attachment_part")
                    for i, attachment in enumerate(attachments, 1):
                        # 查找PDF链接
                        # pdf_links = attachment.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                        pdf_links = attachment.find_all('a')
                        for link in pdf_links:
                            pdf_url = link.get('href')
                            pdf_download_name = link.get('download')
                            if not pdf_url:
                                continue
                            # 构建完整URL
                            full_pdf_url = pdf_url
                            save_path = os.path.join(project_dir, pdf_download_name)
                            try:
                                # 下载PDF文件
                                response = requests.get(full_pdf_url, stream=True)
                                response.raise_for_status()
                                with open(save_path, 'wb') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                print(f"已下载: {pdf_download_name} (来自: {full_pdf_url})")
                                
                            except Exception as e:
                                print(f"下载 {pdf_url} 失败: {e}")

                except Exception as e:
                    print(f"发生错误: {e}")
                    continue
                
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
number_of_pages = 5
for page in range(0, number_of_pages):
        # 构造URL
    url = f"https://www.xuhui.gov.cn/xxgk/portal/article/list?menuType=sy&code=jcgk_fzgh_ghhjh&page={page}"
    print(f"正在处理第 {page + 1} 页: {url}")

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\徐汇区\未分类项目"
    extract_project_info(url)
    # break

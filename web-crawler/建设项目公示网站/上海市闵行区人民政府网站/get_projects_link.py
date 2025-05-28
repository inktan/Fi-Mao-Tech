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
from file_utils import get_deepest_dirs, create_safe_dirname

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
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        # 查找所有符合条件的<li>标签
        results = []
        for li in soup.find_all('li'):
            # 查找日期span
            date_span = li.find('span', class_='f_float')
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
            if any(keyword in title for keyword in ['公示已到期','加装电梯','增设电梯','轨道交通']):
                # print(project_name)
                continue
            try:
                safe_dirname = create_safe_dirname(title, clean_date)
                if safe_dirname in deepest_dir_names:
                    # print(f"公示项目文件夹 {safe_dirname} 已存在，跳过处理")
                    continue
            
                project_dir = os.path.join(base_output_dir, safe_dirname)
                path = Path(project_dir)
                if path.exists() and path.is_dir():
                    # print(f"公示项目文件夹 {project_dir} 已存在，跳过处理")
                    continue
                os.makedirs(project_dir, exist_ok=True)

                # 构建完整URL
                full_url = r'https://zwgk.shmh.gov.cn/mh-xxgk-cms/website/mh_xxgk'+href[5:]
                print(f"\n处理项目: {safe_dirname}",f"项目URL: {full_url}")

                try:
                    response = requests.get(full_url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"请求失败: {e}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find(class_="xx_text1")
                if not content_div:
                    print("未找到class_=xx_text1的标签")

                # 获取所有文本内容（去除多余空白）
                content = content_div.get_text(separator='\n', strip=True)
                # 保存到txt文件
                output_file = os.path.join(project_dir, "项目详情.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"内容已保存到 {output_file}")

                # 查找所有class="xx_attach"的元素
                attachments = soup.find_all(class_="xx_attach")
                for i, attachment in enumerate(attachments, 1):
                    # 查找PDF链接
                    pdf_links = attachment.find_all('a', href=lambda x: x and x.lower().endswith('.pdf'))
                    for link in pdf_links:
                        pdf_url = link.get('href')
                        pdf_download_name = link.get('download')
                        if not pdf_url:
                            continue
                        # 构建完整URL
                        full_pdf_url = urljoin(r'https://zwgk.shmh.gov.cn/', pdf_url)
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
        return pd.DataFrame()

# 使用示例
for page in [0,140,139,138,137,136,135,134,133,132,131]:
    url = f"https://zwgk.shmh.gov.cn/mh-xxgk-cms/website/mh_xxgk/xxgk_ghj_ywxx_ghglgs/List/list_{page}.htm"
    print(url)

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\闵行区\未分类项目"
    extract_project_info(url)
    # break

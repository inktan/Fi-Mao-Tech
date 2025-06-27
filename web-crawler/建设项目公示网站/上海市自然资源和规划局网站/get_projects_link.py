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
        # 获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # 定义正则表达式模式（匹配h4和紧邻的div）
        pattern = r'''
            <h4>\s*<a\s+title="([^"]+)"\s+href="([^"]+)"[^>]*>.*?</a>\s*</h4>  # h4部分
            \s*<div\s+class="small\s+text-muted\s+mb-5">\s*<i[^>]*></i>\s*([^<]+)\s*</div>  # div部分
        '''
        # 查找所有匹配项
        matches = re.findall(pattern, html_content, re.VERBOSE)
        # 筛选新数据
        for title, href, date in matches:
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
                    # print(f"公示项目文件夹 {safe_dirname} 已存在，跳过处理")
                    continue
            
                project_dir = os.path.join(base_output_dir, safe_dirname)
                path = Path(project_dir)
                if path.exists() and path.is_dir():
                    # print(f"公示项目文件夹 {project_dir} 已存在，跳过处理")
                    continue
                os.makedirs(project_dir, exist_ok=True)

                # 构建完整URL
                full_url = f"https://ghzyj.sh.gov.cn/{href}"
                print(f"\n处理项目: {safe_dirname}",f"项目URL: {full_url}")

                try:
                    response = requests.get(full_url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"请求失败: {e}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find(id="ivs_content")
                if content_div:
                    # 获取所有文本内容（去除多余空白）
                    content = content_div.get_text(separator='\n', strip=True)
                    # 保存到txt文件
                    output_file = os.path.join(project_dir, "项目详情.txt")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"文本内容已保存到 {output_file}")

                img_count = 0
                img_tags = soup.find_all('img')
                if img_tags:
                    print(f"找到 {len(img_tags)} 张图片")
                    
                    for i, img in enumerate(img_tags, 1):
                        src = img.get('src')
                        if not src:
                            continue
                        # 构建完整URL
                        full_url = urljoin('https://ghzyj.sh.gov.cn/', src)
                        
                        # 生成文件名
                        filename = f"公示图_{i:02d}{Path(src).suffix}"  # 保留原始文件扩展名
                        save_path = os.path.join(project_dir, filename)
                        
                        try:
                            # 下载图片
                            img_data = requests.get(full_url, headers=headers).content
                            with open(save_path, 'wb') as f:
                                f.write(img_data)
                            print(f"已保存: {filename} (来自: {full_url})")
                            img_count += 1
                        except Exception as e:
                            print(f"下载 {src} 失败: {e}")
                    
                    print(f"共下载 {img_count} 张图片")

            except Exception as e:
                print(f"发生错误: {e}")
                continue
                
    except Exception as e:
        print(f"发生错误: {e}")

# 使用示例
for page in range(1, PageCount + 1):
    if page > 1:
        # 构造URL
        url = f"https://ghzyj.sh.gov.cn/gszqyj/index_{page}.html"
    else:
        # 第一页的URL
        url = r"https://ghzyj.sh.gov.cn/gszqyj/index.html"

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\上海市\未分类项目"
    extract_project_info(url)
    # break





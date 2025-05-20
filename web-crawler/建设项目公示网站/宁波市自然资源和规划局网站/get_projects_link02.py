import re
import requests
import pandas as pd
import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长

def make_pudong_gov_request(url):
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 获取网页内容
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    html_content = response.text.encode('latin-1').decode('utf-8')
    
    # 正则表达式匹配所有<li>标签
    li_pattern = re.compile(
        r'<li>\s*<a href="([^"]*)"[^>]*>\s*<span class="title">([^<]*)</span>\s*<span class="time">([^<]*)</span>\s*</a>\s*</li>',
        re.DOTALL
    )

    # 查找所有匹配的<li>标签
    matches = li_pattern.findall(html_content)

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

            if int(year) < 2025:
                date_stop = True
                break

            # 只添加新链接且年份>=2025的数据
            if year >= 2025:
                safe_dirname = create_safe_dirname(project_name, publish_date)
                project_dir = os.path.join(base_output_dir, safe_dirname)
                path = Path(project_dir)
                if path.exists() and path.is_dir():
                    print(f"文件夹 {project_dir} 已存在，跳过处理")
                    # return True  # 或者 continue 如果在循环中
                    continue
                os.makedirs(project_dir, exist_ok=True)

                # print(pro_url)
                # print(project_name)
                # print(publish_date)
                
                # 设置输出文件路径
                output_file = os.path.join(project_dir, "项目详情.txt")
                
                domain = "http://zgj.ningbo.gov.cn"
                full_url = domain + pro_url
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
    
    # 提取基本信息
    # 查找id="ivs_content"的标签
    content_div = soup.find(id="main")
    # content_div = soup.find(class_="TRS_Editor")
    if not content_div:
        print("未找到class='main'的标签")
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
        file_url = r'https://zgj.ningbo.gov.cn/' + src
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
base_output_dir = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\宁波\\宁波市\\未分类项目"

# 使用示例
# 宁波市公示公告> 规划> 规划批前公示只有十天公示期
number_of_pages = 3
for page in range(number_of_pages):
    url = f'https://zgj.ningbo.gov.cn//col//col1229101542//index.html?uid=5624005&pageNum={page+1}'

    print(url)
    make_pudong_gov_request(url)

    # break

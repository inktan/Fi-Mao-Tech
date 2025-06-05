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
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS

root_directory = r"Y:\\GOA-项目公示数据\\建设项目公示信息\\无锡\无锡市"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长
def make_pudong_gov_request():
    url = "https://zrzy.wuxi.gov.cn/intertidwebapp/docquery/queryZrzyDocments"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }

    data = {
        "currentPage": "1",
        "chanId": "49953,49954,49955,49956",
        # "title": "",
    }
        
    try:
        response = requests.post(
            url,
            headers=headers,
            # cookies=cookies,
            data=data,
        )
        
        response.raise_for_status()  # 检查请求是否成功
        # 打印响应信息
        data = response.json()
        
        projects = data["list"]
        for project in projects:
            time_str = project['writeTime']
            match = re.match(r"(\d{4}-\d{2}-\d{2})", time_str)
            if match:
                publish_date = match.group(1)
                year = re.match(r"(\d{4})", time_str).group(1)
                # 只添加新链接且年份>=2025的数据
                if int(year) < 2025:
                    continue
            
                project_name = project['title']
                if any(keyword in project_name for keyword in PROJECT_KEYWORDS):
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
                img_dir = project_dir
                os.makedirs(img_dir, exist_ok=True)
                
                full_url = r'https://zrzy.wuxi.gov.cn' + project['url']
                extract_project_info(full_url,project_dir, output_file)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

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
    content_div = soup.find(id="Zoom")
    # content_div = soup.find(class_="xx_text1")
    if not content_div:
        print("未找到id='Zoom'的标签")
        return False

    # 获取所有文本内容（去除多余空白）
    content = content_div.get_text(separator='\n', strip=True)
    # 保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已保存到 {output_file}")

    # 初始化计数器
    image_counter = 1
    pdf_counter = 1
    doc_counter = 1
    
    # 初始化计数器
    image_counter = 1
    
    for img in content_div.find_all('img', src=True):
        src = img['src']
        file_url = r'https://zrzy.wuxi.gov.cn' + src
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
    # 查找所有 a 标签
    links = content_div.find_all('a', href=True)

    for link in links:
        file_url = r'https://zrzy.wuxi.gov.cn' + link['href']
        
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
            elif ext == '.pdf':
                # PDF 文件保持原名
                new_filename = link['title']
                pdf_counter += 1
            elif ext in ('.doc', '.docx'):
                # Word 文件保持原名
                new_filename = link['title']
                doc_counter += 1
            else:
                # 其他类型文件保持原名
                new_filename = link['title']
            
            # 保存文件
            save_path = os.path.join(project_dir, new_filename)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            print(f"已下载: {new_filename}")
            
        except Exception as e:
            print(f"下载 {file_url} 失败: {e}")


# 使用示例
if __name__ == "__main__":
    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\无锡\无锡市\未分类项目"
    make_pudong_gov_request()
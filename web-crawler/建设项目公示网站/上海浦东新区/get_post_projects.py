import requests
import json
from datetime import datetime
import os
import os
from pathlib import Path
import sys
from bs4 import BeautifulSoup

# 获取当前文件的父目录的父目录（即上级目录）
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)  # 将上级目录加入 Python 路径

# 现在可以直接导入上级目录的模块
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS,PageCount

root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def make_pudong_gov_request():
    url = "https://www.pudong.gov.cn/zwgk-search-front/api/data/search"
    
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    data = {
            "channelList": ["15856"],
            "pageNo": 1,
            "pageSize": 20
            }
        
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),  # 注意这里使用json.dumps
            timeout=10
        )
        
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()['data']
        projects = data["list"]
        for project in projects:
            timestamp = project['display_date'] 
            dt = datetime.fromtimestamp(timestamp / 1000)
            formatted_date = dt.strftime("%Y年%m月%d日")
            year = dt.year
            if year < 2025:
                continue

            project_name = project['title']
            if any(keyword in project_name for keyword in PROJECT_KEYWORDS):
                # print(project_name)
                continue

            publish_date = formatted_date
            safe_dirname = create_safe_dirname(project_name, publish_date)
            if safe_dirname in deepest_dir_names:
                # print(f"'{safe_dirname}' 已存在，跳过处理")
                continue

            project_dir = os.path.join(base_output_dir, safe_dirname)
            
            path = Path(project_dir)
            if path.exists() and path.is_dir():
                print(f"文件夹 {project_dir} 已存在，跳过处理")
                # return True  # 或者 continue 如果在循环中
                continue

            os.makedirs(project_dir, exist_ok=True)
            
            # 设置输出文件路径
            output_file = os.path.join(project_dir, "项目详情.txt")
            full_url = project['url']
            extract_project_info(full_url, output_file)

            if 'attaches' in project and project['attaches']:
                for attach in project['attaches']:
                    pdf_url = attach['url']
                    file_name = attach['name']
                    save_path = os.path.join(project_dir, file_name)
                    
                    try:
                        # 下载PDF文件
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }

                        response = requests.get(pdf_url, headers=headers, stream=True)
                        response.raise_for_status()
                        
                        with open(save_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        print(f"已下载: {file_name} (来自: {pdf_url})")
                    except Exception as e:
                        print(f"下载 {pdf_url} 失败: {e}")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def extract_project_info(url, output_file):
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
    content_div = soup.find(id="ivs_content")
    # content_div = soup.find(class_="xx_text1")
    if not content_div:
        print("未找到id='ivs_content'的标签")
        return False

    # 获取所有文本内容（去除多余空白）
    content = content_div.get_text(separator='\n', strip=True)
    # 保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"内容已保存到 {output_file}")
# 使用示例
if __name__ == "__main__":
    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\浦东新区\未分类项目"
    make_pudong_gov_request()
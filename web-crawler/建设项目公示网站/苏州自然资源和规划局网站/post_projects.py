import requests
import json
from datetime import datetime
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from pathlib import Path

def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长
def make_pudong_gov_request():
    url = "https://zrzy.jiangsu.gov.cn/szghgs/web/allGs.do"

    headers = {
        # "Host": "zrzy.wuxi.gov.cn",
        # "Origin": "https://zrzy.wuxi.gov.cn",
        # "Referer": "https://zrzy.wuxi.gov.cn/gggs/ghgs/cxghssglgs/pqgs/csghssglgs/index.shtml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        # "X-Requested-With": "XMLHttpRequest",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        # "Accept": "application/json, text/javascript, */*; q=0.01",
        # "Accept-Encoding": "gzip, deflate, br, zstd",
        # "Accept-Language": "zh-CN,zh;q=0.9",
        # "Cache-Control": "no-cache",
        # "Connection": "keep-alive",
        # "Pragma": "no-cache",
        # "Sec-Fetch-Dest": "empty",
        # "Sec-Fetch-Mode": "cors",
        # "Sec-Fetch-Site": "same-origin",
        # "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        # "Sec-Ch-Ua-Mobile": "?0",
        # "Sec-Ch-Ua-Platform": '"Windows"',
    }

    # cookies = {
    #     "intertid": "2022",
    #     "Hm_lvt_f4b0176a110c52155a84a7737769021c": "1747297998,1747451887",
    #     "HMACCOUNT": "B0C04E107F5FB2FD",
    #     "Hm_lpvt_f4b0176a110c52155a84a7737769021c": "1747490632",
    # }
    date_stop = False
    for i in range(100):
        if date_stop:
            break
        data = {
            "currentPage": i + 1,
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
            # print(data["pageNo"])
            # print(data["pageSize"])
            # print(data["totalPage"])
            # print(data["totalCount"])
            # print(response.json())
            # return
            
            projects = data["data"]["rows"]
            for project in projects:
                publish_date = project['publicityStartTime']
                # print(time_str)
                # date_stop = True
                # continue

                year = re.match(r"(\d{4})", publish_date).group(1)
                if int(year) < 2025:
                    date_stop = True
                    break

                if int(year) >= 2025:
                    project_name = project['name']
                    # print(project['id'])
                    # continue

                    safe_dirname = create_safe_dirname(project_name, publish_date)
                    project_dir = os.path.join(base_output_dir, safe_dirname)
                    
                    path = Path(project_dir)
                    if path.exists() and path.is_dir():
                        print(f"文件夹 {project_dir} 已存在，跳过处理")
                        # return True  # 或者 continue 如果在循环中
                        continue

                    os.makedirs(project_dir, exist_ok=True)
                    
                    # 设置输出文件路径
                    output_file = os.path.join(project_dir, "项目详情.txt")
                    img_dir = project_dir
                    os.makedirs(img_dir, exist_ok=True)
                    
                    full_url = r'https://zrzy.jiangsu.gov.cn/szghgs/web/detail.do?ID=' + project['id']
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
    # content_div = soup.find(id="Zoom")
    content_div = soup.find(class_="mb")
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
    
    # 查找所有 a 标签
    links = content_div.find_all('img', src=True)
    # print(links)

    for link in links:
        file_url = r'https://zrzy.jiangsu.gov.cn' + link['src']
        
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
if __name__ == "__main__":
    
    # csv_path = r'E:\建设项目公示信息\上海\闵行区\建设项目公示信息表_2025.csv'

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\苏州\苏州市\未分类项目"
    result = make_pudong_gov_request()
    # if result:
    #     print("\n响应数据:")
    #     print(json.dumps(result, indent=2, ensure_ascii=False))
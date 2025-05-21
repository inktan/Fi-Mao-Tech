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

def get_deepest_dirs(root_dir):
    """获取所有嵌套最底层的文件夹路径（没有子文件夹的文件夹）"""
    deepest_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # 如果没有子文件夹，说明是底层文件夹
            dir_name = os.path.basename(dirpath)  # 获取文件夹名（不含路径）
            deepest_dirs.add(dir_name)

    return deepest_dirs
root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\浦东新区"  # 替换为你的目标文件夹路径
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
    url = "https://www.pudong.gov.cn/zwgk-search-front/api/data/search"
    
    # 请求头
    headers = {
        # 'Accept': 'application/json, text/plain, */*',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': '0zaLpREBxJs7S=60RuMQTuA7U027wpuPHBp7UqLpmsS9AqigHz0p1MUAhnnjGAbsfunZvnauW5hNLQY_8CJ5uENpZkCF79Q.zHbGCA; 0zaLpREBxJs7O=60b0rrMxi1A6G6t1Vn60pt7v04YWVUNKr3SJ653o3J42vPz2UGW1b6kB4dooagkPKD3kohXEgyEQgTZqJEP35RLq; zh_choose=s; 0zaLpREBxJs7T=0kp6dSy6rHyFP1.eFMRJLmpouZhkkr0mafxZzHMpd4KVdhEW3bSn9YVZzxJ0e4U5sgzMvrtw.x75FwR2Fx_rSypvVvl5yVNJXGzUBfSyTUxeer9iPcv2ghbxQd7zP9LS00T.uC2BeSPrb9IybsyG7XYeDv.4hNN7VUDYTmQFiJj83RqUCtp7U2eSGcRY0mY3S7gIMwuqTs0cAmCjGFQL7t99MAdOaaAUmiEHj6HN8sr7; 0zaLpREBxJs7P=0_gyr0k__BSphroQZgd2yt5yf7Z5hVL5NxrbrWyhHwgItkFUTwMSf8rozFhxkMcNwilHa_tyKZjFS_1ncix_QvbiM84D8heMQ8hVYkbhDiOIfZ3xPgXECmf.uzC0UMJiAZeN5OHpOPwEbxmfQzHSNpu0eFlrhRzlQdAYShryQqNZLqVV7oaIDN831VjG_gN6.Na7jBq_omVTdFYDvIW_G861RKkS9bGr4tknXqIc4vTinAhZ.sc6p8ZWY78Kr3U0QEysYtMa_7rfuB5Oj3Ta0I8dVciHzrcHy4.A3fISbGxu0snV5EmmG_mz5vqblN3iFh0CFrayg8TKIWNfV9LDGuCALBbLf0F5oR1u.qpEqerl; _pk_testcookie.300.0950=1; _pk_ses.300.0950=1; _pk_id.300.0950=b361e4b5bce0f18e.1747292395.3.1747391951.1747391888.',
        # 'Host': 'www.pudong.gov.cn',
        # 'Origin': 'https://www.pudong.gov.cn',
        # 'Pragma': 'no-cache',
        # 'Referer': 'https://www.pudong.gov.cn/zwgk/14523.gkml_ywl_gsxx/index.html',
        # 'Sec-Ch-Ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        # 'Sec-Ch-Ua-Mobile': '?0',
        # 'Sec-Ch-Ua-Platform': '"Windows"',
        # 'Sec-Fetch-Dest': 'empty',
        # 'Sec-Fetch-Mode': 'cors',
        # 'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    # 请求体 - 需要根据实际API调整
    data = {
            "channelList": ["15856"],
            "pageNo": 1,
            "pageSize": 300
            }
        
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),  # 注意这里使用json.dumps
            timeout=10
        )
        
        response.raise_for_status()  # 检查请求是否成功
        # 打印响应信息
        data = response.json()['data']
        print(data["pageNo"])
        print(data["pageSize"])
        print(data["totalPage"])
        print(data["totalCount"])
        # print(data["list"][0])

        projects = data["list"]
        for project in projects:
            # print(project['title'])
            # print(project['display_date'])
            timestamp = project['display_date'] 
            dt = datetime.fromtimestamp(timestamp / 1000)
            formatted_date = dt.strftime("%Y年%m月%d日")
                        
            # 或者分开获取年、月、日
            year = dt.year
            # month = dt.month
            # day = dt.day
            
            if year >= 2025:
                # print(formatted_date)
                # print(project)

                publish_date = formatted_date
                project_name = project['title']

                safe_dirname = create_safe_dirname(project_name, publish_date)
                
                if safe_dirname in deepest_dir_names:
                    print(f"'{safe_dirname}' 已存在，跳过处理")
                    continue
                    # return False

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
    
    # csv_path = r'E:\建设项目公示信息\上海\闵行区\建设项目公示信息表_2025.csv'

    base_output_dir = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\浦东新区\未分类项目"
    result = make_pudong_gov_request()
    # if result:
    #     print("\n响应数据:")
    #     print(json.dumps(result, indent=2, ensure_ascii=False))
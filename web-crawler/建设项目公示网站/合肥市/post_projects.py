import re
import requests
import pandas as pd
import os
from pathlib import Path
from bs4 import BeautifulSoup
import re
import requests
import json

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
    data = response.json()
    projects = data['data']['list']

    for project in projects:
        try:
            guid = project['guid']
            project_name = project['content'].strip()
            publish_date = project['starttime'].strip()[:10]

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

                # 下载项目公示的文字相关信息
                proUrl = f'https://zwfw.hfzrzy.com/rest/publicity/v1/notice/content/get?guid={guid}'

                response = requests.get(proUrl, headers=headers)
                response.raise_for_status()
                data = response.json()

                output_file = os.path.join(project_dir, "项目详情.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data['data'], ensure_ascii=False))
                print(f"内容已保存到 {output_file}")

                # 下载项目公示的图片相关信息
                proUrl = f'https://zwfw.hfzrzy.com//rest//publicity//v1//notice//thumbnail//get?guid={guid}'

                response = requests.get(proUrl, headers=headers)
                response.raise_for_status()
                data = response.json()
                attachments = data['data']
                for attachment in attachments:
                    new_filename = attachment['filename']
                    file_url = r'https://zwfw.hfzrzy.com/rest/publicity/v1/thumbnail/material/download?guid=' + attachment['guid']
                    try:
                        # 获取文件
                        response = requests.get(file_url,headers=headers,  stream=True)
                        response.raise_for_status()
                        # 保存文件
                        save_path = os.path.join(project_dir, new_filename)
                        with open(save_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                                    
                        print(f"已下载: {new_filename}")
                        
                    except Exception as e:
                        print(f"下载 {file_url} 失败: {e}")


        except Exception as e:
            print(f"发生错误: {e}")
            return pd.DataFrame()

# 使用示例
base_output_dir = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\合肥\\合肥市\\未分类项目"

# 使用示例
# 规划编制批前公示
number_of_pages = 10
for page in range(number_of_pages):
    url = f'https://zwfw.hfzrzy.com//rest//publicity//v1//notice//business//get?type=建设工程设计方案&ky=&pn={page+1}&ps=30'
    # url = f'https://zwfw.hfzrzy.com//rest//publicity//v1//notice//business//get?type=建设工程设计方案&ky=&pn={page+1}&ps=1'

    print(url)
    make_pudong_gov_request(url)

    # break

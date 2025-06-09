# -*- coding: utf-8 -*-
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json
import pandas as pd

from datetime import datetime
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def download_image(url, file_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            # print("图片下载成功：", file_path)
            return
        else:
            return
    except Exception as e:
        return
    
def extract_project_imgs_from_html(html):
    '''获取项目页面中包含的图片链接'''
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img', class_='img-responsive')
    data_urls = [img['lsrc'] for img in img_tags if 'lsrc' in img.attrs]
    return data_urls

def get_pro_lits_info(project_link):
    response = requests.get(project_link)
    if response.status_code == 200:
        json_dict = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').get_text()
        json_dict['title'] = title

        illegal_chars = [" ", "/", "\\", "|", '"', ':', '*', '?', '<', '>', '|']
        for char in illegal_chars:
            title = title.replace(char, "_")

        folder_path = folder_path_template + f'\{title[0:218]}' 
        folder_path = folder_path[0:210] 

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            return

        index_path = folder_path+'\index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        project_imgs_href_links = extract_project_imgs_from_html(response.text)
        for index, img_url in enumerate(project_imgs_href_links):
            # print(img_url)

            file_path = folder_path+ '\\' +f'img_{index}.png'
            file_exists = os.path.exists(file_path)
            if not file_exists and img_url.startswith('http'):
                download_image(img_url, file_path)

        # print(project_imgs_href_links)

if __name__ == '__main__':
    # 请求头（从原始请求中提取关键字段）
    headers = {
        # "Authority": "dashboard.gooood.cn",
        # "Accept": "application/json",
        # "Accept-Encoding": "gzip, deflate, br",
        # "Accept-Language": "zh-CN,zh;q=0.9",
        # "Cache-Control": "no-cache",
        # "Origin": "https://www.gooood.cn",
        # "Referer": "https://www.gooood.cn/",
        # "Sec-Ch-Ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        # "Sec-Ch-Ua-Mobile": "?0",
        # "Sec-Ch-Ua-Platform": '"Windows"',
        # "Sec-Fetch-Dest": "empty",
        # "Sec-Fetch-Mode": "cors",
        # "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        # 注意：实际使用时可能需要添加Cookie（见下方说明）
    }
    page_index = 1
    # 目标URL
    url = "https://dashboard.gooood.cn/api/wp/v2/posts"

    folder_path_template = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\gooood-20250605'

    while True:
        # 请求参数
        params = {
            "categories": 1,
            "page": page_index,
            "per_page": 10
        }
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            # 检查响应状态
            if response.status_code == 200:
                data = response.json()
                page_index += 1
                if page_index > 150:
                    break
                print(url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                for pro_info in data:
                    while True:
                        try:
                            print('publication_date', pro_info['date'])
                            project_link = f'https://www.gooood.cn/{pro_info['slug']}.htm'
                            print(project_link)
                            get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                            time.sleep(2)
                            break # 请求成功，则打破死循环

                        except Exception as e:
                            print(f"发生错误：{e}")
                            print("Connection error. Trying again in 2 seconds.")
                            time.sleep(20)

        except Exception as e:
            print(f"发生错误：{e}")
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(20)




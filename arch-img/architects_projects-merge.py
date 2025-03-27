# -*- coding: utf-8 -*-
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json
import pandas as pd
from tqdm import tqdm

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
    response = requests.get(project_link, headers=headers)
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
    # 设置用户代理
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    folder_path_template = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\architects-20241012'
    
    df = pd.read_csv(r'd:\Ai-clip-seacher\AiArchLib\architects-1-277-2024-10-12.csv')

    for index, project_link in tqdm(df['link-href'].items()):
        if index<0:
            continue

        while True:
            try:
                project_count = index
                print(f"Index: {index}, Href: {project_link}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                time.sleep(2)
                break # 请求成功，则打破死循环

            except Exception as e:
                print(f"发生错误：{e}")
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(20)




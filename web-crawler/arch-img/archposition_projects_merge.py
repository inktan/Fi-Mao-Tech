# -*- coding: utf-8 -*-
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json
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
def extract_project_href_from_thumb_blocks(html):
    '''获取页面中包含的项目链接'''
    soup = BeautifulSoup(html, 'html.parser')
    # 查找所有class="index-feed-item"的a标签
    a_tags = soup.find_all('a', class_='index-feed-item')
    src_list = []
    data_id_list = []
    
    for tag in a_tags:
        href = tag.get('href')
        data_id = tag.get('data-id')
        if 'items' in href:
            src_list.append(r'https://www.archiposition.com'+href)
            data_id_list.append(data_id)
    
    return src_list ,data_id_list

def extract_project_imgs_from_html(html):
    '''获取项目页面中包含的图片链接'''
    soup = BeautifulSoup(html, 'html.parser')
    imgs = soup.find_all('img', class_='size-full')

    data_urls = [img.get('src') for img in imgs]
    
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

        folder_path = folder_path_template + f'\{title}'

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

if __name__ == '__main__':
    # 设置用户代理
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    folder_path_template = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archiposition-20241012'

    url = r'https://www.archiposition.com/wp-admin/admin-ajax.php?action=load_category&ajax=1&limit=2000'
    project_count = 0

    print(url,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        response = requests.get(url, headers=headers)
        time.sleep(3)
        if response.status_code == 200:
            project_links ,data_id_list = extract_project_href_from_thumb_blocks(response.text)#请求出错，则陷入无限请求中
                            
            for idx, project_link in enumerate(tqdm(project_links)):
                while True:
                    try:
                        project_count = data_id_list[idx]
                        get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                        time.sleep(3)
                        break # 请求成功，则打破死循环

                    except Exception as e:
                        print(f"发生错误：{e}")
                        print("Connection error. Trying again in 2 seconds.")
                        time.sleep(2)
                        
    except Exception as e:
        print(f"发生错误：{e}")
        print("Connection error. Trying again in 2 seconds.")
        time.sleep(3)
        




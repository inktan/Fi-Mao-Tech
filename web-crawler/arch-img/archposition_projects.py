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

        folder_path = folder_path_template + f'\project_{project_count}' 
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        index_path = folder_path+'\index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        project_imgs_href_links = extract_project_imgs_from_html(response.text)
        # project_imgs_href_links = [i.split('?')[0] for i in project_imgs_href_links]
        json_dict['project_imgs_links'] = project_imgs_href_links

        json_file_path =  folder_path+"\project_imgs_links.json"
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(json_dict, file, ensure_ascii=False, indent=4)

        # print(project_imgs_href_links)

if __name__ == '__main__':
    # 设置用户代理
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    folder_path_template = r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\archiposition\Date20240826'
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
        




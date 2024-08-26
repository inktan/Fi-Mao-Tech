# -*- coding: utf-8 -*-
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json

from datetime import datetime
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def extract_project_href_from_thumb_blocks(html):
    '''获取页面中包含的项目链接'''
    soup = BeautifulSoup(html, 'html.parser')
    thumb_blocks = soup.find_all('div', class_='thumb-block')
    href_links = []
    
    for block in thumb_blocks:
        a_href = block.find('a')
        # img_holder = block.find('div', class_='img-holder')
        if a_href and 'href' in a_href.attrs:
            href_links.append(a_href['href'])
    
    return href_links


def extract_project_imgs_from_html(html):
    '''获取项目页面中包含的图片链接'''
    soup = BeautifulSoup(html, 'html.parser')
    thumb_blocks = soup.find_all('div', class_='thumb-block')
    data_urls = []
    
    for block in thumb_blocks:
        img_holder = block.find('div')
        if img_holder:
            img = img_holder.find('div', class_='img')
            if img and 'data-url' in img.attrs:
                data_urls.append(img['data-url'])
    
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
        project_imgs_href_links = [i.split('?')[0] for i in project_imgs_href_links]
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

    folder_path_template = r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\architizer'
    page_index = 2936
    project_count = 35203
    while True:
        if page_index==1:
            url ='https://architizer.com/projects/q/'
        elif page_index>1:
            url = f'https://architizer.com/projects/q/page:{page_index}/'
        page_index+=1

        if page_index>12691:
            break

        print(url,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        while True:
            try:
                response = requests.get(url, headers=headers)
                time.sleep(3)
                if response.status_code == 200:
                    project_links = extract_project_href_from_thumb_blocks(response.text)#请求出错，则陷入无限请求中
                    project_links = ['https://architizer.com' +i for i in project_links]
                    # print(project_links)
                                    
                    for project_link in project_links:
                        while True:
                            try:
                                get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                                time.sleep(3)
                                project_count+=1
                                break # 请求成功，则打破死循环

                            except Exception as e:
                                print(f"发生错误：{e}")
                                print("Connection error. Trying again in 2 seconds.")
                                time.sleep(2)
                                
                    break # 请求成功，则打破死循环
            except Exception as e:
                print(f"发生错误：{e}")
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(3)
        




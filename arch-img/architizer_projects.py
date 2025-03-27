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
        project_imgs_href_links = [i.split('?')[0] for i in project_imgs_href_links]
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

    folder_path_template = r'D:\Ai-clip-seacher\AiArchLib\architizer-20241012'
    page_index = 0
    while True:
        page_index+=1
        if page_index<2:
            url ='https://architizer.com/projects/q/'
        else:
            url = f'https://architizer.com/projects/q/page:{page_index}/'

        print(url,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        while True:
            try:
                response = requests.get(url, headers=headers)
                time.sleep(3)
                if response.status_code == 200:
                    project_links = extract_project_href_from_thumb_blocks(response.text)#请求出错，则陷入无限请求中
                    project_links = ['https://architizer.com' +i for i in project_links]
                    # print(project_links)
                    if len(project_links) == 0:
                        continue

                    for project_link in project_links:
                        while True:
                            try:
                                print(project_link)
                                get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                                time.sleep(3)
                                break # 请求成功，则打破死循环

                            except Exception as e:
                                print(f"发生错误：{e}")
                                print("Connection error. Trying again in 2 seconds.")
                                time.sleep(20)
                                
                    break # 请求成功，则打破死循环
            except Exception as e:
                print(f"发生错误：{e}")
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(20)
        




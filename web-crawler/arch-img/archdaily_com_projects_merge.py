# -*- coding: utf-8 -*-
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
    a_hrefs = soup.find_all('a', class_='gridview__content')
    href_links = []
    
    for a_href in a_hrefs:
        if 'href' in a_href.attrs:
            href_links.append(a_href['href'])
    
    return href_links

def extract_project_imgs_from_html(html):
    '''获取项目页面中包含的图片链接'''
    soup = BeautifulSoup(html, 'html.parser')
    img_elements = soup.find_all('img', {'class': 'gallery-thumbs-img'})
    img_src_list = [img['src'] for img in img_elements]
    
    # 图片的三种显示模式，thumb_jpg medium_jpg large_jpg
    # https://images.adsttc.com/media/images/63c9/2073/7643/4a6c/a846/596b/thumb_jpg/kobe-port-museum-taisei-design-planners-architects-and-engineers_6.jpg
    # https://images.adsttc.com/media/images/63c9/2073/7643/4a6c/a846/596b/medium_jpg/kobe-port-museum-taisei-design-planners-architects-and-engineers_6.jpg
    # https://images.adsttc.com/media/images/63c9/2073/7643/4a6c/a846/596b/large_jpg/kobe-port-museum-taisei-design-planners-architects-and-engineers_6.jpg

    img_src_list = [link.replace("medium_jpg", "large_jpg") if "medium_jpg" in link else link for link in img_src_list]
    img_src_list = [link.split('?')[0]  if "?" in link else link for link in img_src_list]

    return img_src_list

def export_pro_lits_info(project_link):
    '''保存每个项目含有的图片链接'''
    response = requests.get(project_link)
    if response.status_code == 200:
        json_dict = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').get_text()
        json_dict['title'] = title

        div_element = soup.find('div', {'id': 'nrd-articles-container'})
        project_index = div_element['data-token'] if div_element else None

        illegal_chars = [" ", "/", "\\", "|", '"', "'"]
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

    folder_path_template = r'D:\Ai-clip-seacher\AiArchLib\archdaily-20241012'
    page_index = 0

    options = webdriver.ChromeOptions()  # 配置 chrome 启动属性
    options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    browser = webdriver.Chrome(options=options)

    while True:
        if page_index>389:
            break
        if page_index>389:
            break

        url = 'https://www.archdaily.com/search/projects'
        if page_index>1:
            url = f'https://www.archdaily.com/search/projects?page={page_index}'
        page_index+=1

        print(url)

        while True:
            try:
                browser.get(url)
                wait = WebDriverWait(browser,3)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                html = browser.page_source

                # index_path = 'index.html'
                # with open(index_path, 'w', encoding='utf-8') as f:
                #     f.write(html)

                project_links = extract_project_href_from_thumb_blocks(html)
                # print(project_links)
                if len(project_links) == 0: # 请求出错，则陷入无限请求中
                    continue

                for project_link in project_links:
                    while True:
                        try:
                            export_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
                            break # 请求成功，则打破死循环

                        except Exception as e:
                            print(f"发生错误：{e}")
                            print("Connection error. Trying again in 2 seconds.")
                            time.sleep(2)
                            
                break # 请求成功，则打破死循环
            except Exception as e:
                print(f"发生错误：{e}")
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)
        

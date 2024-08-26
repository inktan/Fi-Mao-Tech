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

    options = webdriver.ChromeOptions()  # 配置 chrome 启动属性
    options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    browser = webdriver.Chrome(options=options)

    folder_path_template = r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\architizer'
    page_index = 2573
    project_count = 30858
    while True:
        if page_index==1:
            url ='https://architizer.com/projects/q/'
        elif page_index>1:
            url = f'https://architizer.com/projects/q/page:{page_index}/'
        page_index+=1

        if page_index>12691:
            break

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

                project_links = extract_project_href_from_thumb_blocks(html)#请求出错，则陷入无限请求中
                project_links = ['https://architizer.com' +i for i in project_links]
                # print(project_links)
                if len(project_links) == 0: # 请求出错，则陷入无限请求中
                    print("Connection error. Trying again in 2 seconds.")
                    time.sleep(2)
                    continue
                                
                for project_link in project_links:
                    while True:
                        try:
                            get_pro_lits_info(project_link) # 请求出错，则陷入无限请求中
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
                time.sleep(2)
        




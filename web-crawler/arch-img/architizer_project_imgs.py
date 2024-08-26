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

def download_image_(url, file_path):
    count = 0
    while True:
        count+=1
        if count>90:
            return
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                # print("图片下载成功：", file_path)
                return
        except Exception as e:
            print(f"下载图片发生错误：{e}")
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

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

if __name__ == '__main__':
    folder_path = r"D:\Ai-clip-seacher\AiArchLibAdd-20240822\architizer"
    project_folders = [folder_path + '\\' + folder for folder in os.listdir(folder_path) if folder.startswith("project_")]

    for project_folder in tqdm(project_folders):
        project_imgs_folder = project_folder + f'\imgs' 
        if not os.path.exists(project_imgs_folder):
            os.makedirs(project_imgs_folder)
        # print(project_imgs_folder)
        print(project_imgs_folder,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        json_file_path = project_folder + '\project_imgs_links.json'
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 遍历并打印每个键值对
        for index, img_url in enumerate(data['project_imgs_links']):
            # print(img_url)

            file_path = project_imgs_folder+ '\\' +f'img_{index}.jpg'
            file_exists = os.path.exists(file_path)
            if not file_exists and img_url.startswith('http'):
                download_image(img_url, file_path)


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
            else:
                return
        except Exception as e:
            print(f"下载图片发生错误：{e}")
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

# 替换为从浏览器中复制的cookie值
cookies = {
    'cookie_name1': 'sp=3a960e76-4058-48b2-9457-df093207eeaf; _strava4_session=tu86jjodb8npdv3aimjum9hi4i8iamu9; CloudFront-Key-Pair-Id=APKAIDPUN4QMG7VUQPSA; CloudFront-Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vaGVhdG1hcC1leHRlcm5hbC0qLnN0cmF2YS5jb20vKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTcyNTg1MTQ5OX0sIkRhdGVHcmVhdGVyVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzI0NjI3NDk5fX19XX0_; CloudFront-Signature=ePRxddae2gq9ARxHqgTk~C-O5eq1z7EnjGjFw8YRGcneOMx~5YGZayMj11Qcm~BNPQNO~gtJBPaujCkKz5DB1JY2QuzFJD5J7xRRWGn3aMYnnUTUVf3Btmg5Qs9VcYu-akvTqcBxGOV13~URrCa9sgL~~8VfvjJX2h0WX88PZ6giQqnH7xsuSNjxcDZ2EqW-LDc1YWm7RvblEyLjSm3RLakBvHpBOc3enxxMinNeN-cNN-A7~VtcQc8ew9Ks2dAesPBgVd4yW5ezXttBS5S-vlM~3-rr3b9c0TRRp2Er9008kWhVrDRbN3C9F54AG2RvYmwlsZcnqlmG4N0hPExgDg__',
}

def download_image(url, file_path):
    try:
        response = requests.get(url, cookies=cookies, stream=True)
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

    # 最左边
    # https://heatmap-external-a.strava.com/tiles-auth/all/purple/15/27414/13374.png?v=19
    # 最右边
    # https://heatmap-external-a.strava.com/tiles-auth/all/purple/15/27466/13397.png?v=19
    # 最高点
    # https://heatmap-external-a.strava.com/tiles-auth/all/purple/15/27440/13369.png?v=19
    # 最低点
    # https://heatmap-external-a.strava.com/tiles-auth/all/purple/15/27429/13416.png?v=19


    folder_path = r"D:\Ai-clip-seacher\strava_heatmap\imgs"

    for i in tqdm(range(27414,27468)): #X轴
        for j in range(13374,13416): #Y轴
            img_url = f'https://heatmap-external-a.strava.com/tiles-auth/all/orange/15/{i}/{j}.png?v=19'
            file_path = folder_path+ '\\' +f'img_{i}_{j}.png'

            # file_exists = os.path.exists(file_path)
            # if not file_exists and img_url.startswith('http'):

            download_image(img_url, file_path)
            time.sleep(3)
            # break


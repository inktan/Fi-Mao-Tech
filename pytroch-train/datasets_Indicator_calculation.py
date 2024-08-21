# -*- coding: utf-8 -*-

import pandas as pd
import os
import shutil

import os  
import csv  
import random

# 图片文件夹路径  
csv_file = r'f:\sv\imageability\Familiarity\5.csv'
img_dir = r'f:\sv\imageability\Familiarity\5'

# 获取文件夹中所有图片文件名  
img_files = [f for f in os.listdir(img_dir) if f.endswith('.jpg') or f.endswith('.png')]  
  
# 创建CSV文件并写入文件名  
with open(csv_file, 'w', newline='') as csvfile:  
    writer = csv.writer(csvfile)
    for img_file in img_files:  
        writer.writerow([img_file,random.randint(0, 100)])



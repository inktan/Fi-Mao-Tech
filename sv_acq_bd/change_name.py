# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
from datetime import datetime  
import os
import Equirec2Perspec as E2P 
import cv2
import os  

str01 = ['115.','116.','117.']
str02 = ['40.','39.']

output = r'E:\sv\er_huan\sv\sv_degree'

for i,filename in enumerate(tqdm(os.listdir(output))):

    for i in str01:
        for j in str02:
            if i in filename and j in filename:
                old_file_path = os.path.join(output, filename)  
                filename =  filename.replace(i,'_'+i).replace(j,'_'+j)  
                new_file_path = os.path.join(output, filename)  
                os.rename(old_file_path, new_file_path)
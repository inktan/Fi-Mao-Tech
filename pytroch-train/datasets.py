# -*- coding: utf-8 -*-

import torch
from torch.utils import data
from torch.utils.data import DataLoader
import torchvision
import numpy as np
import os
# from torchvision import transforms
# from pathlib import Path
import cv2
import pandas as pd
from tqdm import tqdm

import matplotlib.pyplot as plt

class PerDataset(data.Dataset):  # 继承Dataset
    def __init__(self,index,categories, csv_path=None):
        """
        这里定义数据
        """

        self.image_path = []
        self.image_name = []
        self.label = []
        self.img_id = []
        csv = pd.read_csv(csv_path)

        for i in range(10):#标签数据
            count = 0
            for  _index, j in csv.iterrows():
                if j[categories[index]] -1 ==i:
                    count+=1
                    self.image_path.append(j['编号'])
                    self.image_name.append(j['编号'])
                    self.label.append(float(i))
                    self.img_id.append(j['TOID'])

                    if count >20:
                        break

        self.image_path = np.array(self.image_path)
        self.image_name = np.array(self.image_name)
        self.label = np.array(self.label)
        self.img_id = np.array(self.img_id).astype('int')

        # self.image_path = csv['编号'].values
        # self.image_name = csv['编号'].values
        # self.label = csv[categories[index]].values - 1
        # self.img_id = csv['TOID'].astype('int').values

        images_size = len(self.image_path)  # 图片的数量
        self.images = torch.zeros(images_size, 3, 250, 250, dtype=torch.uint8)  # 640-->250 创建一个都是0的tensor，后面进行值更新。

        print(f'准备数据中，{csv_path}...，共有{images_size}张图片！')

        for i, filename in tqdm(enumerate(self.image_path)):
            file_path = r'D:\BaiduNetdiskDownload\ScoringSystem\rating_sv\\' +filename+".jpg"
            print(i, f'==>{file_path}标签为{categories[index]}')
            img_arr = cv2.imread(file_path)
            img_arr = cv2.resize(img_arr, [250, 250])
            img_t = torch.from_numpy(img_arr)  # 将图片转为tensor
            img_t = img_t.permute(2, 0, 1)  # 在原始的图片中是高、宽、通道，这里改为通道、高、宽
            img_t = img_t[:3]  # 这里为了保证只要前3个通道，因为有些可能有alpha通道
            self.images[i] = img_t  # 通过索引操作，将图片值更新至之前的0填充tensor

        self.images = self.images / 255.0  # 值压缩到[0,1]

        print(f'数据准备完毕!')

        self.labels = torch.from_numpy(self.label)

        if len(self.image_name) != 0:
            self.len = len(self.image_name)
        else:
            self.len = 0

    def __getitem__(self, index):
        """
        必须实现的一个类，获取图片，以及对应的label，另外返回图片的名称
        """
        image = self.images[index, :, :, :]
        label = self.labels[index]
        img_id = self.img_id[index]

        return image, label, img_id
        # return image, label

    def __len__(self):
        return self.len

if __name__ == "__main__":
    csv_path = './data/middle_data/gsv_labeled_train.csv'

    train_dt = PerDataset(csv_path)
    image, label, img_id = train_dt.__getitem__(2)
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
from PIL import Image
import torch
import numpy as np

import matplotlib.pyplot as plt

class PerDataset(data.Dataset):  # 继承Dataset
    def __init__(self, csv_path=None):
        """
        这里定义数据
        """

        self.image_path = []
        self.label = []
        self.images = []

        csv = pd.read_csv(csv_path)
        print(f'准备数据中，{csv_path}...，共有{csv.shape[0]}张图片！')

        for  _index, j in csv.iterrows():
            try:
                file_path = 'E:\\work\\sv_shushu\\谷歌\\街景_960_720\\' +j[0]
                # print(file_path)
                img = Image.open(file_path)
                img_resized = img.resize((250, 250))
                img_arr = np.array(img_resized)
                img_t = torch.from_numpy(img_arr)
                img_t = img_t.permute(2, 0, 1)
                if img_t.shape[0] == 4:
                    img_t = img_t[:3]
                self.images.append(img_t)
                
                self.image_path.append(j[0])
                self.label.append(j[1]-1)
            except:
                print(f'图片{file_path}加载失败！')
                continue

        self.image_path = np.array(self.image_path)
        self.label = np.array(self.label)
        self.labels = torch.from_numpy(self.label)
       
        self.images = np.array(self.images)
        self.images = torch.from_numpy(self.images)
        self.images = self.images / 255.0  # 值压缩到[0,1]

        images_size = len(self.image_path)  # 图片的数量
        print(f'数据准备完毕! {csv_path}...，共有{images_size}张图片！')

        if len(self.image_path) != 0:
            self.len = len(self.image_path)
        else:
            self.len = 0

    def __getitem__(self, index):
        """
        必须实现的一个类，获取图片，以及对应的label，另外返回图片的名称
        """
        image = self.images[index, :, :, :]
        label = self.labels[index]

        return image, label

    def __len__(self):
        return self.len

if __name__ == "__main__":
    csv_path = r'e:\work\sv_shushu\谷歌\1 噪聲水平(Sound intensity).csv'

    train_dt = PerDataset(csv_path)
    # image, label, img_id = train_dt.__getitem__(2)
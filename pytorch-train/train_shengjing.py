# -*- coding: utf-8 -*-

import torch
from torch.utils import data
from torch.utils.data import DataLoader
import torchvision
# import numpy as np
import os
# from torchvision import transforms
# from pathlib import Path
import cv2
import pandas as pd
from tqdm import tqdm

import matplotlib.pyplot as plt
# from datasets import PerDataset
from datasets_gougou import PerDataset

def train(train_csv):
    BATCHSIZE = 10
    EPOCHS = 10
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # train_csv = r'e:\work\sv_shushu\谷歌\1 噪聲水平(Sound intensity).csv'
    model_path = train_csv.replace('.csv', '.pth')
    # 引入训练集
    train_dt = PerDataset(train_csv)
    img_train = DataLoader(train_dt, batch_size=BATCHSIZE, shuffle=True)  # shuffle随机化

    model = torchvision.models.densenet121(torchvision.models.DenseNet121_Weights)
    model.classifier = torch.nn.Linear(in_features=1024, out_features=5, bias=True)

    optimizer = torch.optim.Adam(params=model.parameters(), lr=0.001)  # Create adam optimizer
    lossFuction = torch.nn.CrossEntropyLoss()

    model = model.to(device)
    for epoch in range(EPOCHS):
        '''train'''
        model.train()  # train模式：启用Dropout， Batch Normalization的参数会学习和更新

        acc_epoch_count_train = 0
        acc_epoch_count_val = 0

        for batchidx, dt in enumerate(img_train):
            images, y = dt[0].to(device), dt[1].to(device)

            outputs = model(images)
            loss = lossFuction(outputs, y.long())

            # backward
            optimizer.zero_grad()  # 每次backward会对梯度累加，因此每次backward前要把梯度清零
            loss.backward()
            optimizer.step()

            avg_loss = loss.item()
            # print(outputs)
            # print(y)
            
            # probs, out_label = outputs.max(axis=1)
            # probs = probs.detach().cpu().numpy()
            # out_label = out_label.detach().cpu().numpy()
            # print(probs)
            # print(out_label)

            #         print(avg_loss)

            acc_count = sum(outputs.argmax(axis=1) == y)

            acc_epoch_count_train += acc_count

            all_nums = ((batchidx + 1) * BATCHSIZE)

            # print(acc_epoch_count_train.item(), all_nums)

            acc_percentage = acc_count / BATCHSIZE
            acc_epoch_percentage = acc_epoch_count_train / all_nums

            # print(
            #     '=== Train Epoch: {0:d}/{1:d} === Iter:{2:d} === avg_Loss: {3:.2f} === BatchAcc: {4:.2f} === allAcc: {5:.2f} ==='. \
            #     format(epoch, EPOCHS, batchidx, avg_loss, acc_percentage, acc_epoch_percentage))

    torch.save(model, model_path)

if __name__ == "__main__":

    csv_paths = []
    csv_names = []
    accepted_formats = (".csv")

    csv_path_list =[
        # r'E:\work\sv_YJ_20240924\points',
        r'E:\work\sv_shushu\谷歌\train',
        ]
    for folder_path in csv_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    csv_paths.append(file_path)
                    csv_names.append(file)
                    
    # csv_paths = [
    #     r'e:\work\sv_juanjuanmao\澳门特别行政区_矢量路网\道路_15m_unique_01.csv',
    #     ]

    total_rows = 0
    for file_path in csv_paths:
        train(file_path)

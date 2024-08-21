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
from datasets import PerDataset

def train(i,model_names,categories):
    BATCHSIZE = 10
    EPOCHS = 10
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_csv = r'D:\BaiduNetdiskDownload\ScoringSystem\gsv_labeled_train.csv'
    val_csv = r'D:\BaiduNetdiskDownload\ScoringSystem\gsv_labeled_val.csv'

    # 引入训练集
    train_dt = PerDataset(i,categories,train_csv)
    img_train = DataLoader(train_dt, batch_size=BATCHSIZE, shuffle=True)  # shuffle随机化

    # 引入测试集
    val_dt = PerDataset(i,categories,val_csv)
    img_val = DataLoader(val_dt, batch_size=BATCHSIZE, shuffle=True)  # shuffle随机化

    model = torchvision.models.densenet121(torchvision.models.DenseNet121_Weights)
    model.classifier = torch.nn.Linear(in_features=1024, out_features=287, bias=True)

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
            #         print(outputs)
            #         print(y)
            #         print(avg_loss)

            acc_count = sum(outputs.argmax(axis=1) == y)

            acc_epoch_count_train += acc_count

            all_nums = ((batchidx + 1) * BATCHSIZE)

            print(acc_epoch_count_train.item(), all_nums)

            acc_percentage = acc_count / BATCHSIZE
            acc_epoch_percentage = acc_epoch_count_train / all_nums

            print(
                '=== Train Epoch: {0:d}/{1:d} === Iter:{2:d} === avg_Loss: {3:.2f} === BatchAcc: {4:.2f} === allAcc: {5:.2f} ==='. \
                format(epoch, EPOCHS, batchidx, avg_loss, acc_percentage, acc_epoch_percentage))

        '''eval'''
        model.eval()  # eval模式：不启用Dropout，Batch Normalization的参数保持不变

        with torch.no_grad():  # 告诉pytorch，此段不需要构建计算图，更加安全
            for batchidx_val, dt_val in enumerate(img_val):
                images_val, y_val = dt_val[0].to(device), dt_val[1].to(device)

                outputs_val = model(images_val)
                loss_val = lossFuction(outputs_val, y_val.long())
                avg_loss_val = loss_val.item()

                acc_count_val = sum(outputs_val.argmax(axis=1) == y_val)
                acc_epoch_count_val += acc_count_val

                all_nums_val = ((batchidx_val + 1) * BATCHSIZE)

                print(acc_epoch_count_val, all_nums_val)
                acc_percentage_val = acc_count_val / BATCHSIZE
                acc_epoch_percentage_val = acc_epoch_count_val / all_nums_val

                print(
                    '=== Eval Epoch: {0:d}/{1:d} === Iter:{2:d} === avg_Loss: {3:.2f} === BatchAcc: {4:.2f} === allAcc: {5:.2f} ==='. \
                    format(epoch, EPOCHS, batchidx_val, avg_loss_val, acc_percentage_val, acc_epoch_percentage_val))

    torch.save(model, f'D:\BaiduSyncdisk\FiMaoTech\S03_Pytorch_style\weight_scoring_system/{model_names[i]}_epoch{epoch}.pth')

if __name__ == "__main__":
    model_names = ["A","B","C","D","E","F","G","H","I","J"]
    categories=["可接近性（非常差→非常好）",\
                "维护情况（非常差→非常好）",\
                "变化性（非常单调→非常多变）",\
                "自然性（非常不自然→非常自然）",\
                "色彩丰富性（非常单调→非常丰富）",\
                "景观要素布局（非常杂乱→非常合理）",\
                "庇护性（非常封闭→非常开放）",\
                "卫生状况（非常脏乱→非常干净）",\
                "安全性（非常不安全→非常安全）",\
                "总体印象（非常差→非常好）"]
    
    for i in range(10):
        train(i,model_names,categories)
        # break

# -*- coding: utf-8 -*-

import torch
from torchvision import transforms,datasets,models
import os
from torch.utils.data import Dataset, DataLoader 
import h5py
import numpy as np

class CustomDataset(Dataset): 
    '''
    这里定义预测图像数据所在文件夹
    ''' 
    def __init__(self, h5path, transform=None):
        db = h5py.File(h5path, "r")
        
        self.s2s = np.array(db['sen2'])
        self.labels = np.array(db['label'])
    
        self.transform = transform  

    def __len__(self):  
        return len(self.labels)
  
    def __getitem__(self, idx):  
        s2 = self.s2s[idx]
        if self.transform:  
            s2 = self.transform(s2)
        label = self.labels[idx]

        s2 = torch.from_numpy(s2)  
        s2 = s2.permute(2, 0, 1)

        return s2, np.argmax(label) 

def load_dataset(train_data_path, validationdata_path, test_data_path, batch_size, split=False, split_ratio=0.8):
    # 训练集图像预处理：缩放裁剪、图像增强、转 Tensor、归一化
    transformation = transforms.Compose(
            [transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    transformation = None
    
    # Load all the images, and transform
    train_dataset = CustomDataset(train_data_path, transform=transformation)
    validation_dataset = CustomDataset(validationdata_path, transform=transformation)
    test_dataset = CustomDataset(test_data_path, transform=transformation)
    
    # 
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size, shuffle=False,num_workers=1) # shuffle是否打乱顺序
    validation_loader = torch.utils.data.DataLoader(validation_dataset, batch_size, shuffle=False,num_workers=1)# num_workers使用几个工作进程
    
    return train_loader, validation_loader
    
def train(model, device, train_loader, validation_loader, epochs):
    model = model.to(device)
    optimizer = torch.optim.Adam(params=model.parameters(), lr=0.001)  # Create adam optimizer
    lossFuction = torch.nn.CrossEntropyLoss()

    for epoch in range(epochs):
        '''train'''
        model.train()  # train模式：启用Dropout， Batch Normalization的参数会学习和更新

        acc_epoch_count_train = 0
        acc_epoch_count_val = 0

        for batchidx, dt in enumerate(train_loader):
            images, y = dt[0].to(device), dt[1].to(device)

            outputs = model(images)
            loss = lossFuction(outputs, y.long())

            # backward
            optimizer.zero_grad()  # 每次backward会对梯度累加，因此每次backward前要把梯度清零
            loss.backward()
            optimizer.step()
            avg_loss = loss.item()

            acc_count = sum(outputs.argmax(axis=1) == y)
            acc_epoch_count_train += acc_count
            all_nums = ((batchidx + 1) * train_loader.batch_size)
            print(acc_epoch_count_train.item(), all_nums)

            acc_percentage = acc_count / train_loader.batch_size
            acc_epoch_percentage = acc_epoch_count_train / all_nums

            print(
                '=== Train Epoch: {0:d}/{1:d} === Iter:{2:d} === avg_Loss: {3:.2f} === BatchAcc: {4:.2f} === allAcc: {5:.2f} ==='. \
                format(epoch, epochs, batchidx, avg_loss, acc_percentage, acc_epoch_percentage))

        '''eval'''
        model.eval()  # eval模式：不启用Dropout，Batch Normalization的参数保持不变

        with torch.no_grad():  # 告诉pytorch，此段不需要构建计算图，更加安全
            for batchidx_val, dt_val in enumerate(validation_loader):
                images_val, y_val = dt_val[0].to(device), dt_val[1].to(device)

                outputs_val = model(images_val)
                loss_val = lossFuction(outputs_val, y_val.long())
                avg_loss_val = loss_val.item()

                acc_count_val = sum(outputs_val.argmax(axis=1) == y_val)
                acc_epoch_count_val += acc_count_val

                all_nums_val = ((batchidx_val + 1) * train_loader.batch_size)

                print(acc_epoch_count_val, all_nums_val)
                acc_percentage_val = acc_count_val / train_loader.batch_size
                acc_epoch_percentage_val = acc_epoch_count_val / all_nums_val

                print(
                    '=== Eval Epoch: {0:d}/{1:d} === Iter:{2:d} === avg_Loss: {3:.2f} === BatchAcc: {4:.2f} === allAcc: {5:.2f} ==='. \
                    format(epoch, epochs, batchidx_val, avg_loss_val, acc_percentage_val, acc_epoch_percentage_val))

def main():
    # all_models = torchvision.models.list_models()
    # print(all_models)
    # model_name ='convnext_base'
    # weights_enum = torchvision.models.get_model_weights(model_name)
    # for weight in weights_enum:
    #     print(weight)

    # model = torchvision.models.convnext_base()
    # categories=   [ '愉悦的','放松的','乏味的','焦虑的']

    # for i in range(10):
    #     train(i,model_names,categories)
        # break

    epochs = 20
    batch_size = 5

    folder = r'D:\ProgramData\GitHub\LCZ_MSMLA\data'

    '''
    So2SatLCZ42数据集中的影像块的尺寸定义为32X32像素
    对应于320X320m的物理尺寸
    共获得了400673对哨兵影像块
    整个数据集的容量约为56GB
    '''

    train_data_path =os.path.join(folder,r'standard_all_win48_split0.125_train.h5')
    validationdata_path =os.path.join(folder,r'standard_all_win48_split0.125_val.h5')
    test_data_path =os.path.join(folder,r'standard_all_win48_split0.125_test.h5')
    train_loader, validation_loader = load_dataset(train_data_path, validationdata_path, test_data_path, batch_size, split=True)

    block_setting = [
        models.convnext.CNBlockConfig(128, 256, 3),
        models.convnext.CNBlockConfig(256, 512, 3),
        models.convnext.CNBlockConfig(512, 1024, 27),
        models.convnext.CNBlockConfig(1024, None, 3),
    ]
    model = models.convnext.ConvNeXt(block_setting,num_classes=17)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # device = "cpu"
    
    train(model,device,train_loader, validation_loader,epochs)

    torch.save(model, f'E:\GitHub\LCZ_MSMLA\data/lcz.pth')

if __name__ == "__main__":

    main()
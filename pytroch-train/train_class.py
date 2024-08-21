# -*- coding: utf-8 -*-

import torch
from torchvision import transforms,datasets,models
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader 
import pandas as pd  
import torchvision
import tqdm
import torchvision.models as models

class CustomDataset(Dataset): 
    '''
    这里定义预测图像数据所在文件夹
    ''' 
    def __init__(self,  csv_file, img_dir, transform=None):  
        self.data = pd.read_csv(csv_file)  
        self.img_dir = img_dir  
        self.transform = transform  
        # self.img_names = [i for i in os.listdir(img_dir) if i.endswith('jpg') ==True or i.endswith('jpeg')  ==True or i.endswith('png')  ==True ] # 读取文件夹中的所有图片名  

    def __len__(self):  
        return len(self.data)  
  
    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.data.iloc[idx]['file_path'])  
        image = Image.open(img_path)
        image = image.convert('RGB')
        target = self.data.iloc[idx]['label-index']

        if self.transform:  
            image = self.transform(image)  # 如果有定义转换，则应用转换  
        return image, target  # 返回图片和对应的索引  
    
def load_dataset(csv_file, img_dir, batch_size, split=False, split_ratio=0.9):
    # 训练集图像预处理：缩放裁剪、图像增强、转 Tensor、归一化
    transformation = transforms.Compose(
            [transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    
    # Load all the images, and transform
    full_dataset = CustomDataset(csv_file, img_dir,transform=transformation)
    
    if split == False:
        loader = torch.utils.data.DataLoader(full_dataset, batch_size, shuffle=False)
        return loader
    else:
        # 需要划分数据集
        # Spliting into training(80%) and validation(20%)
        train_size = int(len(full_dataset) * split_ratio)  # 训练集的大小
        validation_size = len(full_dataset) - train_size  # 测试集的大小
        
        # torch split
        train_dataset, validation_dataset  = torch.utils.data.random_split(full_dataset, [train_size, validation_size])
        
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size, shuffle=False,num_workers=1) # shuffle是否打乱顺序
        validation_loader = torch.utils.data.DataLoader(validation_dataset, batch_size, shuffle=False,num_workers=1)# num_workers使用几个工作进程
        
        return train_loader, validation_loader
    
def train(model, device, train_loader, validation_loader, epochs):
    model = model.to(device)
    optimizer = torch.optim.Adam(params=model.parameters(), lr=0.001)  # Create adam optimizer
    # lossFuction =torch.nn.MSELoss()  # 均方误差损失函数  
    lossFuction = torch.nn.CrossEntropyLoss()

    for epoch in range(epochs):
        # '''train'''
        model.train()  # train模式：启用Dropout， Batch Normalization的参数会学习和更新

        acc_epoch_count_train = 0
        acc_epoch_count_val = 0

        for batchidx, dt in enumerate(train_loader):
            
            images, y = dt[0].to(device), dt[1].to(device)

            outputs = model(images)
            loss = lossFuction(outputs, y.long())

        #     # backward
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

        # '''eval'''
        # model.eval()  # eval模式：不启用Dropout，Batch Normalization的参数保持不变

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
    categories=   ['macao_histirical_arch_decorate']

    epochs = 40
    batch_size = 5

    for i in range(1):
        tar_train = categories[i]

        csv_file = r'e:\work\sv_zhoujunling\modified_file.csv'
        img_dir = r''
        train_loader, validation_loader = load_dataset(csv_file, img_dir, batch_size, split=True)

        # block_setting = [
        #     models.convnext.CNBlockConfig(128, 256, 3),
        #     models.convnext.CNBlockConfig(256, 512, 3),
        #     models.convnext.CNBlockConfig(512, 1024, 27),
        #     models.convnext.CNBlockConfig(1024, None, 3),
        # ]
        # model = models.convnext.ConvNeXt(block_setting,num_classes=46)
        model = models.resnet152(num_classes=46)

        # model_path= r'e:\work\sv_zhoujunling\macao_histirical_arch_decorate_01.pth'
        # model = torch.load(model_path)   
        
        # 加载预训练的ConvNeXt模型
        # model = models.convnext_base(pretrained=True)
             
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        train(model,device,train_loader, validation_loader,epochs)
        torch.save(model, r'e:\work\sv_zhoujunling\macao_histirical_arch_resnet152.pth')

if __name__ == "__main__":
    main()
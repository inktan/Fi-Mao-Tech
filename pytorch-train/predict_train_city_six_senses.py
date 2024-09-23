# -*- coding: utf-8 -*-

import torch
from tqdm import tqdm

torch.cuda.empty_cache()
import torch
from torchvision import transforms,datasets,models
import os
import pandas as pd
from torch.utils.data import Dataset, DataLoader 
from PIL import Image
import numpy as np
  
class CustomDataset(Dataset): 
    '''
    这里定义预测图像数据所在文件夹
    ''' 
    def __init__(self, img_dir, transform=None):  
        self.img_dir = img_dir  
        self.transform = transform  
        self.img_names = [i for i in os.listdir(img_dir) if i.endswith('jpg') ==True or i.endswith('jpeg')  ==True or i.endswith('png')  ==True ] # 读取文件夹中的所有图片名  

    def __len__(self):  
        return len(self.img_names)  
  
    def __getitem__(self, idx):  
        img_path = os.path.join(self.img_dir, self.img_names[idx])  # 拼接图片路径  
        image = Image.open(img_path).convert('RGB')  # 打开图片，转换为RGB格式
        if self.transform:  
            image = self.transform(image)  # 如果有定义转换，则应用转换  
        return image, img_path  # 返回图片和对应的索引  
  
# 定义转换  
transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()]) 

def load_dataset(data_path, batch_size):
    '''
    创建数据集和数据加载器
    '''
    # 训练集图像预处理：缩放裁剪、图像增强、转 Tensor、归一化
    transformation = transforms.Compose(
            [transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
    
    # Load all the images, and transform
    full_dataset = CustomDataset(data_path, transform=transformation)
    
    loader = torch.utils.data.DataLoader(full_dataset, batch_size, shuffle=False)
    return loader
  
def predict(model,device,predict_loader,predict_csv):
    model.to(device)
    model.eval()

    df_list = []
    for batchidx_predict, dt_predict in enumerate(predict_loader):
        images_predict,out_name = dt_predict[0].to(device),dt_predict[1]
        probs = model(images_predict)
        probs = probs.squeeze(1).detach().cpu().numpy()  # 这将删除第二个维度（索引为1的维度），如果它的尺寸是1的话
        
        img_df = pd.DataFrame({'out_name':list(out_name),'out_label': probs,})
        df_list.append(img_df)

        print((batchidx_predict+1)*batch_size,len(predict_loader.dataset))

    result = pd.concat(df_list)
    result.to_csv(predict_csv,index=False)

    print(f'预测结束，已结果文件生成文件，地址位{predict_csv}')

if __name__ == "__main__":
    categories= ['wealthy']
    batch_size = 5
    predictn_folder = r'E:/sv/build-HEB/test'  # split into training(80%) and validation(20%)
    predict_csv= f"E:/sv/build-HEB/test/{categories[0]}_temp.csv"
    model_path= f"E:/sv/build-HEB/{categories[0]}_.pth"
    model = torch.load(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    predict_loader = load_dataset(predictn_folder, batch_size)
    predict(model,device,predict_loader,predict_csv)







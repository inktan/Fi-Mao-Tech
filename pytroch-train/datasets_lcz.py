# -*- coding: utf-8 -*-
import torch
from torch.utils.data import Dataset, DataLoader 
import h5py
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA  
from torchvision import transforms,datasets,models

class CustomDataset(Dataset): 
    '''
    这里定义预测图像数据所在文件夹
    ''' 
    def __init__(self, h5path, transform=None):
        db = h5py.File(h5path, "r")
        
        self.s2s = np.array(db['sen2'])
        self.labels = np.array(db['label'])
    
        self.transform = transform
        self.pca = PCA(n_components=3)  

    def __len__(self):  
        return len(self.self.labels)
  
    def __getitem__(self, idx):  
        s2 = self.s2s[idx]
        if self.transform:  
            s2 = self.transform(s2)
        label = self.labels[idx]
        return s2, np.argmax(label) 

if __name__ == "__main__":
    csv_path = 'E:\GitHub\LCZ_MSMLA\data\standard_all_win48_split0.125_test.h5'

    train_dt = CustomDataset(csv_path)
    s2, label = train_dt.__getitem__(2)


    # 使用 reshape 方法将图像的形状改变为 (height, width, 3)  
    # 注意：这里我们假设新的通道维度为3，你可能需要根据实际情况进行调整  
    new_shape = (s2.shape[0], s2.shape[1], 5)  
    image_reduced = s2.reshape(new_shape)

    tensor = torch.from_numpy(image_reduced)  
    
    print(tensor)

    # transformation = transforms.Compose(
    #         [
    #         transforms.RandomResizedCrop(224),
    #         transforms.RandomHorizontalFlip(),
    #         transforms.ToTensor(),
    #         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    #         ])


    # s3 = s2[:,:,0:3]

    # s3=transformation(s3)

    # s4 = torch.from_numpy(s3) 

    # s5 = s4.permute(2, 0, 1)

    # plt.imshow(s2[:,:,3],cmap=plt.cm.get_cmap('Greens'))

    # plt.imshow(s2[:,:,0:3])
    # plt.colorbar()
    # plt.title('Sentinel-2')

    plt.show()
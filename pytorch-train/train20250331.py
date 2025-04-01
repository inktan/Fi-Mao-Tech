import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import pandas as pd
import os

# 1. 定义自定义数据集类
class PlacePulseDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): 包含图片名和分数的CSV文件路径
            root_dir (string): 图片目录
            transform (callable, optional): 可选的变换操作
        """
        self.annotations = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.annotations.iloc[idx, 0])
        image = Image.open(img_name).convert('RGB')
        score = torch.tensor(self.annotations.iloc[idx, 1], dtype=torch.float32)
        
        if self.transform:
            image = self.transform(image)
            
        return image, score

# 2. 定义模型
class ScorePredictor(nn.Module):
    def __init__(self):
        super(ScorePredictor, self).__init__()
        # 使用预训练的ResNet作为特征提取器
        self.cnn = models.resnet18(pretrained=True)
        # 替换最后的全连接层
        num_ftrs = self.cnn.fc.in_features
        self.cnn.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 1)
        )
        
    def forward(self, x):
        return self.cnn(x)

# 3. 训练函数
def train_model(model, criterion, optimizer, dataloaders, num_epochs=25):
    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs-1}')
        print('-' * 10)
        
        # 每个epoch都有训练和验证阶段
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()  # 训练模式
            else:
                model.eval()   # 评估模式
                
            running_loss = 0.0
            
            # 迭代数据
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device).unsqueeze(1)
                
                # 梯度清零
                optimizer.zero_grad()
                
                # 前向传播
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    
                    # 反向传播+优化仅在训练阶段
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                # 统计
                running_loss += loss.item() * inputs.size(0)
            
            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            
            print(f'{phase} Loss: {epoch_loss:.4f}')
    
    return model

# 4. 预测函数
def predict_score(model, image_path, transform):
    """
    预测单张图片的分数
    Args:
        model: 训练好的模型
        image_path: 图片路径
        transform: 图像变换
    Returns:
        预测的分数
    """
    model.eval()
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(image)
    
    return output.item()

# 5. 主程序
if __name__ == '__main__':
    # 参数设置
    data_dir = 'place_pulse'
    csv_file = os.path.join(data_dir, 'votes.csv')
    image_dir = os.path.join(data_dir, 'images')
    batch_size = 32
    num_epochs = 20
    
    # 数据变换
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize(256),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    
    # 创建数据集
    full_dataset = PlacePulseDataset(csv_file, image_dir)
    
    # 划分训练集和验证集
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    
    # 设置不同变换
    train_dataset.dataset.transform = data_transforms['train']
    val_dataset.dataset.transform = data_transforms['val']
    
    # 创建数据加载器
    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4),
        'val': DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    }
    
    # 设备设置
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # 初始化模型
    model = ScorePredictor().to(device)
    
    # 损失函数和优化器
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练模型
    model = train_model(model, criterion, optimizer, dataloaders, num_epochs=num_epochs)
    
    # 保存模型
    torch.save(model.state_dict(), 'place_pulse_scorer.pth')
    
    # 示例：对新图片进行预测
    test_image_path = 'test_image.jpg'  # 替换为你的测试图片路径
    predicted_score = predict_score(model, test_image_path, data_transforms['val'])
    print(f'Predicted score for {test_image_path}: {predicted_score:.2f}')
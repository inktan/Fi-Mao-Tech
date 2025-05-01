import geopandas as gpd
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
import joblib
from pathlib import Path

# 设置随机种子保证可重复性
torch.manual_seed(42)
np.random.seed(42)

# 1. 数据加载与预处理
def preprocess_data(input_path):
    """加载并预处理SHP数据"""
    gdf = gpd.read_file(input_path)
    
    # 定义特征列和目标列
    feature_cols = ['NEAR_DIST', 'dem', 'density', 'landcover', 'ylight', 'ndvi', 
                   'podu', 'population', 'poxiang', 'rain', 'road2', 'temper', 
                   'densitywa', 'lengthwa']
                   
# 筛选相关性
# dem
# ylight
# ndvi
# podu ---
# population ---
# road2
# lengthwa

    feature_cols = ['dem', 'ylight', 'ndvi','podu', 'population', 'road2', 'lengthwa']
    feature_cols = ['ylight', 'road2']
    target_col = 'Join_Count'
    
    # 检查列是否存在
    missing_cols = [col for col in feature_cols + [target_col] if col not in gdf.columns]
    if missing_cols:
        raise ValueError(f"缺少必要的列: {missing_cols}")
    
    # 独热编码landcover
    # landcover_dummies = pd.get_dummies(gdf['landcover'], prefix='landcover')
    # gdf = pd.concat([gdf.drop(columns=['landcover']), landcover_dummies], axis=1)
    
    # 更新特征列
    numeric_cols = [col for col in feature_cols if col != 'landcover']
    # new_feature_cols = numeric_cols + list(landcover_dummies.columns)
    new_feature_cols = numeric_cols
    
    # 标准化数值特征
    scaler = StandardScaler()
    gdf[numeric_cols] = scaler.fit_transform(gdf[numeric_cols])
    
    # 准备训练数据
    X = gdf[new_feature_cols].values.astype(np.float32)
    y = gdf[target_col].values.astype(np.float32).reshape(-1, 1)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, scaler, new_feature_cols

# 2. 定义MLP模型
class BirdCountMLP(nn.Module):
    def __init__(self, input_size):
        super(BirdCountMLP, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
    
    def forward(self, x):
        return self.layers(x)

# 3. 训练函数
def train_model(X_train, y_train, input_size, epochs=100, batch_size=32):
    """训练MLP模型"""
    # 转换为PyTorch张量
    train_dataset = TensorDataset(
        torch.from_numpy(X_train), 
        torch.from_numpy(y_train))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # 初始化模型
    model = BirdCountMLP(input_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练循环
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        if (epoch+1) % 10 == 0:
            print(f'Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(train_loader):.4f}')
    
    return model

# 4. 评估函数
def evaluate_model(model, X_test, y_test):
    """评估模型性能"""
    model.eval()
    with torch.no_grad():
        test_dataset = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test))
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        total_loss = 0.0
        predictions, actuals = [], []
        
        for inputs, targets in test_loader:
            outputs = model(inputs)
            loss = nn.MSELoss()(outputs, targets)
            total_loss += loss.item()
            predictions.extend(outputs.numpy())
            actuals.extend(targets.numpy())
        
        # 计算RMSE
        rmse = np.sqrt(total_loss / len(test_loader))
        print(f'Test RMSE: {rmse:.4f}')
        
        return np.array(predictions), np.array(actuals)

# 5. 保存模型和预处理对象
def save_artifacts(model, scaler, feature_cols, output_dir):
    """保存模型和相关文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存PyTorch模型
    model_path = output_dir / 'bird_count_mlp.pth'
    torch.save(model.state_dict(), model_path)
    
    # 保存标准化器
    scaler_path = output_dir / 'standard_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    
    # 保存特征列表
    features_path = output_dir / 'feature_columns.txt'
    with open(features_path, 'w') as f:
        f.write('\n'.join(feature_cols))
    
    print(f"模型和相关文件已保存到: {output_dir}")

# 主流程
def main(year):
    # 输入输出路径
    input_shp = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_train_valid_data.shp'
    output_dir = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_models'
    
    # 1. 数据预处理
    X_train, X_test, y_train, y_test, scaler, feature_cols = preprocess_data(input_shp)
    
    # 2. 训练模型
    print("\n开始训练MLP模型...")
    model = train_model(X_train, y_train, input_size=len(feature_cols), epochs=100)
    
    # 3. 评估模型
    print("\n评估模型性能:")
    predictions, actuals = evaluate_model(model, X_test, y_test)
    
    # 4. 保存模型和预处理对象
    save_artifacts(model, scaler, feature_cols, output_dir)

if __name__ == "__main__":

    # years = ['98','99','00',
    # '01','02','03','04','05','06','07','08','09','10',
    # '11','12','13','14','15','16','17','18','19','20',
    # '22','23',]

    years = ['98','99','00',
    '01','02','03','04','05','06','07','08','09','10',
    '11','12','13','14','15','16','17','18','19','20',
    '22','23',]

    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        try:
            # 运行主函数
            main(year)
        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")
            continue
        # main(year)
import geopandas as gpd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np

# 1. 读取SHP文件
def read_shp_file(file_path):
    """读取SHP文件并提取所需列"""
    gdf = gpd.read_file(file_path)
    
    # 提取需要的列
    X = gdf[['ylight', 'road2']].values
    y = gdf['Join_Count'].values
    
    return X, y

# 2. 数据预处理
def preprocess_data(X, y):
    """数据预处理：标准化和划分训练测试集"""
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X_scaled)
    y_tensor = torch.FloatTensor(y).view(-1, 1)  # 确保y是列向量
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X_tensor, y_tensor, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, scaler

# 3. 定义PyTorch模型
class RegressionModel(nn.Module):
    """简单的回归神经网络模型"""
    def __init__(self, input_size):
        super(RegressionModel, self).__init__()
        self.layer1 = nn.Linear(input_size, 64)
        self.layer2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.output(x)
        return x

# 4. 训练模型
def train_model(X_train, y_train, epochs=100, learning_rate=0.01):
    """训练回归模型"""
    input_size = X_train.shape[1]
    model = RegressionModel(input_size)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        # 前向传播
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    
    return model

# 5. 评估模型
def evaluate_model(model, X_test, y_test):
    """评估模型性能"""
    with torch.no_grad():
        predictions = model(X_test)
        mse = nn.MSELoss()(predictions, y_test)
        print(f'Test MSE: {mse.item():.4f}')

# 6. 主函数
def main(year):
    # 文件路径 - 替换为你的SHP文件路径
    shp_file = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_valid_data.shp'
    
    # 1. 读取数据
    X, y = read_shp_file(shp_file)
    
    # 2. 预处理数据
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)
    
    # 3. 训练模型
    print("开始训练模型...")
    model = train_model(X_train, y_train, epochs=100, learning_rate=0.01)
    
    # 4. 评估模型
    print("\n模型评估结果:")
    evaluate_model(model, X_test, y_test)
    
    # 5. 保存模型
    torch.save(model.state_dict(), f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_regression_model.pth')
    print("\n模型已保存为 e:\work\sv_goufu\MLP20250428\year24_regression_model.pth")
    
    # 如果需要，也可以保存scaler
    import joblib
    joblib.dump(scaler, f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_scaler.pkl')
    print("数据标准化器已保存为 e:\work\sv_goufu\MLP20250428\year24_scaler.pkl")

if __name__ == "__main__":
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        main(year)
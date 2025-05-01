import geopandas as gpd
import torch
import joblib
import numpy as np
from torch import nn

# 1. 定义与训练时相同的模型结构
class RegressionModel(nn.Module):
    """必须与训练时相同的模型结构"""
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

# 2. 加载模型和标准化器
def load_model_and_scaler(model_path, scaler_path):
    """加载训练好的模型和标准化器"""
    # 加载标准化器
    scaler = joblib.load(scaler_path)
    
    # 初始化模型结构
    # 注意：这里假设输入特征为2个(ylight和raod2)
    model = RegressionModel(input_size=2)
    
    # 加载模型权重
    model.load_state_dict(torch.load(model_path))
    model.eval()  # 设置为评估模式
    
    return model, scaler

# 3. 读取新数据并进行预测
def predict_new_data(shp_path, model, scaler):
    """读取新SHP文件并进行预测"""
    # 读取新数据
    gdf = gpd.read_file(shp_path)
    
    # 检查必要的列是否存在
    required_columns = ['ylight', 'road2']
    for col in required_columns:
        if col not in gdf.columns:
            raise ValueError(f"输入SHP文件缺少必要列: {col}")
    
    # 提取特征数据
    X_new = gdf[required_columns].values
    
    # 使用相同的标准化器进行标准化
    X_scaled = scaler.transform(X_new)
    
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X_scaled)
    
    # 进行预测
    with torch.no_grad():
        predictions = model(X_tensor).numpy().flatten()
    
    # 添加预测结果到GeoDataFrame
    gdf['predict_'] = predictions
    
    return gdf

# 4. 主函数
def main(year):
    # 文件路径配置
    model_path = f'e:\\work\\sv_goufu\\MLP20250428\\year20_regression_model.pth'  # 之前保存的模型
    scaler_path = f'e:\\work\\sv_goufu\\MLP20250428\\year20_scaler.pkl'          # 之前保存的标准化器
    # model_path = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_regression_model.pth'  # 之前保存的模型
    # scaler_path = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_scaler.pkl'          # 之前保存的标准化器
    new_shp_path = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_valid_data.shp'       # 新SHP文件路径
    new_shp_path = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_02.shp'       # 新SHP文件路径
    output_shp_path = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_02_predictions.shp'  # 输出文件路径
    
    # 1. 加载模型和标准化器
    print("加载模型和标准化器...")
    model, scaler = load_model_and_scaler(model_path, scaler_path)
    
    # 2. 读取新数据并进行预测
    print(f"读取新数据: {new_shp_path}...")
    try:
        result_gdf = predict_new_data(new_shp_path, model, scaler)
    except Exception as e:
        print(f"错误: {str(e)}")
        return
    
    # 3. 保存结果
    print(f"保存预测结果到: {output_shp_path}...")
    result_gdf.to_file(output_shp_path)
    print("处理完成!")

if __name__ == "__main__":
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        main(year)
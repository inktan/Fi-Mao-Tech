import geopandas as gpd
import pandas as pd
import torch
import joblib
from pathlib import Path
import numpy as np
from torch import nn

# 1. 定义与训练时相同的模型架构
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

# 2. 创建预测器类
class BirdCountPredictor:
    def __init__(self, model_dir):
        self.model_dir = Path(model_dir)
        self._load_artifacts()
    
    def _load_artifacts(self):
        """加载所有必要的模型和预处理文件"""
        # 加载特征列列表
        with open(self.model_dir / 'feature_columns.txt', 'r') as f:
            self.feature_columns = [line.strip() for line in f.readlines()]
        
        # 加载标准化器
        self.scaler = joblib.load(self.model_dir / 'standard_scaler.pkl')
        
        # 初始化并加载模型
        self.model = BirdCountMLP(len(self.feature_columns))
        self.model.load_state_dict(torch.load(self.model_dir / 'bird_count_mlp.pth'))
        self.model.eval()
    
    def preprocess_input(self, input_df):
        """预处理输入数据"""
        df = input_df.copy()
                
        # 处理landcover的独热编码
        landcover_cols = [col for col in self.feature_columns if col.startswith('landcover_')]
        if 'landcover' in df.columns:
            landcover_dummies = pd.get_dummies(df['landcover'], prefix='landcover')
            df = pd.concat([df.drop(columns=['landcover']), landcover_dummies], axis=1)
        
        # 确保所有独热编码列都存在
        for col in landcover_cols:
            if col not in df.columns:
                df[col] = 0
        
        # 检查必要列是否存在
        missing_cols = set(self.feature_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"缺少必要的列: {missing_cols}")

        # 标准化数值特征
        numeric_cols = [col for col in self.feature_columns if not col.startswith('landcover_')]
        df[numeric_cols] = self.scaler.transform(df[numeric_cols])
        
        return df[self.feature_columns].values.astype(np.float32)
    
    def predict(self, input_df):
        """执行预测并返回结果"""
        X = self.preprocess_input(input_df)
        with torch.no_grad():
            predictions = self.model(torch.from_numpy(X)).numpy().flatten()
        return predictions

# 3. 主函数：读取SHP、预测、保存结果
def predict_and_save_shp(model_dir, input_shp_path, output_shp_path):
    """
    完整预测流程：
    1. 加载模型
    2. 读取SHP文件
    3. 进行预测
    4. 添加预测结果到原始数据
    5. 保存为新SHP文件
    
    参数:
        model_dir: 模型目录路径
        input_shp_path: 输入SHP文件路径
        output_shp_path: 输出SHP文件路径
    """
    # 初始化预测器
    predictor = BirdCountPredictor(model_dir)
    
    # 读取SHP文件
    print(f"正在读取SHP文件: {input_shp_path}")
    gdf = gpd.read_file(input_shp_path)
    
    # 进行预测
    print("正在进行预测...")
    predictions = predictor.predict(gdf)
    
    # 添加预测结果到原始数据
    gdf['predicted_Join_Count'] = predictions
    gdf['predicted_Join_Count'] = gdf['predicted_Join_Count'].round(2)  # 保留2位小数
    
    # 保存结果
    print(f"正在保存结果到: {output_shp_path}")
    gdf.to_file(output_shp_path)
    
    print(f"预测完成！已添加预测结果并保存到: {output_shp_path}")
    print(f"预测值统计:")
    print(gdf['predicted_Join_Count'].describe())

# 4. 使用示例
if __name__ == "__main__":
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        try:

            # 设置路径
            model_directory = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_models'

            # model_directory = r'E:\work\sv_goufu\MLP\year21\models'
            input_shapefile = f'E:\\work\\sv_goufu\\MLP20250428\\year{year}_valid_data.shp'
            output_shapefile = input_shapefile.replace('.shp', '_with_predictions.shp')
            
            # 执行预测并保存
            predict_and_save_shp(model_directory, input_shapefile, output_shapefile)

        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")
            continue
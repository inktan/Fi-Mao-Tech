import geopandas as gpd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import numpy as np
import geopandas as gpd
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import geopandas as gpd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import warnings

# 忽略警告信息
warnings.filterwarnings('ignore')

class RandomForestModel:
    def __init__(self, n_estimators=100, random_state=42):
        """
        初始化随机森林回归模型
        :param n_estimators: 树的数量
        :param random_state: 随机种子
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            oob_score=True,
            n_jobs=-1  # 使用所有CPU核心
        )
        self.scaler = StandardScaler()
        self.feature_importances_ = None
    
    def train(self, train_shp_path, test_size=0.2):
        """训练随机森林回归模型"""
        # 1. 读取训练数据
        train_gdf = gpd.read_file(train_shp_path)
        print("原始数据行数:", len(train_gdf))
        print("训练数据列名:", train_gdf.columns)
        
        # 检查必要列是否存在
        required_columns = ['Join_Count', 'road2', 'densitywa']
        if not all(col in train_gdf.columns for col in required_columns):
            raise ValueError("训练SHP文件中缺少所需的列")
        
        # 2. 删除含有NaN的行
        train_gdf = train_gdf.dropna(subset=required_columns)
        print("删除NaN后数据行数:", len(train_gdf))
        if len(train_gdf) == 0:
            raise ValueError("删除NaN后无有效数据可供训练")
        
        # 3. 准备数据
        X = train_gdf[['road2', 'densitywa']].values
        y = train_gdf['Join_Count'].values
        
        # 4. 数据归一化
        X_normalized = self.scaler.fit_transform(X)
        
        # 5. 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=test_size, random_state=42
        )
        
        # 6. 训练模型
        self.model.fit(X_train, y_train)
        self.feature_importances_ = self.model.feature_importances_
        
        # 7. 评估模型
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        mse_train = mean_squared_error(y_train, y_pred_train)
        r2_train = r2_score(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        r2_test = r2_score(y_test, y_pred_test)
        
        print("\n模型训练完成")
        print(f"特征重要性(road2, densitywa): {self.feature_importances_}")
        print(f"OOB Score: {self.model.oob_score_:.4f}")
        print("\n训练集评估:")
        print(f"MSE: {mse_train:.4f}, R²: {r2_train:.4f}")
        print("\n测试集评估:")
        print(f"MSE: {mse_test:.4f}, R²: {r2_test:.4f}")
        
        # 可视化特征重要性
        # self._plot_feature_importance()
        
        # 可视化实际值 vs 预测值
        # self._plot_actual_vs_predicted(y_train, y_pred_train, "训练集")
        # self._plot_actual_vs_predicted(y_test, y_pred_test, "测试集")
    
    def _plot_feature_importance(self):
        """绘制特征重要性图"""
        plt.figure(figsize=(10, 5))
        features = ['road2', 'densitywa']
        plt.bar(features, self.feature_importances_)
        plt.title('特征重要性')
        plt.ylabel('重要性得分')
        plt.show()
    
    def _plot_actual_vs_predicted(self, y_true, y_pred, title):
        """绘制实际值 vs 预测值图"""
        plt.figure(figsize=(10, 6))
        plt.scatter(y_true, y_pred, alpha=0.5)
        plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'k--', lw=2)
        plt.xlabel('实际值')
        plt.ylabel('预测值')
        plt.title(f'{title} - 实际值 vs 预测值')
        plt.grid(True)
        plt.show()
    
    def predict_shp(self, predict_shp_path, output_shp_path):
        """预测新SHP文件并添加预测列"""
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("请先训练模型")
        
        # 1. 读取预测数据
        predict_gdf = gpd.read_file(predict_shp_path)
        print("\n预测数据原始行数:", len(predict_gdf))
        print("预测数据列名:", predict_gdf.columns)
        
        # 检查必要列是否存在
        required_columns = ['road2', 'densitywa']
        if not all(col in predict_gdf.columns for col in required_columns):
            raise ValueError("预测SHP文件中缺少所需的列")
        
        # 2. 删除含有NaN的行
        predict_gdf = predict_gdf.dropna(subset=required_columns)
        print("删除NaN后预测数据行数:", len(predict_gdf))
        if len(predict_gdf) == 0:
            raise ValueError("删除NaN后无有效数据可供预测")
        
        # 3. 准备预测数据
        X_predict = predict_gdf[['road2', 'densitywa']].values
        # X_predict_normalized = self.scaler.transform(X_predict)
        X_predict_normalized = X_predict
        
        # 4. 进行预测
        predictions = self.model.predict(X_predict_normalized)
        
        # 5. 添加预测列到GeoDataFrame
        predict_gdf['predict'] = predictions
        
        # 6. 保存结果
        predict_gdf.to_file(output_shp_path, encoding='utf-8')
        print(f"\n预测完成，结果已保存到: {output_shp_path}")
        
        # 打印预测统计信息
        print("\n预测结果统计:")
        print(predict_gdf['predict'].describe())
        
        return predict_gdf

# 使用示例
if __name__ == "__main__":
    # 初始化模型
    rf_model = RandomForestModel(n_estimators=200)  # 可以调整树的数量
    
    # 训练模型
    train_shp = r"e:\work\sv_goufu\MLP20250427\year20_01_train_valid_data.shp"  # 替换为训练SHP文件路径
    rf_model.train(train_shp, test_size=0.2)  # 使用20%数据作为测试集
    
    # 进行预测
    predict_shp = r"e:\work\sv_goufu\MLP20250427\year24_01.shp"  # 替换为预测SHP文件路径
    output_shp = r"e:\work\sv_goufu\MLP20250427\year24_01_predicted_results.shp"  # 输出文件路径

    
    # 执行预测并保存结果
    result_gdf = rf_model.predict_shp(predict_shp, output_shp)
    
    # 打印前5个预测结果
    print("\n前5个预测结果:")
    print(result_gdf[['road2', 'densitywa', 'predict']].head())

    

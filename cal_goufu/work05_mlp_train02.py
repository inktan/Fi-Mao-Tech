import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# 定义特征列和目标列
feature_cols = ['NEAR_DIST', 'dem', 'density', 'landcover', 'ylight', 'ndvi', 
                'podu', 'population', 'poxiang', 'rain', 'road2', 'temper', 
                'densitywa', 'lengthwa']
target_col = 'Join_Count'

# 读取数据
gdf = gpd.read_file(r'e:\work\sv_goufu\MLP\year21\汇总数据-面\MLP21_filled_train_valid_data.shp')

# 确保目标列都大于0
gdf = gdf[gdf[target_col] > 0].copy()


# 检查landcover列是否为字符串/分类类型
if not pd.api.types.is_categorical_dtype(gdf['landcover']) and not pd.api.types.is_object_dtype(gdf['landcover']):
    print("警告: landcover列似乎不是分类类型，建议转换为字符串类型")
    gdf['landcover'] = gdf['landcover'].astype(str)

# 分离特征和目标
X = gdf[feature_cols]
y = gdf[target_col]

# 识别数值列和分类列
numeric_features = [col for col in feature_cols if col != 'landcover']
categorical_features = ['landcover']  # 需要独热编码的列

# 创建预处理管道
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 创建完整的模型管道
model_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    ))
])

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 训练模型
model_pipeline.fit(X_train, y_train)

# 评估函数
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    # 确保所有预测值都大于0
    y_pred = np.maximum(y_pred, 1e-6)
    
    print("Model Evaluation Metrics:")
    print(f"- MAE: {mean_absolute_error(y_test, y_pred):.4f}")
    print(f"- MSE: {mean_squared_error(y_test, y_pred):.4f}")
    print(f"- RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
    print(f"- R2: {r2_score(y_test, y_pred):.4f}")
    print(f"- Min Prediction: {y_pred.min():.4f}")
    print(f"- Max Prediction: {y_pred.max():.4f}")
    
    return y_pred

# 评估模型
test_predictions = evaluate_model(model_pipeline, X_test, y_test)

# 保存模型管道
model_path = r'E:\work\sv_goufu\MLP\year21\models\bird_count_prediction_pipeline.pkl'
joblib.dump(model_pipeline, model_path)

print(f"模型已保存到: {model_path}")

# 加载之前保存的模型管道
model_pipeline = joblib.load(model_path)

# 定义特征列（必须与训练时相同）
feature_cols = ['NEAR_DIST', 'dem', 'density', 'landcover', 'ylight', 'ndvi', 
                'podu', 'population', 'poxiang', 'rain', 'road2', 'temper', 
                'densitywa', 'lengthwa']

# 读取新数据（替换为你的新SHP文件路径）
new_data_path = r'e:\work\sv_goufu\MLP\year21\汇总数据-面\MLP21_filled.shp'
new_gdf = gpd.read_file(new_data_path)

# 检查是否包含所有需要的特征列
missing_cols = set(feature_cols) - set(new_gdf.columns)
if missing_cols:
    raise ValueError(f"新数据缺少必要的特征列: {missing_cols}")

# 检查landcover列是否为字符串/分类类型
if not pd.api.types.is_categorical_dtype(new_gdf['landcover']) and not pd.api.types.is_object_dtype(new_gdf['landcover']):
    print("警告: landcover列似乎不是分类类型，建议转换为字符串类型")
    new_gdf['landcover'] = new_gdf['landcover'].astype(str)

# 提取特征数据
X_new = new_gdf[feature_cols]

# 使用管道进行预测（自动应用相同的预处理）
predictions = model_pipeline.predict(X_new)

# 确保所有预测值大于0
predictions = np.maximum(predictions, 1e-6)

# 将预测结果添加到GeoDataFrame
new_gdf['pre_birds'] = predictions

# 保存带有预测结果的新文件
output_path = new_data_path.replace('.shp', '_with_predictions.shp')
new_gdf.to_file(output_path, encoding='utf-8')

print(f"预测完成，结果已保存到: {output_path}")
print("\n预测结果统计:")
print(new_gdf['pre_birds'].describe())

# import matplotlib.pyplot as plt

# 简单可视化预测结果
# plt.figure(figsize=(10, 6))
# plt.hist(new_gdf['pre_birds'], bins=30, color='skyblue', edgecolor='black')
# plt.title('Predicted Bird Count Distribution')
# plt.xlabel('Predicted Bird Count')
# plt.ylabel('Frequency')
# plt.grid(True, alpha=0.3)
# plt.show()

# 空间分布可视化（如果数据有几何信息）
# if hasattr(new_gdf, 'geometry'):
#     fig, ax = plt.subplots(figsize=(12, 8))
#     new_gdf.plot(column='pre_birds', ax=ax, legend=True,
#                 legend_kwds={'label': "Predicted Bird Count", 'orientation': "horizontal"},
#                 cmap='YlOrRd', scheme='quantiles', markersize=10)
#     ax.set_title('Spatial Distribution of Predicted Bird Count')
#     plt.tight_layout()
#     plt.show()
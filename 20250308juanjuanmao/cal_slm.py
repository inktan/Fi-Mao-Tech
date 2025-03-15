import numpy as np
import pysal as ps
from pysal.model import spreg
import geopandas as gpd
import libpysal  # 导入 libpysal
import os  
import glob  
import numpy as np
import pandas as pd  
from sklearn.preprocessing import MinMaxScaler   
import random

import numpy as np
import libpysal
from libpysal.weights import KNN  # 使用 KNN 权重矩阵
from spreg import ML_Lag

gdf = gpd.read_file(r"e:\work\sv_juanjuanmao\20250308\吸引力数据\attractive_force.shp")  # 替换为你的 SHP 文件路径
print(gdf.columns)

# 假设 gdf 是你的地理数据框
y = gdf['Y'].values
# X = gdf[['X_length_m', 'X_ashcan', 'X_tree_100', 'X_chair_10', 'X_poster_1', 'X_window_1', 'X_Num_adja', 'X_shop_num', 'X_open_soc', 'X_Mix_busi']].values

# 检查 X 的维度
# print("X shape:", X.shape)  # 确保输出为 (n_samples, 11)

# 使用 KNN 创建权重矩阵（例如，选择 4 个最近邻居）
# W = KNN.from_dataframe(gdf, k=4)

# 计算空间滞后模型
# slm = ML_Lag(y, X, W, name_y='Y', name_x=['X_length_m', 'X_ashcan', 'X_tree_100', 'X_chair_10', 'X_poster_1', 'X_window_1', 'X_Num_adja', 'X_shop_num', 'X_open_soc', 'X_Mix_busi'])

# 输出模型结果
# print(slm.summary)

import numpy as np
import libpysal
from libpysal.weights import KNN
from spreg import ML_Lag

# 假设 gdf 是你的地理数据框
# y = gdf['Y'].values
# 
# 只保留部分自变量（避免共线性）
selected_features = ['X_length_m', 'X_ashcan', 'X_tree_100', 'X_chair_10', 'X_poster_1', 'X_window_1', 'X_Num_adja', 'X_Mix_busi']

indicator_matrix = pd.DataFrame()  
for i in selected_features:
    indicator_matrix[i] = gdf[i]
# # 初始化MinMaxScaler  
scaler = MinMaxScaler(feature_range=(0, 1))  
for i in range(len(indicator_matrix.columns)):
    indicator_matrix_index = indicator_matrix.columns[[i]].tolist()
    indicator_matrix[indicator_matrix_index] = scaler.fit_transform(indicator_matrix[indicator_matrix_index])

X = indicator_matrix[selected_features].values

# 检查 X 的维度
print("X shape after feature selection:", X.shape)  # 输出应为 (8, 4)

# 检查自变量的方差
# print("Variance of X:", np.var(X, axis=0))

# 使用 KNN 创建权重矩阵（例如，选择 2 个最近邻居）
W = KNN.from_dataframe(gdf, k=2)
print(W.neighbors)  # 检查每个样本的邻居

# 计算空间滞后模型
slm = ML_Lag(y, X, W, name_y='Y', name_x=selected_features)

# 输出模型结果
print(slm.summary)
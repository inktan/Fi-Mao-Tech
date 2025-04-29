import os  
import glob  
import numpy as np
import pandas as pd  
from sklearn.preprocessing import MinMaxScaler
import random
# 读取语义分析数据
file_path1 = r'e:\work\sv_shushu\所有指标\ss_mean01.csv'  # 替换为你的第一个CSV文件的路径  
df1 = pd.read_csv(file_path1)

# 使用rename()方法重命名列
df1 = df1.rename(columns={'id': 'iamge_name'})

# # 天-3
# # 植被 植物-18-67 地形-95-14
# # 建筑物 建筑 2- 墙-1 围栏-33 摩天大楼-49
# # 路 道路-88-7-53 人行道-12 杆-39 红绿灯 交通号志-137
indicator_matrix = pd.DataFrame()  

_sky = df1.columns[[3]]
_plant = df1.columns[[14,18,67,95]]
_building = df1.columns[[1,2,33,49]]
_road = df1.columns[[88,7,53,12,39,137]]

indicator_matrix['iamge_name'] = df1[['iamge_name']].sum(axis=1)  
indicator_matrix['Sum_sky'] = df1[_sky.tolist()].sum(axis=1)  
indicator_matrix['Sum_plant'] = df1[_plant.tolist()].sum(axis=1)  
indicator_matrix['Sum_building'] = df1[_building.tolist()].sum(axis=1)  
indicator_matrix['Sum_road'] = df1[_road.tolist()].sum(axis=1)  
  
add_columns = ['Sound_intensity',
 'Vibrant',
 'Calm',
 'Uneventful',
 'Annoying',
 'Eventful',
 'Monotonous',
 'Soundscape_quality',
 'Traffic_noise',
 'Human_sounds',
 'Natural_sounds',
 'Mechanicl_noise',
 'Music_noise',
 'Pleasant',
 'Chaotic']

# 为每个新列生成1-5之间的随机整数
for column in add_columns:
    indicator_matrix[column] = np.random.randint(1, 6, size=len(indicator_matrix))

# 合并六感数据
folder_path=r'E:\work\sv_shushu\谷歌\index\six'
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]
for file in file_paths:
    df = pd.read_csv(file, encoding='GBK')
    need_columns = []
    for col in df.columns:
        if not col in indicator_matrix.columns:
            need_columns.append(col)
    # 按照列方向进行排序
    indicator_matrix = pd.concat([indicator_matrix, df[need_columns]], axis=1)

# indicator_matrix.to_csv(r'e:\work\sv_shushu\谷歌\ss_indicator_matrix_normalization.csv', index=False)
  
# 初始化MinMaxScaler  
scaler = MinMaxScaler(feature_range=(0, 1)) 

# 分离需要缩放的列和不需要缩放的列
columns_to_scale = indicator_matrix.columns.difference(['iamge_name'])

# 检查需要缩放的列是否都是数值类型
if not all(pd.api.types.is_numeric_dtype(indicator_matrix[col]) for col in columns_to_scale):
    raise ValueError("所有需要缩放的列必须是数值类型。")

scaler = MinMaxScaler(feature_range=(0, 1))
# 拟合并转换需要缩放的列
scaled_values = scaler.fit_transform(indicator_matrix[columns_to_scale])
# 将缩放后的数据转换为DataFrame，并保持列名
scaled_df = pd.DataFrame(scaled_values, columns=columns_to_scale, index=indicator_matrix.index)
# 将缩放后的列与未缩放的'iamge_name'列合并
indicator_matrix = pd.concat([indicator_matrix[['iamge_name']], scaled_df], axis=1)

# 使用正则表达式提取 lon 和 lat
pattern = r'_([^_]+)_([^_]+)_(\d{4})'  # 匹配 _<lon>_<lat>_<year>
# 提取匹配的部分
extracted = indicator_matrix['iamge_name'].str.extract(pattern)
# 重命名列
extracted.columns = ['lon', 'lat', 'year']  # 根据需要调整列名
# 如果只需要 lon 和 lat，可以只保留这两列
indicator_matrix = indicator_matrix.join(extracted[['lon', 'lat']])

print(indicator_matrix.columns)
print(indicator_matrix.shape)
print(indicator_matrix.head())

indicator_matrix.to_csv(r'E:\work\sv_shushu\谷歌\index\scaler.csv', index=False)


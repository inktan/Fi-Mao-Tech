import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import geopandas as gpd

file_name = r"e:\work\sv_shushu\谷歌\index\six_kmeans.shp"
gdf = gpd.read_file(file_name)
gdf = gdf.iloc[:, 1:-1]

print(gdf.columns)
print(gdf.head())
print(gdf['cluster'].value_counts())

# raise('stop')
# 提取聚类 1 的数据
cluster_1_data = gdf[gdf['cluster'] == 1].iloc[:, :-1]  # 排除聚类标签列
# 标准化数据到 0-1 范围
cluster_1_data_normalized = cluster_1_data.apply(lambda x: (x - x.min()) / (x.max() - x.min()))

# 创建一个画布
plt.figure(figsize=(10, 8))

# 设置山脊图的 y 轴偏移量
n_features = cluster_1_data_normalized.shape[1]  # 特征数量
y_offsets = np.arange(n_features)  # 每个特征的 y 轴偏移量

# 绘制每个特征的山脊图
for i, column in enumerate(cluster_1_data_normalized.columns):
    sns.kdeplot(
        cluster_1_data_normalized[column] + y_offsets[i],  # 在 y 轴方向上堆叠
        label=column,
        fill=True,
        alpha=0.6,
        bw_adjust=0.5,  # 调整带宽
        color=sns.color_palette("husl", n_features)[i],  # 使用不同颜色
    )

# 设置图形属性
plt.xlabel('Contribution (Normalized to 0-1)')
plt.ylabel('Feature')
plt.yticks(y_offsets, cluster_1_data_normalized.columns)  # 设置 y 轴刻度标签
plt.title('Ridgeline Plot of Feature Contributions for Cluster 1')
plt.grid(True)
# plt.legend()
plt.show()
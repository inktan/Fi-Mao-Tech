import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import contextily as cx
import os
from tqdm import tqdm
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import shutil

import numpy as np
import matplotlib.pyplot as plt

output_filepath = r'e:\work\sv_shushu\谷歌\index\six_sv_scaler.shp'
polygons_gdf = gpd.read_file(output_filepath)

# 提取特征数据（排除第一列和最后一列）
x = polygons_gdf.iloc[:, 1:-1]

# 尝试不同的聚类数
cluster_range = range(2, 101)  # 从 2 到 19 的聚类数
silhouette_scores = []

for n_clusters in cluster_range:
    kmeans = KMeans(n_clusters=n_clusters, max_iter=500)
    labels = kmeans.fit_predict(x)
    silhouette_avg = silhouette_score(x, labels)
    silhouette_scores.append(silhouette_avg)
    print(f"聚类数: {n_clusters}, 平均轮廓宽度: {silhouette_avg}")


# 创建画布，设置高宽比为 1:10
fig, ax = plt.subplots(figsize=(10, 4))  # 宽度为 10，高度为 1

# 绘制平均轮廓宽度随聚类数的变化
ax.plot(cluster_range, silhouette_scores, marker='o', markersize=2)  # 设置散点半径为最小

# 设置标题和轴标签
ax.set_xlabel('Numbers of clusters')  # 横标题为 nums
ax.set_ylabel('Average silhouette width')  # Y 轴标题为 width

# 设置 X 轴刻度
ax.set_xticks(range(0, 101, 10))  # 每 10 一个刻度
ax.set_xticks([6], minor=True)  # 在 X=6 处显示刻度
ax.set_xticklabels([6], minor=True)  # 显示刻度标签

# 在 X 轴等于 6 时，绘制一根竖向的黑色虚线
ax.axvline(x=6, color='black', linestyle='--', linewidth=1)

# 显示图形
plt.show()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib
import matplotlib.transforms as transforms

file_name = r"e:\work\sv_shushu\所有指标\six_sv_mean_kmeans.shp"
df = gpd.read_file(file_name)
df = df.iloc[:, 1:-1]

df = df.rename(columns={
    'Mechanicl_': 'Mechanicl',
    'Sum_buildi': 'Building',
    'Sum_plant': 'Plant',
    'Sum_road': 'Road',
    'Sum_sky': 'Sky'})

print(df.columns)
print(df.head())
print(df['cluster'].value_counts())

# 假设df是你的DataFrame，且有一个列'cluster'表示聚类结果
cluster_1_data = df[df['cluster'] == 5]

# 假设贡献度已经计算好并存储在DataFrame中
# 例如，每个特征的贡献度是它们的标准化值
contributions = cluster_1_data.iloc[:, :-1].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

# 设置图形风格
sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

# 创建一个图形和轴
fig, ax = plt.subplots(figsize=(10, 40))

# 定义颜色
palette = sns.color_palette("husl", len(contributions.columns))

# 设置每个特征的山脊图在y轴上的偏移量
y_offset = 2  # 每个特征之间的间隔

for i, column in enumerate(contributions.columns):
    # 计算 y 轴偏移量
    offset = i * y_offset  # 调整偏移量以控制山脊之间的距离

    # 创建转换对象，将 KDE 图沿 y 轴向上平移
    transform = transforms.Affine2D().translate(0, offset) + ax.transData
    # 绘制 KDE 图，并应用转换
    sns.kdeplot(contributions[column], ax=ax, label=column, color=palette[i], fill=True, alpha=0.5, linewidth=1.5, clip=(0, 1), transform=transform)
    # 添加水平线分隔
    ax.axhline(y=offset, color='black', linestyle='--', linewidth=0.5)

ax.axhline(y_offset*(len(contributions.columns) + 2), color='black', linestyle='--', linewidth=0.5)

# 设置 y 轴刻度
ax.set_yticks(range(0, (len(contributions.columns) )* y_offset, y_offset))  # 调整刻度范围和步长
ax.set_yticklabels(contributions.columns)

# 设置x轴范围
ax.set_xlim(0, 1)

# 添加标题和标签
ax.set_title('Contribution of Features in Cluster 1', fontsize=16)
ax.set_xlabel('value', fontsize=12)
ax.set_ylabel('Features', fontsize=12)

# 调整 y 轴刻度线的长度和标签的间距
ax.tick_params(axis='y', which='major', length=20, pad=10)  # 增加刻度线长度和标签间距

# 显示图例
# ax.legend(loc='upper right')

# 显示图形
plt.show()
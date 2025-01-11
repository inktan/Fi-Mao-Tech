import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

polygons = gpd.read_file(r'e:\work\sv_jourdan\arcgis\data\topython\polygon.shp')
points = gpd.read_file(r'e:\work\sv_jourdan\arcgis\data\topython\point.shp')

joined = gpd.sjoin(points, polygons, how="inner", op="within")

grouped = joined.groupby('NAME_2')['score'].apply(list)
df = pd.DataFrame(grouped).reset_index()
dict={}
for i in range(df.shape[0]):
    dict[df.iloc[i,0]] = df.iloc[i,1]

# 假设这是你的数据字典
dict_data = dict

plt.figure(figsize=(12, 12))
bplot = plt.boxplot(dict_data.values(), labels=dict_data.keys(), patch_artist=True)
# 使用colormap生成颜色
cmap = plt.get_cmap('viridis')  # 使用pastel色系
colors = [cmap(i) for i in range(len(dict_data))]

# 设置箱体颜色
for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)

# 设置须的颜色
for whisker in bplot['whiskers']:
    whisker.set(color='black', linewidth=1.5)

# 设置离群点的颜色
for flier in bplot['fliers']:
    flier.set(marker='o', color='red', alpha=0.5)

# 设置y轴的范围
plt.ylim(-2, 12)

plt.title("箱型图", fontsize=20, fontweight='bold', fontname='SimHei')
# 旋转x轴标签，避免重叠
plt.xticks(rotation=45, ha='right')
plt.ylabel("值", fontsize=20, fontweight='bold', fontname='SimHei')
# plt.grid(True)
plt.show()


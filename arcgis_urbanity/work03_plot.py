import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import contextily as cx
import tilemapbase

# 设置全局字体大小（默认是10，这里放大一倍）
plt.rcParams.update({'font.size': 20})  # 基础字体大小
plt.rcParams.update({'axes.titlesize': 24})  # 标题字体大小
plt.rcParams.update({'axes.labelsize': 22})  # 坐标轴标签大小
plt.rcParams.update({'xtick.labelsize': 20})  # x轴刻度标签大小
plt.rcParams.update({'ytick.labelsize': 20})  # y轴刻度标签大小
plt.rcParams.update({'legend.fontsize': 20})  # 图例字体大小

# 打开 Shapefile 文件
# shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_count01.shp'  # 替换为你的 Shapefile 路径
# shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_count_res1001.shp'  # 替换为你的 Shapefile 路径
shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_mean_kmeans.shp'  # 替换为你的 Shapefile 路径
# shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_mean_res10_kmeans.shp'  # 替换为你的 Shapefile 路径
gdf = gpd.read_file(shapefile_path)
gdf = gdf.copy()
gdf = gdf.to_crs(epsg=3857)  # web mercator
# gdf['sv_counts']=gdf['sv_counts']/4  # 归一化处理，除以4
gdf['cluster']=gdf['cluster'] # 归一化处理，除以4
# 检查是否存在 sv_counts 列
# if 'cluster' not in gdf.columns:
#     raise ValueError("The Shapefile must have a 'cluster' column.")

# 设置颜色和透明度
# 使用清新绿色系（绿色渐变）
# cmap = plt.get_cmap('Greens')  # Greens 是绿色系的颜色映射
# cmap = plt.get_cmap('Blues')  # Greens 是绿色系的颜色映射
cmap = plt.get_cmap('coolwarm')  # Greens 是绿色系的颜色映射
# norm = Normalize(vmin=gdf['sv_counts'].min(), vmax=gdf['sv_counts'].max())  # 归一化 sv_counts 值
norm = Normalize(vmin=gdf['cluster'].min(), vmax=gdf['cluster'].max())  # 归一化 sv_counts 值

# 创建 ScalarMappable 对象，用于颜色映射
sm = ScalarMappable(norm=norm, cmap=cmap)

# 绘制地图
fig, ax = plt.subplots(figsize=(20, 20))

# 遍历每一行，根据 sv_counts 设置颜色和透明度
for idx, row in gdf.iterrows():
    color = sm.to_rgba(row['cluster'])  # 根据 sv_counts 获取颜色
    # color = sm.to_rgba(row['sv_counts'])  # 根据 sv_counts 获取颜色
    gdf.iloc[[idx]].plot(ax=ax, color=color, alpha=0.86)  # 设置透明度为 0.6

# 添加颜色条并设置字体大小
cbar = plt.colorbar(sm, ax=ax)
# cbar.set_label('cluster', size=22)  # 颜色条标签大小
cbar.set_label('sv_counts', size=22)  # 颜色条标签大小
cbar.ax.tick_params(labelsize=20)  # 颜色条刻度标签大小

# 设置标题
ax.set_title('cluster Visualization with Gradient Green and Transparency', fontsize=24)
# ax.set_title('sv_counts Visualization with Gradient Green and Transparency', fontsize=24)
cx.add_basemap(ax, crs=gdf.crs, source=cx.providers.CartoDB.Positron)
# 显示图形
# plt.show()
# plt.savefig(r'e:\work\sv_shushu\20250423\plot\Figure_2_res10.png')
plt.savefig(r'e:\work\sv_shushu\20250423\plot\Figure_2.png')

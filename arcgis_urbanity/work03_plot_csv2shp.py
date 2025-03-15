import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import contextily as cx
import pandas as pd

input_file = r'e:\work\sv_shushu\谷歌\ss_indi_matrix_nor_scaler_point_kmeans.csv'
df = pd.read_csv(input_file)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=dst_crs)
gdf = gdf.copy()
gdf = gdf.to_crs(epsg=3857)  # web mercator

# 检查是否存在 sv_count 列
if 'cluster' not in gdf.columns:
    raise ValueError("The Shapefile must have a 'cluster' column.")

# 设置颜色和透明度
# 使用清新绿色系（绿色渐变）
cmap = plt.get_cmap('winter')  # Greens 是绿色系的颜色映射
norm = Normalize(vmin=gdf['cluster'].min(), vmax=gdf['cluster'].max())  # 归一化 sv_count 值

# 创建 ScalarMappable 对象，用于颜色映射
sm = ScalarMappable(norm=norm, cmap=cmap)

# 绘制地图
fig, ax = plt.subplots(figsize=(10, 10))

# 遍历每一行，根据 sv_count 设置颜色和透明度
for idx, row in gdf.iterrows():
    color = sm.to_rgba(row['cluster'])  # 根据 sv_count 获取颜色
    gdf.iloc[[idx]].plot(ax=ax, color=color, alpha=0.86)  # 设置透明度为 0.6

# 添加颜色条
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('cluster')  # 设置颜色条标签

# 设置标题
ax.set_title('cluster Visualization with Gradient Green and Transparency')
# cx.add_basemap(ax, crs=gdf.crs, source=cx.providers.CartoDB.Positron)
# 显示图形
plt.show()
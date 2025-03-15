import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import contextily as cx

# 打开 Shapefile 文件
shapefile_path = r'e:\work\九条路\上海市_50m_9roads.shp'  # 替换为你的 Shapefile 路径
gdf = gpd.read_file(shapefile_path)
gdf = gdf.copy()
gdf = gdf.to_crs(epsg=3857)  # web mercator
# 检查是否存在 sv_count 列
# if 'cluster' not in gdf.columns:
#     raise ValueError("The Shapefile must have a 'cluster' column.")

# 设置颜色和透明度
# 使用清新绿色系（绿色渐变）
cmap = plt.get_cmap('coolwarm')  # Greens 是绿色系的颜色映射
norm = Normalize(vmin=gdf['id'].min(), vmax=gdf['id'].max())  # 归一化 sv_count 值

# 创建 ScalarMappable 对象，用于颜色映射
sm = ScalarMappable(norm=norm, cmap=cmap)

# 绘制地图
fig, ax = plt.subplots(figsize=(10, 10))

# 遍历每一行，根据 sv_count 设置颜色和透明度
for idx, row in gdf.iterrows():
    color = sm.to_rgba(row['id'])  # 根据 sv_count 获取颜色
    gdf.iloc[[idx]].plot(ax=ax, color=color, alpha=0.86)  # 设置透明度为 0.6

# 添加颜色条
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('id')  # 设置颜色条标签

# 设置标题
ax.set_title('cluster Visualization with Gradient Green and Transparency')
cx.add_basemap(ax, crs=gdf.crs, source=cx.providers.CartoDB.Positron)
# 显示图形
plt.show()
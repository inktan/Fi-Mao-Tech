import geopandas as gpd
import matplotlib.pyplot as plt

# 读取 Shapefile 文件
gdf = gpd.read_file(r"e:\work\sv_juanjuanmao\20250308\八条路线\T7_50m_.shp")  # 替换为你的 .shp 文件路径

# 绘制几何图形
gdf.plot()  # 使用 geopandas 内置的 plot 方法（基于 matplotlib）
plt.title("Shapefile Geometry Visualization")
plt.show()

# gdf.plot(
#     color="lightblue",    # 填充颜色（适用于多边形）
#     edgecolor="black",    # 边界颜色
#     linewidth=0.5,        # 边界线宽
#     markersize=10,       # 点的大小（如果是点数据）
#     figsize=(10, 8)      # 图形大小
# )
# plt.show()

# gdf.plot(column="POPULATION", legend=True, cmap="viridis")  # POPULATION 是属性列名
# plt.show()
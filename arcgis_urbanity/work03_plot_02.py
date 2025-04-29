import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import contextily as cx

# 打开 Shapefile 文件
# shapefile_path = r'e:\work\sv_shushu\20250423\all_points_convex_hull_six_polygon.shp'
shapefile_path = r'e:\work\sv_shushu\20250423\all_points_convex_hull_six_polygon_res10.shp'
# shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_count.shp'
# shapefile_path = r'e:\work\sv_shushu\所有指标\six_sv_count_res10.shp'
gdf = gpd.read_file(shapefile_path)
gdf = gdf.copy()
gdf = gdf.to_crs(epsg=3857)  # web mercator

# 绘制地图
fig, ax = plt.subplots(figsize=(20, 20))

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

gdf.plot(
    ax=ax,
    alpha=0.15, edgecolor='k',
    categorical=True,
    legend=True, legend_kwds={'loc': 'upper left'},
)

cx.add_basemap(ax, crs=gdf.crs, source=cx.providers.CartoDB.Positron)

# 设置标题
# ax.set_title('sv_count Visualization with Gradient Green and Transparency')

# plt.show()
plt.savefig(r'e:\work\sv_shushu\20250423\plot\Figure_1_res10.png')
# plt.savefig(r'E:\work\sv_jumaorizhi\Figure_1.png')
import geopandas as gpd
from pyproj import CRS

# 打开SHP文件
gdf = gpd.read_file(r'e:\work\苏大-鹌鹑蛋好吃\20251015\research_area.shp')

# 检查当前坐标系
print("原始坐标系:", gdf.crs)

# 转换为WGS84坐标系 (EPSG:4326)
if gdf.crs != CRS.from_epsg(4326):
    gdf = gdf.to_crs(epsg=4326)
    print("已转换为WGS84坐标系")

# 获取整个数据集的经纬度范围
total_bounds = gdf.total_bounds
print(f"整个数据集的经纬度范围:")
print(f"最小经度: {total_bounds[0]}")
print(f"最小纬度: {total_bounds[1]}")
print(f"最大经度: {total_bounds[2]}")
print(f"最大纬度: {total_bounds[3]}")

# 获取每个几何体的经纬度范围
# for idx, row in gdf.iterrows():
#     bounds = row.geometry.bounds
#     print(f"\n要素 {idx} 的经纬度范围:")
#     print(f"最小经度: {bounds[0]}")
#     print(f"最小纬度: {bounds[1]}")
#     print(f"最大经度: {bounds[2]}")
#     print(f"最大纬度: {bounds[3]}")
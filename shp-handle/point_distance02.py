import geopandas as gpd
import random
from shapely.geometry import Point

# 读取Shapefile
shapefile_path = r'e:\work\sv_nadingzichidefangtoushi\merged_coordinates_01.shp'  # Replace with your shapefile path
gdf = gpd.read_file(shapefile_path)

# 这里假设是UTM区域33N（EPSG:32633），你需要根据实际情况替换
utm_crs = 'EPSG:32633'  # 替换为你的UTM区域
gdf = gdf.to_crs(utm_crs)

# 确保是点数据
if gdf.geom_type[0] != 'Point':
    raise ValueError("Shapefile must contain point data.")

# 随机选取一个点
random_index = random.randint(0, len(gdf) - 1)
random_point = gdf.iloc[random_index]['geometry']

# 计算每个点到随机点的距离
gdf['distance'] = gdf['geometry'].apply(lambda geom: geom.distance(random_point))

# 找到距离随机点最近的点
nearest_point_index = gdf['distance'].idxmin()
nearest_point = gdf.iloc[nearest_point_index]

# 输出结果
print(f"随机选取的点: {random_point}")
print(f"距离随机点最近的点: {nearest_point['geometry']}, 距离: {nearest_point['distance']}")
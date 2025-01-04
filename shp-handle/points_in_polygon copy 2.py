import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 读取CSV文件
df = pd.read_csv('your_file.csv')

# 假设CSV文件中有 'lon' 和 'lat' 列
# 将经纬度转换为点
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
geo_df = gpd.GeoDataFrame(df, geometry=geometry)

# 读取shapefile文件
shapefile = gpd.read_file('your_shapefile.shp')

# 假设shapefile中有两个多边形，分别是 'polygon1' 和 'polygon2'
polygon1 = shapefile[shapefile['name'] == 'polygon1'].geometry.unary_union
polygon2 = shapefile[shapefile['name'] == 'polygon2'].geometry.unary_union

# 判断点是否在polygon1中且不在polygon2中
geo_df['in_polygon1'] = geo_df.geometry.within(polygon1)
geo_df['not_in_polygon2'] = ~geo_df.geometry.within(polygon2)

# 筛选符合条件的点
filtered_df = geo_df[geo_df['in_polygon1'] & geo_df['not_in_polygon2']]

# 去掉临时列
filtered_df = filtered_df.drop(columns=['geometry', 'in_polygon1', 'not_in_polygon2'])

# 保存为新的CSV文件
filtered_df.to_csv('filtered_points.csv', index=False)
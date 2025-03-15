import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'f:\立方数据\2025年道路数据\【立方数据学社】上海市\上海市_50m_9roads.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=dst_crs)
# 保存为Shapefile
gdf.to_file(r'f:\立方数据\2025年道路数据\【立方数据学社】上海市\上海市_50m_9roads.shp', driver='ESRI Shapefile')

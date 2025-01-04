import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'f:\立方数据\2014-2020年GDP栅格数据（全国分省分市无需转发）\按城市裁剪的数据\【立方数据学社】上海市\China_GDP_2020_.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=dst_crs)
# 保存为Shapefile
gdf.to_file(input_file.replace('.csv','.shp'), driver='ESRI Shapefile')

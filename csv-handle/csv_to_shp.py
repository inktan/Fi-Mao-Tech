import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'e:\work\sv_xiufenganning\地理数据\ade_20k_语义00分割比例数据_03-_.csv'
# df = pd.read_csv(input_file, encoding='GBK')
df = pd.read_csv(input_file)

headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=dst_crs)
# 保存为Shapefile
out_file = input_file.replace('.csv', '.shp')
gdf.to_file(out_file, driver='ESRI Shapefile')


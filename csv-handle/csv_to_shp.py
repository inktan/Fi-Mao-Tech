import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'd:\work\sv_taiwan\points_tw.csv'
# df = pd.read_csv(input_file, encoding='GBK')
df = pd.read_csv(input_file)
# df = pd.read_excel(input_file)
# df = pd.read_excel(input_file)

headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

# gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=dst_crs)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=dst_crs)
# 保存为Shapefile
out_file = input_file.replace('.csv', '.shp')
# out_file = input_file.replace('.xlsx', '.shp')
gdf.to_file(out_file, driver='ESRI Shapefile')


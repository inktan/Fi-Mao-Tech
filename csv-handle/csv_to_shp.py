import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'f:\地学大数据\2024POI\2024华中地图poi\湖北省\武汉市POI数据.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.经度, df.纬度), crs=dst_crs)
# 保存为Shapefile
out_file = input_file.replace('.csv', '.shp')
gdf.to_file(out_file, driver='ESRI Shapefile')

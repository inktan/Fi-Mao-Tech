import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'f:\sv_suzhou\points_has_sv.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat), crs=dst_crs)
# 保存为Shapefile
gdf.to_file(r'f:\sv_suzhou\points_has_sv.shp', driver='ESRI Shapefile')

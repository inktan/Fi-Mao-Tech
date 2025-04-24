import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'e:\work\sv_jumaorizhi\xc_src_complexity_harmony.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=dst_crs)
# 保存为Shapefile
out_file = input_file.replace('.csv', '.shp')
gdf.to_file(out_file, driver='ESRI Shapefile')

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

input_file = r'e:\work\sv_gonhoo\0-Zvalue-Totle-fukuoka-city.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
dst_crs = 'EPSG:4326'

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs=dst_crs)
# 保存为Shapefile
gdf.to_file(r'E:\work\sv_gonhoo\value_shp\0-Zvalue-Totle-fukuoka-city.shp', driver='ESRI Shapefile')

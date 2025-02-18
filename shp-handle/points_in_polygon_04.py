import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

csv_file = r'f:\地学大数据\道路数据\澳门特别行政区\澳门特别行政区_15m_.csv' 

csv_df = pd.read_csv(csv_file)
geometry = [Point(xy) for xy in zip(csv_df['longitude'], csv_df['latitude'])]
gdf_points = gpd.GeoDataFrame(csv_df, geometry=geometry)
print(gdf_points.shape)
# 设置坐标参考系统（CRS），通常是WGS84（EPSG:4326）
gdf_points.set_crs(epsg=4326, inplace=True)

polygon_file = 'e:\work\sv_juanjuanmao\Export_Output-澳门\Export_Output-澳门.shp' 
gdf_polygons = gpd.read_file(polygon_file)
gdf_polygons.set_crs(epsg=4326, inplace=True)

gdf_polygons = gdf_polygons.to_crs(gdf_points.crs)

points_within_polygons = gpd.sjoin(gdf_points, gdf_polygons, predicate='within')

output_csv = 'E:\work\sv_juanjuanmao\Export_Output-澳门\points_within_polygons.csv' 
points_within_polygons.to_csv(output_csv, index=False)

print(f"保存了 {len(points_within_polygons)} 个落在多边形内的点到 {output_csv}")





import geopandas as gpd
import pandas as pd

shp_file_path = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_0m_01.shp'

points_df = gpd.read_file(shp_file_path)
print(f'去重前共有 {points_df.shape} 行数据')

points_df = points_df.drop_duplicates(subset=['longitude', 'latitude', 'name_2'])
# df_unique = points_df.drop_duplicates(subset=['id'])
# 打印去重后的数据行数
print(f'去重后共有 {points_df.shape} 行数据')

points_df.to_csv(shp_file_path.replace('_01.shp','_02.csv') , index=False)
# 检查 result_gdf 的类型
print(type(points_df))
# 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
if type(points_df) == pd.core.frame.DataFrame:
    points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))
points_df.to_file(shp_file_path.replace('_01.shp','_02.shp') , index=False)


import geopandas as gpd

shp_file_path = r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_05.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.columns.tolist())
# print(gdf.shape)
# print(gdf.head())
print(gdf)
# print(gdf.crs)
# print(gdf['geometry'].head())

# gdf = gdf.to_crs(epsg=4326)

# gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

# gdf = gpd.read_file(shp_file_path)

# 检查是否有 'fclass' 列
# if 'fclass' in gdf.columns:
#     unique_fclasses = gdf['fclass'].unique()
#     print("唯一 fclass 值:", unique_fclasses)
# else:
#     print("该 Shapefile 没有 'fclass' 字段！")
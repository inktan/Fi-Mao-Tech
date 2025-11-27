import geopandas as gpd

shp_file_path = r'f:\大数据\2024年我国多属性建筑矢量数据（免费获取）\合并后的数据（一个省份合并为一个shp文件）\北京市\北京市.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

# print(gdf.columns)
print(gdf.columns.tolist())
print(gdf.shape)
print(gdf.head())
# print(gdf)
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





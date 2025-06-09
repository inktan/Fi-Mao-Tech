import geopandas as gpd

shp_file_path = r'f:\立方数据\2024年我国多属性建筑矢量数据（免费获取）\合并后的数据（一个省份合并为一个shp文件）\西藏自治区\西藏自治区.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.shape)
print(gdf.head())
print(gdf.crs)
print(gdf['geometry'].head())

# gdf = gdf.to_crs(epsg=4326)

# gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

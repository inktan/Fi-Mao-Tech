import geopandas as gpd

shp_file_path = r'f:\立方数据\202405更新_2024年省市县三级行政区划数据（审图号：GS（2024）0650号）\shp格式的数据（调整过行政区划代码，补全省市县信息）\县.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.shape)
print(gdf.head())
print(gdf.crs)
print(gdf['geometry'].head())

# gdf = gdf.to_crs(epsg=4326)

# gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

import geopandas as gpd

# 加载Shapefile文件
gdf = gpd.read_file('f:\sv_suzhou\gis数据\道路网\苏州市.shp')

# 筛选包含“历史”的行
# 假设'name'是列名，根据实际情况替换
filtered_gdf = gdf[gdf['name'].str.contains('山塘', na=False)]

# 输出筛选后的结果
print(filtered_gdf['name'])

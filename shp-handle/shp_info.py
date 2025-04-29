import geopandas as gpd

shp_file_path = r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.shape)
print(gdf.head())
print(gdf.crs)
print(gdf['geometry'].head())

gdf = gdf.to_crs(epsg=4326)

gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

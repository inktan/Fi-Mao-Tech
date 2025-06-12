import geopandas as gpd

shp_file_path = r'd:\Users\wang.tan.GOA\Document\WXWork\1688853481969789\Cache\File\2025-06\867e0adab8d06fdf24eb0dad641dbf44_1e80b1583668a8bbf8540898561dd23e_8.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.shape)
print(gdf.head())
print(gdf.crs)
print(gdf['geometry'].head())

# gdf = gdf.to_crs(epsg=4326)

# gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

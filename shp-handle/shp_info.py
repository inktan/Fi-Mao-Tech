import geopandas as gpd

shp_file_path = r"e:\work\sv_goufu\MLP\year21\MLP21.shp"  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
print(gdf.shape)
print(gdf.head())

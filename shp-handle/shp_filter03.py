import geopandas as gpd

# 读取 Shapefile 文件
shp_file_path =r'f:\立方数据\2025年道路数据\【立方数据学社】上海市\上海市.shp'

gdf = gpd.read_file(shp_file_path)

print(gdf.columns)
columns_to_extract = ['title', 'page_type',gdf.geometry.name]
for col in columns_to_extract:
    if col not in gdf.columns:
        print(f"列 {col} 不存在于 Shapefile 文件中，请检查列名。")
        break
else:
    new_gdf = gdf[columns_to_extract]
    csv_file_path = r'e:\work\sv_gonhoo\fugang-Poi\fugang-page_type.shp'
    new_gdf.to_file(csv_file_path, index=False)

    print(f"新的 CSV 文件已保存到 {csv_file_path}")
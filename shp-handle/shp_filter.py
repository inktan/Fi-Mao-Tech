import geopandas as gpd

# 读取Shapefile文件
input_file = r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output.shp'
output_file = r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output_店铺.shp'

# 读取Shapefile文件
gdf = gpd.read_file(input_file)

# 选择 name 列中包含 "店铺"、"咖啡" 或 "购物" 的行

filtered_gdf = gdf[gdf['name'].str.contains('店|店', case=False)]

# 保存为新的Shapefile文件
filtered_gdf.to_file(output_file)

print(f"Data saved to {output_file}")
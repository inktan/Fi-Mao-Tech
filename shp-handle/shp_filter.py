import geopandas as gpd

# 读取原始的Shapefile
original_shp = gpd.read_file('e:\work\sv_hukejia\calculate_point\浙江行政境界高分\行政境界-乡镇-面.shp')

# 筛选出FNAME列中包含"街道"的行
filtered_shp = original_shp[original_shp['FNAME'].str.contains("街道", na=False)]

# 保存筛选后的数据为新的Shapefile
filtered_shp.to_file('e:\work\sv_hukejia\calculate_point\浙江行政境界高分\行政境界-乡镇-面_街道.shp')

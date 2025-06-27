import geopandas as gpd

# 指定要查看的Shapefile路径
shp_file = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_with_avg\拉萨市_with_avg.shp"  # 请替换为实际路径

# 读取Shapefile
gdf = gpd.read_file(shp_file)

# 找出所有avg_开头的列，排除avg_lon和avg_lat
avg_columns = [col for col in gdf.columns 
               if col.startswith('avg_') 
               and col not in ['avg_lon', 'avg_lat']]

# 输出前5行（不包含几何列）
print("\n前5行数据（不包含几何列）：")
print(gdf[avg_columns].shape)
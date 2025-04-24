# import geopandas as gpd
# from shapely.geometry import Polygon

# # 读取点Shapefile
# point_shp = r'e:\work\sv_shushu\20250423\all_points_Spatial_Balance.shp'
# gdf = gpd.read_file(point_shp)

# # 检查是否有足够的点生成多边形(至少需要3个点)
# if len(gdf) < 3:
#     raise ValueError("至少需要3个点才能生成多边形")

# # 生成凸包(Convex Hull)
# convex_hull = gdf.unary_union.convex_hull

# # 创建包含凸包的GeoDataFrame
# hull_gdf = gpd.GeoDataFrame(geometry=[convex_hull], crs=gdf.crs)

# # 保存为新的Shapefile
# output_shp = r'e:\work\sv_shushu\20250423\all_points_convex_hull.shp'
# hull_gdf.to_file(output_shp)
# print(f"凸包已保存至: {output_shp}")

import geopandas as gpd

# 读取点Shapefile
point_shp = r'e:\work\sv_shushu\20250423\all_points_Spatial_Balance.shp'
gdf = gpd.read_file(point_shp)

# 生成最小外接矩形
min_rect = gdf.unary_union.minimum_rotated_rectangle

# 创建包含矩形的GeoDataFrame
rect_gdf = gpd.GeoDataFrame(geometry=[min_rect], crs=gdf.crs)

# 保存为新的Shapefile
output_shp = r'e:\work\sv_shushu\20250423\all_points_convex_hull.shp'

rect_gdf.to_file(output_shp)
print(f"最小外接矩形已保存至: {output_shp}")
import geopandas as gpd
import pandas as pd

# 加载 SHP 文件
polygon_file = r"e:\work\sv_lvmaoshuiguai\fanwei02.shp"  # Polygon SHP 文件路径
other_file = r"f:\立方数据\2025年道路数据\【立方数据学社】西安市\西安市.shp"      # 另一个 SHP 文件路径
other_file = r"e:\work\sv_lvmaoshuiguai\road_zhonglou_15m_.shp"      # 另一个 SHP 文件路径

polygon_gdf = gpd.read_file(polygon_file)
other_gdf = gpd.read_file(other_file)

# 检查空间参考系统
# if polygon_gdf.crs != other_gdf.crs:
#     other_gdf = other_gdf.to_crs(polygon_gdf.crs)

# 创建新的 GeoDataFrame 来存储结果
result_gdf = gpd.GeoDataFrame(columns=other_gdf.columns)
# result_gdf = pd.DataFrame()

# 遍历 other_gdf 中的每个几何元素
for index, row in other_gdf.iterrows():
    # 检查几何元素是否完全包含在 Polygon 中或与之相交
    if row.geometry.within(polygon_gdf.geometry.iloc[0]) or row.geometry.intersects(polygon_gdf.geometry.iloc[0]):
        # 如果是，将几何元素添加到结果 GeoDataFrame 中
        result_gdf = result_gdf._append(row, ignore_index=True)

print(result_gdf.shape)
result_gdf = result_gdf.set_crs("EPSG:4326")

# 保存结果为新的 SHP 文件（可选）
# result_gdf.to_file( r"e:\work\sv_lvmaoshuiguai\road_zhonglou.shp")
result_gdf.to_file( r"e:\work\sv_lvmaoshuiguai\result_15m.shp")
result_gdf.to_csv( r"e:\work\sv_lvmaoshuiguai\result_15m.csv")

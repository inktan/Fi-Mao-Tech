import geopandas as gpd
from shapely.geometry import Polygon, Point
from coord_convert import transform  # 需要安装coord_convert库

# 1. 定义GCJ-02坐标并转换为WGS84
gcj_coords = [
    (114.253918,30.613739),
    (114.328707,30.638645),
    (114.332882,30.63738),
    (114.359738,30.618792),
    (114.38031,30.583506),
    (114.35583,30.544722),
    (114.358154,30.549498),
    (114.355011,30.546746),
    (114.354158,30.544296),
    (114.35847,30.536115),
    (114.35847,30.536115),
    (114.34833,30.50923),
    (114.338824,30.510823),
    (114.333597,30.515239),
    (114.302415,30.525944),
    (114.294915,30.524804),
    (114.271081,30.536712),
    (114.252411,30.536336),
    (114.240503,30.547847),
    (114.237167,30.549599),
    (114.250022,30.569959),
    (114.251125,30.58364),
    (114.249253,30.591624),
    (114.253732,30.605819),
    (114.249283,30.613062)
]

# 转换坐标
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in gcj_coords]
polygon = Polygon(wgs_coords)

# 2. 创建GeoDataFrame表示多边形（用于可视化检查）
polygon_gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")

# 3. 读取点数据
point_gdf = gpd.read_file(r"f:\地学大数据\2024POI\2024华中地图poi\湖北省\武汉市POI数据.shp")  # 替换为你的点文件路径

# 确保使用相同坐标系
if point_gdf.crs != polygon_gdf.crs:
    point_gdf = point_gdf.to_crs(polygon_gdf.crs)

# 4. 空间查询
points_in_polygon = point_gdf[point_gdf.geometry.within(polygon)]

# 4. 保存结果
# (1) 保存为新的 Shapefile
points_in_polygon.to_file(r"e:\work\sv_xiufenganning\road\pois.shp")

# (2) 保存为 CSV 文件（不含几何列）
# 先复制一份数据，删除几何列
csv_data = points_in_polygon.drop(columns=['geometry'])
csv_data.to_csv(r"e:\work\sv_xiufenganning\road\pois.csv", index=False)

print("处理完成！")
print(f"找到 {len(points_in_polygon)} 个落在面内的点。")
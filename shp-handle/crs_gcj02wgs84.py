import geopandas as gpd
from shapely.geometry import Point
from coord_convert.transform import gcj2wgs,wgs2gcj  # 确保已安装 coord_convert

# 1. 读取原始 shp 文件
input_shp = r"e:\work\sv_xiufenganning\road\_network.shp"  # 替换为你的输入文件路径
gdf = gpd.read_file(input_shp)

# 2. 检查列名是否正确（假设经纬度列是 'Longitude' 和 'Latitude_Y'）
if 'Longitude' not in gdf.columns or 'Latitude_Y' not in gdf.columns:
    raise ValueError("列名 'Longitude' 或 'Latitude_Y' 不存在！")

# 3. 坐标转换（GCJ-02 → WGS84）并生成新几何
wgs_points = []
for _, row in gdf.iterrows():
    lon_gcj, lat_gcj = row['Longitude'], row['Latitude_Y']
    # lon_wgs, lat_wgs = gcj2wgs(lon_gcj, lat_gcj)  # 调用转换函数
    lon_wgs, lat_wgs = wgs2gcj(lon_gcj, lat_gcj)  # 调用转换函数
    wgs_points.append(Point(lon_wgs, lat_wgs))

# 4. 创建新的 GeoDataFrame
gdf_wgs = gpd.GeoDataFrame(
    gdf.drop(columns=['geometry']),  # 保留其他属性列
    geometry=wgs_points,
    crs="EPSG:4326"  # WGS84 坐标系
)

# 5. 保存为新的 shp 文件
output_shp = r"e:\work\sv_xiufenganning\road\_network_gcj02.shp"
gdf_wgs.to_file(output_shp, encoding='utf-8')

print(f"转换完成，结果已保存到 {output_shp}")
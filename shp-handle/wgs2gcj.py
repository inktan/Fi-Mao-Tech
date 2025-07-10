import geopandas as gpd
from coord_convert.transform import wgs2gcj

# 1. 读取原始 Shapefile 文件
input_path = r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data.shp'
gdf = gpd.read_file(input_path)

# 2. 检查是否为点数据（如果不是，需要调整）
if gdf.geom_type[0] != 'Point':
    raise ValueError("该 Shapefile 不是点数据，请确保输入的是点图层")

# 3. 遍历每个点，转换坐标（GCJ-02 → WGS-84）
def convert_gcj02_to_wgs84(geom):
    # 获取原始坐标（GCJ-02）
    x, y = geom.x, geom.y
    # 转换为 WGS-84
    wgs_lon, wgs_lat = wgs2gcj(x, y)
    # 返回新的点
    return gpd.points_from_xy([wgs_lon], [wgs_lat])[0]

# 应用坐标转换
gdf['geometry'] = gdf['geometry'].apply(convert_gcj02_to_wgs84)

# 4. 保存为新的 Shapefile
output_path = r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj.shp'
gdf.to_file(output_path, encoding='utf-8')

print(f"转换完成，已保存为: {output_path}")
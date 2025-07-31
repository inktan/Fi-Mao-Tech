import json
import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer

def match_shp_to_json(shp_path, json_path, output_json_path):
    # 1. 读取SHP文件
    print("正在读取SHP文件...")
    gdf = gpd.read_file(shp_path)
    
    # 确保SHP文件是WGS84坐标系
    if gdf.crs != CRS('EPSG:4326'):
        print("警告：SHP文件不是WGS84坐标系，将自动转换...")
        gdf = gdf.to_crs('EPSG:4326')
    
    # 2. 读取JSON文件
    print("正在读取JSON文件...")
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 3. 准备坐标转换器（用于计算精确距离）
    transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True)
    
    # 4. 遍历JSON数据，查找匹配的SHP点
    print("开始匹配坐标点...")
    matched_count = 0
    
    # 初始化结果列表
    result = []
    
    for item in json_data:
        if 'lon_lat' in item and item['lon_lat'] and 'wgs84' in item['lon_lat']:
            json_lon = item['lon_lat']['wgs84']['lon']
            json_lat = item['lon_lat']['wgs84']['lat']
            
            # 转换为Web墨卡托投影计算精确距离
            x1, y1 = transformer.transform(json_lon, json_lat)

            # 在SHP文件中查找距离小于10米的点
            for idx, row in gdf.iterrows():
                shp_point = row.geometry
                # 转换为Web墨卡托计算精确距离（米）
                x2, y2 = transformer.transform(shp_point.x, shp_point.y)
                distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                if distance < 1:
                    if 'no' in row:
                        item['no'] = str(row['no'])  # 添加no字段到JSON
                        item['distance'] = distance  # 添加距离字段（单位：米）
                        matched_count += 1
                        result.append(item)
                        break  # 找到第一个匹配的点就停止
    
    # 5. 保存更新后的JSON文件
    print(f"匹配完成，共找到 {matched_count} 个匹配点")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"结果已保存到: {output_json_path}")
    return json_data

# 使用示例
shp_path = r'E:\work\sv_xiufenganning\地理数据\Export_Output_wgs84.shp'
json_path = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(1).json'  # 输入的JSON文件路径
output_json_path = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(2).json'  # 输出的JSON文件路径

result = match_shp_to_json(shp_path, json_path, output_json_path)
print("处理完成！")
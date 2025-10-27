import json
import geopandas as gpd
from shapely.geometry import Polygon
import os

def json_to_shp(json_file_path, output_shp_path):
    """
    将包含Polygon几何信息的JSON文件转换为Shapefile
    
    Parameters:
    json_file_path: JSON文件路径
    output_shp_path: 输出的Shapefile路径
    """
    
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 存储几何图形和属性
    geometries = []
    properties = []
    
    # 遍历每个要素
    for feature in data:
        if feature.get('type') == 'Feature':
            geometry_data = feature.get('geometry', {})
            
            # 检查是否为Polygon类型
            if geometry_data.get('type') == 'Polygon':
                coordinates = geometry_data.get('coordinates', [])
                
                # 处理Polygon坐标（可能有外环和内环）
                if coordinates:
                    # 外环坐标
                    exterior_coords = coordinates[0]
                    
                    # 创建Polygon对象
                    polygon = Polygon(exterior_coords)
                    
                    # 添加到几何列表
                    geometries.append(polygon)
                    
                    # 提取属性（排除几何信息）
                    props = {key: value for key, value in feature.items() 
                            if key not in ['geometry', 'type']}
                    properties.append(props)
    
    # 创建GeoDataFrame
    gdf = gpd.GeoDataFrame(properties, geometry=geometries)
    
    # 设置坐标系（这里假设是WGS84，根据你的数据调整）
    gdf.crs = 'EPSG:4326'
    
    # 保存为Shapefile
    gdf.to_file(output_shp_path, encoding='utf-8')
    
    print(f"成功转换 {len(geometries)} 个Polygon到Shapefile: {output_shp_path}")
    return gdf

# 使用示例
if __name__ == "__main__":
    # 输入和输出文件路径
    json_file = r"e:\work\sv_lixiang\temp.json"  # 替换为你的JSON文件路径
    output_shp = r"e:\work\sv_lixiang\temp_polygons.shp"  # 输出的Shapefile路径
    
    # 执行转换
    gdf = json_to_shp(json_file, output_shp)
    
    # 打印结果信息
    print(f"转换后的数据信息:")
    print(f"要素数量: {len(gdf)}")
    print(f"坐标系: {gdf.crs}")
    print(f"字段: {list(gdf.columns)}")
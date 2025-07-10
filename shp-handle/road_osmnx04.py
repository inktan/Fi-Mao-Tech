import geopandas as gpd
import osmnx as ox
import os
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import time
import pandas as pd

# 设置OSMnx配置
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 600  # 增加超时时间

def process_individual_polygons(input_shp, output_dir=None, network_type='all'):
    """
    为SHP文件中的每个多边形单独获取路网并保存
    
    参数:
        input_shp: 输入SHP文件路径
        output_dir: 输出目录(默认为输入文件所在目录)
        network_type: 路网类型 ('all', 'drive', 'walk', 'bike')
    """
    # 1. 读取SHP文件
    gdf = gpd.read_file(input_shp)
    
    # 2. 确保是WGS84坐标系
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # 3. 检查几何类型
    if not all(gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])):
        raise ValueError("输入SHP文件必须只包含多边形要素")
    
    # 4. 设置输出目录
    if output_dir is None:
        output_dir = os.path.dirname(input_shp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 5. 创建结果DataFrame用于汇总
    results = []
    
    # 6. 处理每个多边形
    for idx, row in gdf.iterrows():
        start_time = time.time()
        polygon = row.geometry
        
        # 为每个多边形创建基本文件名
        base_name = os.path.splitext(os.path.basename(input_shp))[0]
        output_shp = os.path.join(output_dir, f"{base_name}_polygon_{idx}_netroad.shp")
        
        try:
            # 获取路网数据
            print(f"\n正在处理多边形 {idx}...")
            G = ox.graph_from_polygon(polygon, network_type=network_type)
            
            # 转换为GeoDataFrame
            gdf_edges = ox.graph_to_gdfs(G, nodes=False)
            
            # 确保有有效的几何图形
            gdf_edges = gdf_edges[gdf_edges.geometry.notnull()]
            
            # 保存结果
            gdf_edges.to_file(output_shp, encoding='utf-8')
            
            # 记录处理结果
            processing_time = time.time() - start_time
            road_count = len(gdf_edges)
            results.append({
                'polygon_id': idx,
                'road_count': road_count,
                'processing_time': processing_time,
                'output_file': output_shp,
                'status': 'success'
            })
            
            print(f"成功保存多边形 {idx} 的路网数据到: {output_shp}")
            print(f"包含 {road_count} 条道路，处理时间: {processing_time:.2f}秒")
            
        except Exception as e:
            processing_time = time.time() - start_time
            results.append({
                'polygon_id': idx,
                'road_count': 0,
                'processing_time': processing_time,
                'output_file': '',
                'status': f'failed: {str(e)}'
            })
            print(f"处理多边形 {idx} 时出错: {e}")
            print(f"处理多边形 {idx} 时出错: {e}")
    
    # 7. 保存处理结果汇总
    results_df = pd.DataFrame(results)
    summary_file = os.path.join(output_dir, f"{base_name}_processing_summary.csv")
    results_df.to_csv(summary_file, index=False)
    print(f"\n处理完成! 结果汇总已保存到: {summary_file}")
    
    return results_df

# 使用示例
input_shp = r"e:\work\sv_xiufenganning\地理数据\circles_500m.shp"
output_dir = r"e:\work\sv_xiufenganning\地理数据\individual_road_networks"  # 可选自定义输出目录

# 处理多边形
results = process_individual_polygons(input_shp, output_dir, network_type='all')

# 显示前几个处理结果
print("\n处理结果摘要:")
print(results.head())
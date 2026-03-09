import pandas as pd
import matplotlib.pyplot as plt
import osmnx as ox
from shapely import wkt
from coord_convert import transform
from shapely.geometry import Polygon

# 假设你的坐标转换工具类如下 (如果没有，请确保 transform.py 在路径中)
# import transform 

def process_polygon_and_download_osm(csv_path, output_shp):
    # 1. 读取 CSV 文件
    df = pd.read_csv(csv_path)
    
    # 假设 WKT 数据在名为 'WKT' 的列中，取第一行作为示例
    wkt_string = df['WKT'].iloc[0]
    
    # 2. 解析 WKT 字符串为 Shapely Polygon 对象
    # 这步会自动处理 "POLYGON ((...))" 这种格式
    poly_gcj = wkt.loads(wkt_string)
    
    # 3. 提取 GCJ-02 坐标并转换为 WGS84
    # poly_gcj.exterior.coords 包含了多边形的所有外轮廓点
    gcj_coords = list(poly_gcj.exterior.coords)
    
    # 使用你提供的转换逻辑 (transform.gcj2wgs)
    # 注意：通常 gcj2wgs 接收 (lng, lat)
    wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in gcj_coords]
    
    # 4. 重新构建 WGS84 坐标系下的 Polygon
    polygon_wgs = Polygon(wgs_coords)
    
    # 5. 可视化检查
    fig, ax = plt.subplots(figsize=(10, 8))
    x, y = polygon_wgs.exterior.xy
    ax.fill(x, y, alpha=0.5, fc='blue', ec='black')
    ax.set_title('Polygon in WGS84 (Ready for OSMnx)')
    plt.grid(True)
    plt.show()

    # 6. 使用 OSMnx 下载路网
    print("正在从 OpenStreetMap 下载路网数据...")
    # 注意：OSMnx 的 polygon 参数需要是标准的 shapely Polygon
    G = ox.graph_from_polygon(polygon_wgs, network_type='all')

    # 7. 转换为 GeoDataFrame 并保存为 Shapefile
    gdf = ox.graph_to_gdfs(G, nodes=False)
    
    # 确保路径存在
    gdf.to_file(output_shp, encoding='utf-8')
    print(f"路网已成功保存至: {output_shp}")

# --- 执行 ---
csv_file = r'e:\work\sv_zhoujunling\20260209\guoa.csv'  # 替换为你的文件名
output_path = r'e:\work\sv_zhoujunling\20260209\guoa_network.shp'  
process_polygon_and_download_osm(csv_file, output_path)
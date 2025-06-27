import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon, box
from coord_convert import transform
import matplotlib.pyplot as plt
import math
import time
import os
import pandas as pd

# 设置OSMnx配置
ox.settings.log_console = True
ox.settings.timeout = 180
ox.settings.memory = None

# 原始坐标数据
coords = [
    (121.60804101666092, 25.677880782832283),
    (122.24524805480884, 24.992740711895404),
    (122.2946865319065, 23.75690225193834),
    (122.57483790212672, 21.516155541624226),
    (119.61402244038776, 21.41902614669051),
    (118.72412985262947, 23.32885035806267),
    (119.1416103258988, 24.388839341659345),
    (120.71265526478068, 25.618457785948305),
]

# 坐标转换
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]
polygon = Polygon(wgs_coords)

# 可视化函数
def visualize_polygon_with_subdivisions(main_poly, sub_polygons):
    """可视化主多边形和所有子区域"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制主多边形
    x, y = main_poly.exterior.xy
    ax.fill(x, y, alpha=0.2, fc='blue', ec='black', label='Main Polygon')
    
    # 绘制所有子区域
    for i, sub_poly in enumerate(sub_polygons):
        if hasattr(sub_poly, 'exterior'):
            x, y = sub_poly.exterior.xy
            ax.plot(x, y, 'r-', linewidth=0.8)
            ax.fill(x, y, alpha=0.1, fc='red')
            
            # 在每个子区域中心添加编号
            centroid = sub_poly.centroid
            ax.text(centroid.x, centroid.y, str(i), 
                   fontsize=8, ha='center', va='center', color='darkred')
    
    ax.set_title(f'Polygon Subdivision ({len(sub_polygons)} sub-areas)')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 划分多边形为子区域
def split_polygon(poly, n_splits=5):
    """将多边形划分为n_splits x n_splits个小矩形"""
    minx, miny, maxx, maxy = poly.bounds
    width = (maxx - minx) / n_splits
    height = (maxy - miny) / n_splits
    
    sub_polygons = []
    for i in range(n_splits):
        for j in range(n_splits):
            left = minx + i * width
            right = minx + (i + 1) * width
            bottom = miny + j * height
            top = miny + (j + 1) * height
            
            sub_poly = box(left, bottom, right, top)
            intersection = sub_poly.intersection(poly)
            if not intersection.is_empty:
                sub_polygons.append(intersection)
                # sub_polygons.append(sub_poly)
    return sub_polygons

# 划分并可视化
sub_polygons = split_polygon(polygon, n_splits=5)
visualize_polygon_with_subdivisions(polygon, sub_polygons)

# 下载和保存数据
output_dir = r"E:\work\sv_zoudaobuhuang\roads"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

all_gdfs = []
for i, sub_poly in enumerate(sub_polygons):
    print(f"\nProcessing sub-polygon {i+1}/{len(sub_polygons)} (Area {i})...")
    print(f"Bounds: {sub_poly.bounds}")
    
    try:
        # 可视化当前处理的小区域
        # fig, ax = plt.subplots(figsize=(8, 6))
        # x_main, y_main = polygon.exterior.xy
        # ax.fill(x_main, y_main, alpha=0.1, fc='blue', ec='black')
        
        # if hasattr(sub_poly, 'exterior'):
        #     x_sub, y_sub = sub_poly.exterior.xy
        #     ax.fill(x_sub, y_sub, alpha=0.5, fc='red', ec='darkred')
        #     ax.set_title(f'Downloading Area {i} (Part {i+1}/{len(sub_polygons)})')
        #     ax.set_xlabel('Longitude')
        #     ax.set_ylabel('Latitude')
        #     plt.grid(True)
        #     plt.tight_layout()
        #     plt.show()
        
        # 下载数据
        G = ox.graph_from_polygon(
            sub_poly,
            network_type='all',
            simplify=True,
            retain_all=False,
            truncate_by_edge=True
        )
        
        # 转换为GeoDataFrame并保存
        gdf = ox.graph_to_gdfs(G, nodes=False)
        temp_path = os.path.join(output_dir, f"_network_part_{i}.shp")
        gdf.to_file(temp_path)
        print(f"Saved part {i} to {temp_path}")
        all_gdfs.append(gdf)
        
        # 清理内存
        del G, gdf
        
    except Exception as e:
        print(f"Error processing sub-polygon {i}: {str(e)}")
        continue
    
    time.sleep(5)

# 合并结果（可选）
if all_gdfs:
    final_gdf = gpd.GeoDataFrame(pd.concat(all_gdfs, ignore_index=True))
    final_path = os.path.join(output_dir, "_network_merged.shp")
    final_gdf.to_file(final_path)
    print(f"\nMerged file saved to {final_path}")
    
    # 可视化最终结果
    fig, ax = plt.subplots(figsize=(12, 10))
    final_gdf.plot(ax=ax, color='blue', linewidth=0.5, alpha=0.7)
    ax.set_title('Final Merged Road Network')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
else:
    print("\nNo data was downloaded.")
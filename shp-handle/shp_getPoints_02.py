import geopandas as gpd
import pandas as pd
import numpy as np
import os
import glob
from shapely.geometry import LineString, Point, MultiLineString, MultiPolygon, Polygon
from tqdm import tqdm
from scipy.spatial import cKDTree
from multiprocessing import Pool, cpu_count

# 设置 tqdm 配合 pandas
tqdm.pandas()

def extract_points_vectorized(line, interval):
    """
    使用投影坐标系下的欧氏距离进行快速插值
    """
    # 按照 interval 距离进行插值取点
    distances = np.arange(0, line.length, interval)
    points = [line.interpolate(distance) for distance in distances]
    
    # 确保终点被包含
    if line.coords:
        points.append(Point(line.coords[-1]))
    return points

def process_geometry_optimized(args):
    """
    多进程包装函数
    """
    row_data, interval = args
    geom = row_data['geometry']
    idx = row_data['name']
    
    if geom is None or geom.is_empty:
        return []

    points = []
    # 统一处理各种几何类型
    if isinstance(geom, (LineString,)):
        points = extract_points_vectorized(geom, interval)
    elif isinstance(geom, (MultiLineString,)):
        for part in geom.geoms:
            points.extend(extract_points_vectorized(part, interval))
    elif isinstance(geom, (Polygon,)):
        points = extract_points_vectorized(geom.exterior, interval)
    elif isinstance(geom, (MultiPolygon,)):
        for part in geom.geoms:
            points.extend(extract_points_vectorized(part.exterior, interval))
    elif isinstance(geom, Point):
        points = [geom]

    return [(idx, p.x, p.y) for p in points]

def process_shapefile(file_path, interval):
    try:
        print(f"\n开始处理文件: {os.path.basename(file_path)}")

        # --- 步骤 1: 读取与投影转换 ---
        print("--> 步骤 1/5: 读取文件与坐标转换...")
        gdf = gpd.read_file(file_path)
        if gdf.empty:
            print("警告: 文件为空，跳过处理。")
            return

        utm_crs = gdf.estimate_utm_crs()
        gdf_utm = gdf.to_crs(utm_crs)
        print("     坐标转换完成。")

        # --- 步骤 2: 并行提取点位 ---
        print(f"--> 步骤 2/5: 使用 {cpu_count() - 1} 核心并行提取点位...")
        data_list = [{'geometry': row.geometry, 'name': idx} for idx, row in gdf_utm.iterrows()]
        
        # 预留一个核心给系统，防止卡死
        num_processes = max(1, cpu_count() - 1)
        with Pool(processes=num_processes) as pool:
            results_nested = list(tqdm(
                pool.imap(process_geometry_optimized, [(d, interval) for d in data_list]),
                total=len(data_list),
                desc="     提取进度"
            ))
        
        results = [item for sublist in results_nested for item in sublist]
        if not results:
            print("警告: 未能从文件中提取任何点位。")
            return
        print("     点位提取完成。")

        # --- 步骤 3: 构造 GeoDataFrame ---
        print("--> 步骤 3/5: 构造 GeoDataFrame 并转换坐标...")
        points_df = pd.DataFrame(results, columns=['osm_id', 'x_utm', 'y_utm'])
        
        temp_gdf = gpd.GeoDataFrame(
            points_df,
            geometry=gpd.points_from_xy(points_df.x_utm, points_df.y_utm, crs=utm_crs)
        ).to_crs("EPSG:4326")
        
        temp_gdf['longitude'] = temp_gdf.geometry.x
        temp_gdf['latitude'] = temp_gdf.geometry.y
        print(f"     初步生成点数: {len(temp_gdf)}")
        
        # 经纬度去重
        temp_gdf.drop_duplicates(subset=['longitude', 'latitude'], inplace=True)
        print(f"     经纬度去重后点数: {len(temp_gdf)}")

        # --- 步骤 4: 高效空间去重 (分块处理) ---
        print("--> 步骤 4/5: 执行高效空间去重...")
        
        # 复用经纬度坐标进行去重，因为UTM坐标在分块处理中不再直接使用
        coords = np.array(temp_gdf[['longitude', 'latitude']].values)
        
        # 检查是否有足够的点进行去重
        if len(coords) < 2:
            print("     点数过少，跳过空间去重。")
            final_gdf = temp_gdf.copy()
        else:
            tree = cKDTree(coords)
            print("     空间索引构建完成。")

            to_remove = set()
            # 设定一个合理的区块大小，以平衡内存和处理速度
            chunk_size = 50000  
            num_chunks = int(np.ceil(len(coords) / chunk_size))

            print(f"     开始分块筛选重叠点（共 {num_chunks} 块）...")

            for i in tqdm(range(num_chunks), desc="     分块处理进度"):
                start_index = i * chunk_size
                end_index = min((i + 1) * chunk_size, len(coords))
                
                # 只查询当前区块内点的邻居
                # 注意：这里的半径 r 需要根据经纬度单位进行调整，这是一个近似值
                # 50米约等于0.00045度
                radius_in_degrees = interval / 111111  # 简化转换
                
                indices_in_chunk = tree.query_ball_point(coords[start_index:end_index], r=radius_in_degrees * 0.9)
                
                # 处理当前区块的查询结果
                for j, neighbors in enumerate(indices_in_chunk):
                    current_point_index = start_index + j
                    if current_point_index in to_remove:
                        continue
                    
                    # 将所有索引比当前点大的邻居加入待移除集合
                    # 这是为了保证每个近邻点集群中只保留索引最小的那个点
                    for neighbor_idx in neighbors:
                        if neighbor_idx > current_point_index:
                            to_remove.add(neighbor_idx)
            
            # 从所有索引中移除被标记的点
            all_indices = set(range(len(coords)))
            final_indices = sorted(list(all_indices - to_remove))
            final_gdf = temp_gdf.iloc[final_indices].copy()
        
        print(f"     空间去重后点数: {len(final_gdf)}")

        # --- 步骤 5: 保存结果 ---
        print("--> 步骤 5/5: 保存结果...")
        output_basename = file_path.replace('.shp', f'_{interval}m_Optimized')
        
        # 保存为 CSV
        csv_path = f"{output_basename}.csv"
        final_gdf.drop(columns=['geometry', 'x_utm', 'y_utm']).to_csv(csv_path, index=False)
        print(f"     已保存 CSV 文件: {csv_path}")
        
        # 保存为 SHP
        shp_path = f"{output_basename}.shp"
        # GeoPandas 要求 geometry 列存在才能保存为 shapefile
        final_gdf_for_shp = final_gdf[['osm_id', 'longitude', 'latitude', 'geometry']].copy()
        final_gdf_for_shp.to_file(shp_path, driver='ESRI Shapefile', encoding='utf-8')
        print(f"     已保存 SHP 文件: {shp_path}")

        print(f"处理完成! 最终点数: {len(final_gdf)}")

    except Exception as e:
        print(f"处理文件 {os.path.basename(file_path)} 时发生错误: {e}")

def main():
    folder_path = r'F:\大数据\2025年8月份道路矢量数据\Japan'
    shape_files = glob.glob(os.path.join(folder_path, '*.shp'))
    
    shape_files.append(r'f:\大数据\2025年8月份道路矢量数据\north-korea-260227-free.shp\gis_osm_roads_free_1.shp')
    shape_files.append(r'f:\大数据\2025年8月份道路矢量数据\south-korea-260227-free.shp\gis_osm_roads_free_1.shp')

    interval = 50

    for file_path in shape_files:
        process_shapefile(file_path, interval)

if __name__ == '__main__':
    main()








    
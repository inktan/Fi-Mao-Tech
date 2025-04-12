import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
import pyproj
from tqdm import tqdm  # 用于进度条显示

def process_points(input_shp, output_shp, min_dist=0.1, max_dist=49):
    """
    处理点数据，删除距离其他点在0.1m到50m之间的点
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
        min_dist: 最小距离阈值(米)
        max_dist: 最大距离阈值(米)
    """
    # 1. 读取数据
    print("正在读取数据...")
    gdf = gpd.read_file(input_shp)
    
    # 确保是WGS84 (EPSG:4326)坐标系
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # 2. 将经纬度转换为平面坐标(UTM)以便精确计算距离
    print("坐标转换中...")
    centroid = gdf.geometry.unary_union.centroid if hasattr(gdf.geometry, 'unary_union') else gdf.geometry.union_all().centroid
    utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
    utm_crs = f'EPSG:{32600 + utm_zone}' if centroid.y >= 0 else f'EPSG:{32700 + utm_zone}'
    
    # 转换为UTM坐标
    gdf_utm = gdf.to_crs(utm_crs)
    
    # 3. 使用KDTree进行高效空间查询
    print("构建空间索引...")
    coords = np.array([(geom.x, geom.y) for geom in gdf_utm.geometry])
    tree = cKDTree(coords)
    
    # 4. 找出需要删除的点
    print("查找邻近点...")
    to_remove = set()
    
    # 使用批量查询提高性能
    batch_size = 10000  # 根据内存调整
    for i in tqdm(range(0, len(coords), batch_size), desc="处理进度"):
        batch_indices = range(i, min(i + batch_size, len(coords)))
        # 查询所有点对，距离在max_dist以内的
        neighbors = tree.query_ball_point(coords[batch_indices], r=max_dist, return_sorted=True)
        
        for idx, neighbors_list in zip(batch_indices, neighbors):
            # 跳过已经标记要删除的点
            if idx in to_remove:
                continue
                
            # 检查每个邻居
            for j in neighbors_list:
                if j <= idx:  # 避免重复检查
                    continue
                    
                dist = np.linalg.norm(coords[idx] - coords[j])
                if min_dist < dist < max_dist:
                    # 删除其中一个点(这里选择删除索引较大的)
                    to_remove.add(j)
    
    # 5. 创建过滤后的GeoDataFrame
    print("创建结果数据集...")
    mask = [i not in to_remove for i in range(len(gdf))]
    filtered_gdf = gdf[mask]
    
    # 6. 保存结果
    print("保存结果...")
    filtered_gdf.to_file(output_shp)
    
    print(f"处理完成 - 原始点数: {len(gdf)}, 处理后点数: {len(filtered_gdf)}, 删除点数: {len(to_remove)}")

# 使用示例
if __name__ == "__main__":

    input_shp = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_.shp'  # Replace with your shapefile path
    output_shp = input_shp.replace('.shp', '0m_01.shp')

    process_points(input_shp, output_shp)
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from scipy.spatial import cKDTree
import pyproj

def process_points(input_shp, output_shp, min_dist=0.1, max_dist=50):
    """
    处理点数据，删除距离其他点在0.1m到50m之间的点
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
        min_dist: 最小距离阈值(米)
        max_dist: 最大距离阈值(米)
    """
    # 1. 读取数据
    gdf = gpd.read_file(input_shp)
    
    # 确保是WGS84 (EPSG:4326)坐标系
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # 2. 将经纬度转换为平面坐标(UTM)以便精确计算距离
    # 自动确定合适的UTM区域
    centroid = gdf.geometry.unary_union.centroid
    utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
    utm_crs = f'EPSG:{32600 + utm_zone}' if centroid.y >= 0 else f'EPSG:{32700 + utm_zone}'
    
    # 转换为UTM坐标
    gdf_utm = gdf.to_crs(utm_crs)
    
    # 3. 使用KDTree进行高效空间查询
    coords = np.array([(geom.x, geom.y) for geom in gdf_utm.geometry])
    tree = cKDTree(coords)
    
    # 4. 找出需要删除的点
    to_remove = set()
    
    # 查询所有点对，距离在max_dist以内的
    pairs = tree.query_pairs(max_dist, output_type='ndarray')
    
    for i, j in pairs:
        dist = np.linalg.norm(coords[i] - coords[j])
        if min_dist < dist < max_dist:
            # 随机删除其中一个点(这里选择删除索引较大的)
            to_remove.add(max(i, j))
    
    # 5. 创建过滤后的GeoDataFrame
    mask = [i not in to_remove for i in range(len(gdf))]
    filtered_gdf = gdf[mask]
    
    # 6. 保存结果
    filtered_gdf.to_file(output_shp)
    
    print(f"原始点数: {len(gdf)}, 处理后点数: {len(filtered_gdf)}, 删除点数: {len(to_remove)}")

# 使用示例

input_shp = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_.shp'  # Replace with your shapefile path
output_shp = input_shp.replace('.shp', '0m_02.shp')

process_points(input_shp, output_shp)
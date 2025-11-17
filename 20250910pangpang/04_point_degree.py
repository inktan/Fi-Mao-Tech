import geopandas as gpd
import numpy as np
from math import atan2, degrees, sin, cos, sqrt, radians
from scipy.spatial import cKDTree
from pathlib import Path
import csv
from tqdm import tqdm

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    计算两个经纬度坐标之间的大圆距离（米）
    """
    # 将角度转换为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # 地球半径（米）
    return c * 6371000

def calculate_angle(base_point, target_point):
    """
    计算目标点相对于基准点的角度（0-360度）
    """
    dx = target_point.x - base_point.x
    dy = target_point.y - base_point.y
    
    angle_rad = atan2(dx, dy)
    angle_deg = degrees(angle_rad)
    
    return angle_deg if angle_deg >= 0 else angle_deg + 360

def create_circular_range(number, range_size=20):
    """
    在0-360的圆形区间内，以number为中心创建前后加减range_size的区间
    
    Args:
        number: 中心数字
        range_size: 区间大小（前后各加减多少）
    
    Returns:
        tuple: (start, end) 区间边界
    """
    # 确保数字在0-360范围内
    number = number % 360
    
    # 计算区间边界
    start = (number - range_size) % 360
    end = (number + range_size) % 360
    
    return start, end

def is_in_circular_range(test_number, range_start, range_end):
    """
    判断数字是否在圆形区间内
    
    Args:
        test_number: 要测试的数字
        range_start: 区间起始
        range_end: 区间结束
    
    Returns:
        bool: 是否在区间内
    """
    test_number = test_number % 360
    
    if range_start <= range_end:
        # 正常区间，如 39-79
        return range_start <= test_number <= range_end
    else:
        # 跨越0点的区间，如 350-10
        return test_number >= range_start or test_number <= range_end

def find_nearest_points_with_metrics(gdf1, gdf2, k=5):
    """
    最优方案：查找最近点并计算距离（米）和角度
    """
    # 统一坐标系
    if gdf1.crs != gdf2.crs:
        gdf2 = gdf2.to_crs(gdf1.crs)

    gdf1 = gdf1.to_crs(epsg=4326)
    gdf2 = gdf2.to_crs(epsg=4326)

    # 检测坐标系类型
    is_4326 = str(gdf1.crs).upper() == 'EPSG:4326'
    print(f"坐标系: {gdf1.crs}, 使用{'大圆距离' if is_4326 else '欧几里得距离'}")
    
    # 提取坐标
    coords1 = np.array([[p.x, p.y] for p in gdf1.geometry])
    coords2 = np.array([[p.x, p.y] for p in gdf2.geometry])
    
    # 构建KD树
    tree = cKDTree(coords2)
    
    print(f"处理 {len(gdf1)} 个基准点，每个点查找 {k} 个最近点...")
    print("=" * 70)
    
    results = []
    
    for i, (idx, base_row) in tqdm(enumerate(gdf1.iterrows()),total=len(gdf1)):
        base_point = base_row.geometry
        base_lon, base_lat = base_point.x, base_point.y
        
        # KD树搜索
        distances, indices = tree.query([coords1[i]], k=min(k, len(gdf2)))
        
        nearest_points = []
        for dist, target_idx in zip(distances[0], indices[0]):
            target_point = gdf2.iloc[target_idx].geometry
            SpeciesNam = gdf2.iloc[target_idx].SpeciesNam
            CommonName = gdf2.iloc[target_idx].CommonName
            target_lon, target_lat = target_point.x, target_point.y
            
            # 计算真实距离（米）
            if is_4326:
                real_dist_m = haversine_distance(base_lon, base_lat, target_lon, target_lat)
            else:
                real_dist_m = dist
            
            # 计算角度
            angle = calculate_angle(base_point, target_point)
            
            nearest_points.append({
                'distance_m': real_dist_m,
                'angle_deg': angle,
                'target_idx': target_idx,
                'target_coords': (target_lon, target_lat),
                'SpeciesNam': SpeciesNam,
                'CommonName': CommonName,
            })
        
        # 按距离排序
        nearest_points.sort(key=lambda x: x['distance_m'])
        
        # 存储结果
        # results.append({
        #     'base_idx': idx,
        #     'base_coords': (base_lon, base_lat),
        #     'nearest_points': nearest_points
        # })
        
        # 打印进度
        print(f"\n基准点 {i+1}/{len(gdf1)} (索引:{idx}): ({base_lon:.6f}, {base_lat:.6f})")
        # for rank, point_info in enumerate(nearest_points, 1):
        #     print(f"  #距离{rank}: {point_info['distance_m']:6.2f}m, {point_info['angle_deg']:5.1f}°, "
        #           f"目标{point_info['target_idx']} ({point_info['target_coords'][0]:.6f}, {point_info['target_coords'][1]:.6f})")
        # print(nearest_points)

        path = Path(folder_path)
        # 使用列表推导式查找所有符合条件的文件夹
        folders = [f for f in path.iterdir() if f.is_dir() and f.name.startswith(f'{i}_')]
        if not folders:
            continue
        
        first_folder = folders[0]
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
        
        image_paths = []
        for file_path in first_folder.rglob('*'):  # rglob 递归查找
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_paths.append(file_path)

        # 图像计算 341 273 221
        # gis计算  318 221 197
        # 差值     23  52  24

        # result_dict = {
        #     str(path): float(path.stem.split('_')[-1])
        #     for path in image_paths
        # }
        # print(result_dict.values())
        for item in nearest_points:
            print(item['angle_deg'])

            number=item['angle_deg']
            range_size=15
            # range_size=20
            # range_size=25
            # range_size=30
            start, end = create_circular_range(number, range_size)            

            for img_path in image_paths[:k]:
                # print(f"  找到图像文件: {img_path}")
                spano_tree_degree = float(Path(img_path).stem.split('_')[-1])

                if not is_in_circular_range(spano_tree_degree, start, end):
                    # print(f"图像角度 {spano_tree_degree} 不在区间 ({start}, {end}) 内，跳过。")
                    continue

                # closest_item = min(nearest_points, key=lambda x: abs(x['angle_deg'] - spano_tree_degree))

                # print(f"目标角度: {spano_tree_degree}")
                # print(f"最接近的角度: {closest_item['angle_deg']}")
                # print(f"绝对差值: {abs(closest_item['angle_deg'] - spano_tree_degree)}")
                # print(f"找到的元素: {closest_item}")

                with open(extracted_trees_name_csv_path,'a' ,newline='') as f:
                    writer = csv.writer(f)
                    img_path = str(img_path).replace('E:\\work\\sv_pangpang\\sv_pano_20251106\\sv_google_pano\\', '')
                    writer.writerow([img_path, spano_tree_degree, item['distance_m'], item['angle_deg'], item['angle_deg'] - spano_tree_degree, item['target_idx'], item['SpeciesNam'], item['CommonName']])

def main():
    # 读取文件
    gdf1 = gpd.read_file(shp1_path)
    gdf2 = gpd.read_file(shp2_path)
    
    print(f"基准点文件: {len(gdf1)} 个点")
    print(f"目标点文件: {len(gdf2)} 个点")
    
    # 执行分析
    find_nearest_points_with_metrics(gdf1, gdf2, k=3)
    
if __name__ == "__main__":
    
    # 替换为你的文件路径
    folder_path = r'E:\work\sv_pangpang\sv_pano_20251106\sv_google_pano\extracted_trees'

    shp1_path = r"e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data_32633\CoS_GSV_30m_points.shp"  # 基准点文件
    shp2_path = r"e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data_32633\CoS_streettree_data.shp"  # 搜索点文件

    extracted_trees_name_csv_path = r'E:\work\sv_pangpang\sv_pano_20251106\sv_google_pano\extracted_trees_name_range_size_15.csv'

    with open(extracted_trees_name_csv_path,'w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['file_path','spano_tree_degree','point_tree_dis','point_tree_degree','difference_angles','tree_idx','SpeciesNam','CommonName'])

    main()

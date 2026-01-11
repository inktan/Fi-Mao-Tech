import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont 
from pyproj import CRS, Transformer
from math import atan2, degrees, sin, cos, sqrt, radians

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from scipy.spatial import cKDTree
import pandas as pd
import os

# 1. 设置路径和加载数据
csv_file = r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos_03.csv'  # 替换为你的 CSV 文件路径

# 读取 CSV 文件
df = pd.read_csv(csv_file)

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

def main(IMAGE_PATH, JSON_PATH, DEPTH_PATH, OUTPUT_PATH, tree_point_gdf):
    tree_point_gdf_coords1 = np.array([[p.x, p.y] for p in tree_point_gdf.geometry])
    tree_kdtree = cKDTree(tree_point_gdf_coords1)

    image_filename = os.path.basename(IMAGE_PATH)
    match_row = df[df['filename'] == image_filename]
    CAMERA_LON = float(match_row['lngX'].iloc[0])
    CAMERA_LAT = float(match_row['latY'].iloc[0])
    YAW_ANGLE_THETA_0_DEG = float(match_row['heading'].iloc[0])

    try:
        with Image.open(IMAGE_PATH) as img:
            W, H = img.size
    except FileNotFoundError:
        W, H = 2048, 1024 
        print(f"Warning: Image file not found at {IMAGE_PATH}. Using simulated size W={W}, H={H}.")

    try:
        with open(JSON_PATH, 'r') as f:
            detections = json.load(f)['detections']
    except FileNotFoundError:
        return
        # detections = [
        #     {'label': 'Plane tree', 'confidence': 0.95, 'bbox': [300, 450, 500, 700]}, 
        #     {'label': 'Willow', 'confidence': 0.88, 'bbox': [700, 500, 850, 750]},
        # ]
        # print("Warning: JSON file not found. Using simulated detection data.")
        
    if len(detections) == 0:
        print("No detections found in the JSON file.")
        return
    
    # print(f"图像尺寸：W={W} 像素, H={H} 像素")
    # print(f"SVI 默认航向角 (θ₀): {YAW_ANGLE_THETA_0_DEG} 度")

    def get_depth_at_pixel(depth_path, x_pixel, y_pixel, W, H):
        """
        从深度图读取指定像素的深度值。
        基于用户提供的灰度值(30-200) 到 距离(2.0-25.0米) 的反向线性关系进行优化。
        """
        G_min = 30.0
        G_max = 200.0
        D_min = 2.0
        D_max = 25.0
        G_range = G_max - G_min
        D_range = D_max - D_min
        DEFAULT_D = (D_min + D_max) / 2 

        try:
            depth_img = Image.open(depth_path).convert('L')
            if not (0 <= x_pixel < W and 0 <= y_pixel < H):
                return DEFAULT_D

            gray_value = float(depth_img.getpixel((int(x_pixel), int(y_pixel))))
            
            if gray_value <= G_min:
                depth_m = D_max
            elif gray_value >= G_max:
                depth_m = D_min
            else:
                normalized_g = (gray_value - G_min) / G_range
                depth_m = D_min + (1.0 - normalized_g) * D_range
                
            return depth_m

        except FileNotFoundError:
            return DEFAULT_D 
        except Exception:
            return DEFAULT_D 


    # ====================================================================
    # 1. 初始化 pyproj Transformer
    # WGS84 (EPSG:4326) 到 UTM Zone 50N (EPSG:32650)
    # Jinan 位于 UTM Zone 50N (东经 114° - 120°)
    # always_xy=True 确保输入顺序为 (Lon, Lat) 输出为 (Easting, Northing) 即 (x, y)
    # ====================================================================
    try:
        # 前向转换：Lon/Lat -> X/Y
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32650", always_xy=True)
        # 反向转换：X/Y -> Lon/Lat (用于将最终的 X, Y 转换回 WGS84 经纬度)
        rev_transformer = Transformer.from_crs("EPSG:32650", "EPSG:4326", always_xy=True)
        pyproj_loaded = True
    except Exception as e:
        print(f"Warning: pyproj Transformer failed to load. Ensure pyproj is installed. Error: {e}")
        pyproj_loaded = False

    def calculate_tree_parameters_FINAL(detections, depth_path, W, H, theta_0_deg, camera_lon, camera_lat):
        results = []
        # 获取相机所在的平面坐标 (x_prime, y_prime)
        x_prime, y_prime = transformer.transform(camera_lon, camera_lat) 
        
        for i, det in enumerate(detections):
            bbox = det.get('bbox', [0, 0, 0, 0]) 
            xmin, ymin, xmax, ymax = [int(val) for val in bbox]
            
            X_center = (xmin + xmax) / 2
            Z_bottom = ymax 
            Z_top = ymin
            
            # --- 步骤 1: 估计深度 D ---
            D = get_depth_at_pixel(depth_path, X_center, Z_bottom, W, H)
            
            # --- 步骤 2: 计算绝对方位角 (φ) 和平面坐标 (x, y) ---
            north_angle = (360.0 - float(theta_0_deg)) % 360.0
            # 将正北角度映射到0-360范围内的另一侧
            if north_angle <= 180:
                north_angle+=180  # 0-180映射到180-360
            else:
                north_angle-=180  # 180-360映射到0-180

            tree_degree = X_center/W * 360.0

            if tree_degree <= north_angle:
                tree_degree = tree_degree - north_angle + 360  # 0-180映射到180-360
            else:
                tree_degree-=north_angle  # 180-360映射到0-180

            phi_rad = np.deg2rad(tree_degree) 
            
            # 树木的平面坐标 (x, y)
            x = x_prime + D * np.cos(phi_rad)
            y = y_prime + D * np.sin(phi_rad)
            
            # --- 步骤 2.5: 将平面坐标 (x, y) 转换回 WGS84 经纬度 (新增) ---
            tree_lon, tree_lat = rev_transformer.transform(x, y)
            
            # --- 步骤 3 & 4: 计算树的高度 h 和直径 w (不变) ---
            Z_px, Z_prime_px = Z_bottom, Z_top 
            delta_rad = np.deg2rad(180.0 / H * (Z_px - H / 2))
            delta_prime_rad = np.deg2rad(180.0 / H * (Z_prime_px - H / 2))
            h = D * (np.tan(delta_prime_rad) - np.tan(delta_rad))
            
            Y_px = W - xmax # Y_right
            Y_prime_px = W - xmin # Y_left
            mu_rad = np.deg2rad(360.0 / W * (Y_px - W / 2))
            mu_prime_rad = np.deg2rad(360.0 / W * (Y_prime_px - W / 2))
            w = D * (np.tan(mu_rad) - np.tan(mu_prime_rad))

            # 创建检索树的位置点
            Point(tree_lon, tree_lat)
            tree_point = [tree_lon, tree_lat]
            # KD树搜索
            # k=1 默认为最近距离
            # k=10 在最近距离为10的前提下，寻找最小角度
            distances, indices = tree_kdtree.query([tree_point], k=1)

            nearest_points = []
            for  target_idx in indices:
                target_point = tree_point_gdf.iloc[target_idx].geometry
                SpeciesNam = tree_point_gdf.iloc[target_idx].SpeciesNam
                CommonName = tree_point_gdf.iloc[target_idx].CommonName
                asset_id = tree_point_gdf.iloc[target_idx].asset_id
                target_lon, target_lat = target_point.x, target_point.y
                
                # 计算真实距离（米）
                real_dist_m = haversine_distance(camera_lon, camera_lat, target_lon, target_lat)
                
                # 计算角度
                angle = calculate_angle(Point(camera_lon, camera_lat), target_point)
                
                nearest_points.append({
                    'distance_m': real_dist_m,
                    'angle_deg': angle,
                    'target_idx': target_idx,
                    'target_coords': (target_lon, target_lat),
                    'SpeciesNam': SpeciesNam,
                    'CommonName': CommonName,
                    'asset_id': asset_id,
                })
            
            # 按距离排序
            nearest_points.sort(key=lambda x: x['distance_m'])
            # 定义计算角度差的函数
            def calculate_angle_diff(point_angle, tree_angle):
                diff = abs(point_angle - tree_angle)
                return min(diff, 360 - diff)
            
            # 找到角度差最小的点
            best_match = min(
                nearest_points, 
                key=lambda x: calculate_angle_diff(x['angle_deg'], tree_degree)
            )

            asset_id = best_match['asset_id'], # 新增
            SpeciesNam = best_match['SpeciesNam'], # 新增
            CommonName = best_match['CommonName'], # 新增

            results.append({
                'id': i + 1,
                'label': det['label'],
                'confidence': det['confidence'],
                'bbox': bbox, 
                'D (meters)': D,
                'height (meters)': abs(h), 
                'canopy_diameter (meters)': abs(w), 
                'North_degree (deg)': north_angle,
                'Yaw_Angle_phi (deg)': tree_degree,
                'Tree_X_Planar_meters': x,
                'Tree_Y_Planar_meters': y,
                'Tree_Lon_WGS84': tree_lon, # 新增
                'Tree_Lat_WGS84': tree_lat, # 新增
                'asset_id': asset_id, # 新增
                'SpeciesNam': SpeciesNam, # 新增
                'CommonName': CommonName, # 新增
            })

        return results

    def draw_results_on_image(image_path, calculated_results, output_path):
        """
        在原始街景图像上绘制边界框和计算出的所有参数信息，并保存。
        """
        try:
            img = Image.open(image_path).convert("RGB")
        except FileNotFoundError:
            print(f"Error: Cannot open image file at {image_path} for drawing.")
            return

        draw = ImageDraw.Draw(img)
        
        # 尝试加载支持中文的字体
        FONT_SIZE = 10 
        try:
            font = ImageFont.truetype("simsun.ttc", size=FONT_SIZE) 
        except IOError:
            try:
                font = ImageFont.truetype("msyh.ttc", size=FONT_SIZE)
            except IOError:
                font = ImageFont.load_default()
                print("Warning: Chinese font not found. Using default font.")
                
        color_map = {
            'Plane tree': 'red',
            'Willow': 'green',
            'Locust tree': 'blue',
            'other': 'yellow'
        }

        for res in calculated_results:
            xmin, ymin, xmax, ymax = res['bbox']
            label = res['label']
            
            # 1. 绘制边界框
            box_color = color_map.get(label, 'red') 
            draw.rectangle([xmin, ymin, xmax, ymax], outline=box_color, width=3)
            
            # 2. 准备所有参数文本
            d_text = f"深度(D): {res['D (meters)']:.1f} m"
            if res['D (meters)'] == 13.5: 
                d_text += "(默认)" 

            # 这里约定规则，全景图从左往右为0-360度
            text_lines = [
                f"ID: {res['id']} - {label} ({res['confidence']:.2f})",
                d_text,
                f"高度(h): {res['height (meters)']:.1f} m",
                f"冠幅宽度(w): {res['canopy_diameter (meters)']:.1f} m",
                f"相对正北角度: {res['Yaw_Angle_phi (deg)']:.0f}°",
                f"WGS84:({res['Tree_Lon_WGS84']:.5f}, {res['Tree_Lat_WGS84']:.5f})",
                f"asset_id: {res['asset_id']}",
                f"SpeciesNam: {res['SpeciesNam']}",
                f"CommonName: {res['CommonName']}",
            ]
            info_text = "\n".join(text_lines)
            
            # 3. 绘制文本
            text_x = xmin + 5 
            
            # 估算文本块高度，尝试放在框体上方
            try:
                text_bbox_temp = draw.textbbox((0, 0), info_text, font=font)
                text_height = text_bbox_temp[3] - text_bbox_temp[1]
            except Exception:
                text_height = len(text_lines) * (FONT_SIZE + 5) 
            
            text_y = ymin - text_height - 5 
            
            # 如果上方空间不足，则放在下方
            if text_y < 0:
                text_y = ymax + 5 

            # 4. 绘制文本背景和文本本身
            text_bbox = draw.textbbox((text_x, text_y), info_text, font=font)
            box_color = color_map.get(label, 'white') 
            # draw.rectangle(text_bbox, fill=box_color, width=0)
            draw.rectangle(text_bbox, width=0)
            draw.text((text_x, text_y), info_text, fill="black", font=font) 
    
        # try:
        #     img = Image.open(image_path).convert("RGB")
        # except FileNotFoundError:
        #     print(f"Error: Cannot open image file at {image_path} for drawing.")
        #     return

        # draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("simsun.ttc", size=10) 
        draw.text((10, 340),  f"约定规则，全景图从左往右为0-360度", fill="red", font=font) 
        draw.text((10, 360),  f"正北对应全景图角度(φ): {calculated_results[0]['North_degree (deg)']:.0f}°", fill="red", font=font) 

        # 绘制正北像所在像素位置
        xmin = calculated_results[0]['North_degree (deg)']/360*8192
        xmax = xmin + 20
        ymin = 0
        ymax = 800
        box_color = 'blue'
        # draw.rectangle([xmin, ymin, xmax, ymax], fill=box_color)

        # 保存图像
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)
            # print(f"\n--- ✅ 绘图结果已保存至: {output_path} ---")
        except Exception as e:
            print(f"\n--- ❌ 图像保存失败 ---")
            print(f"Error during image saving: {e}")

    calculated_results = calculate_tree_parameters_FINAL(
        detections, DEPTH_PATH, W, H, YAW_ANGLE_THETA_0_DEG, CAMERA_LON, CAMERA_LAT
    )

    # print("\n--- 🌳 街景树尺寸参数计算结果 (基于您的优化深度图) ---")
    # for res in calculated_results:
    #     print(f"\n# 树木 ID: {res['id']} ({res['label']})")
    #     print(f"  - 深度 D: {res['D (meters)']:.2f} 米")
    #     print(f"  - 高度 h: {res['height (meters)']:.2f} 米")
    #     print(f"  - 冠幅直径 w: {res['canopy_diameter (meters)']:.2f} 米")
    #     print(f"  - 绝对方位角 φ: {res['Yaw_Angle_phi (deg)']:.2f} 度")
    #     print(f"  - 平面坐标 (x, y): ({res['Tree_X_Planar_meters']:.2f}, {res['Tree_Y_Planar_meters']:.2f}) 米 (UTM 模拟)")
        # --- 新增打印 WGS84 经纬度 ---
        # print(f"  - WGS84 经纬度 (Lon, Lat): ({res['Tree_Lon_WGS84']:.6f}, {res['Tree_Lat_WGS84']:.6f})")
        
    draw_results_on_image(IMAGE_PATH, calculated_results, OUTPUT_PATH)

if __name__ == "__main__":
    tree_point_path = r"e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data_32633\CoS_streettree_data.shp"  # 搜索点文件
    tree_point_gdf = gpd.read_file(tree_point_path)
    print(f"树点数量: {len(tree_point_gdf)} 个点")
    if tree_point_gdf.crs != CRS('EPSG:4326'):
        print("警告：SHP文件不是WGS84坐标系，将自动转换...")
        tree_point_gdf = tree_point_gdf.to_crs('EPSG:4326')

    # IMAGE_PATH = r"e:\work\sv_pangpang\sv_pano_20251106\test_json\0_151.2039411_-33.86877441_84.30375671386719_2020_11_detection_results.jpg"
    # JSON_PATH = r"e:\work\sv_pangpang\sv_pano_20251106\test_json\0_151.2039411_-33.86877441_84.30375671386719_2020_11_detection_results.json"
    # OUTPUT_PATH = r"e:\work\sv_pangpang\sv_pano_20251106\test_json\0_151.2039411_-33.86877441_84.30375671386719_2020_11_detection_annotations_wgs84.jpg" 
    # DEPTH_PATH = r"e:\work\sv_pangpang\sv_pano_20251106\test_json\0_151.2039411_-33.86877441_84.30375671386719_2020_11.jpg" 

    path = r'E:\work\sv_pangpang\sv_pano_20251219\Cos_test'
    result_files = []
    # 遍历当前目录
    for root, dirs, files in os.walk(path):
        for file in files:
            # if file.endswith('_detection_results.jpg'):
            # if file.endswith('.jpg'):
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                result_files.append(file_path)

    for index, IMAGE_PATH in tqdm(enumerate(result_files), total=len(result_files)):
        # print(f"Processing file: {IMAGE_PATH}")

        JSON_PATH = IMAGE_PATH.replace('Cos_test', 'grounding_dino_results').replace('.png', '_detection_results.json')
        DEPTH_PATH = IMAGE_PATH.replace('Cos_test', 'CoS_30m_pano_cut_depth_test')
        OUTPUT_PATH = IMAGE_PATH.replace('Cos_test', 'Cos_test_date')

        main(IMAGE_PATH, JSON_PATH, DEPTH_PATH, OUTPUT_PATH, tree_point_gdf)
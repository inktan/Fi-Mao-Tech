import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont 
from pyproj import Transformer

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
    
# ====================================================================
# 2. 模拟和变量设置 (保留自上一轮对话)
# ====================================================================

# 模拟 Monodepth2 输出路径 (假设已生成)
MONODEPTH_OUTPUT_PATH = "simulated_depth_map.npy"
# 原始输入文件路径 (此处使用一个合理的模拟值)
# 假设的相机位置 (Jinan附近) 和航向角
CAMERA_LON = 117.001
CAMERA_LAT = 36.666
YAW_ANGLE_THETA_0_DEG = 85.0

IMAGE_PATH = "simulated_image.jpg"
JSON_PATH = "simulated_detections.json"
OUTPUT_PATH = "annotated_image_pyproj.jpg" 

W, H = 2048, 1024 
DEFAULT_DEPTH_M = 15.0 

# 模拟检测结果（为避免依赖外部文件，直接定义）
detections = [
    {'label': 'Plane tree', 'confidence': 0.95, 'bbox': [300, 450, 500, 700]}, # 树1：左侧
    {'label': 'Willow', 'confidence': 0.88, 'bbox': [700, 500, 850, 750]},     # 树2：中间
    {'label': 'Locust tree', 'confidence': 0.92, 'bbox': [1700, 500, 1900, 750]}, # 树3：右侧
]

# 模拟创建深度图文件 (假定所有深度都是 15.0 米)
simulated_depth_map = np.full((H, W), DEFAULT_DEPTH_M, dtype=np.float32)
np.save(MONODEPTH_OUTPUT_PATH, simulated_depth_map)
print(f"--- ⚠️ 模拟深度图已创建用于测试：{MONODEPTH_OUTPUT_PATH} (D={DEFAULT_DEPTH_M}m) ---")


# ====================================================================
# 3. 核心函数: 深度读取（保持不变，模拟 Monodepth2 输出处理）
# ====================================================================

def get_depth_at_pixel_from_monodepth_output(depth_map_path, x_pixel, y_pixel, W, H):
    x_int, y_int = int(x_pixel), int(y_pixel)
    if not (0 <= x_int < W and 0 <= y_int < H):
        return DEFAULT_DEPTH_M
    
    try:
        depth_map = np.load(depth_map_path)
        if depth_map.shape != (H, W):
            return DEFAULT_DEPTH_M
        
        D = depth_map[y_int, x_int]
        if D <= 0 or D > 100: 
            return DEFAULT_DEPTH_M
            
        return float(D)

    except FileNotFoundError:
        return DEFAULT_DEPTH_M
    except Exception:
        return DEFAULT_DEPTH_M

# ====================================================================
# 4. 核心函数: 参数计算（修改坐标转换部分）
# ====================================================================

def calculate_tree_parameters_FINAL(detections, depth_map_path, W, H, theta_0_deg, camera_lon, camera_lat, pyproj_loaded):
    results = []
    
    # === 步骤 0: 准确获取相机所在的平面坐标 (x_prime, y_prime) - 使用 pyproj ===
    if pyproj_loaded:
        x_prime, y_prime = transformer.transform(camera_lon, camera_lat)
    else:
        # 如果 pyproj 未加载，使用默认值或简单近似（不推荐用于实际分析）
        x_prime, y_prime = 500000.0, 4000000.0 # 模拟 UTM 坐标 (X, Y)
        print("Using simulated planar coordinates for the camera (pyproj not available).")
    
    for i, det in enumerate(detections):
        bbox = det.get('bbox', [0, 0, 0, 0]) 
        xmin, ymin, xmax, ymax = [int(val) for val in bbox]
        
        X_center = (xmin + xmax) / 2
        Z_bottom = ymax 
        Z_top = ymin
        
        # --- 步骤 1: 估计深度 D ---
        D = get_depth_at_pixel_from_monodepth_output(depth_map_path, X_center, Z_bottom, W, H)
        
        # --- 步骤 2: 计算绝对方位角 (φ) ---
        theta_prime_deg = (X_center - W / 2) / W * 360.0
        phi_deg = (theta_0_deg + theta_prime_deg) % 360.0
        if phi_deg < 0:
            phi_deg += 360.0
        phi_rad = np.deg2rad(phi_deg) 
        
        # 树木的准确平面坐标 (x, y) - 米制 UTM Zone 50N
        # X = X_camera + D * cos(phi)
        # Y = Y_camera + D * sin(phi)
        x_tree = x_prime + D * np.cos(phi_rad)
        y_tree = y_prime + D * np.sin(phi_rad)
        
        # === 步骤 2.5: 将平面坐标 (x, y) 转换回 WGS84 经纬度 (使用 pyproj) ===
        if pyproj_loaded:
            tree_lon, tree_lat = rev_transformer.transform(x_tree, y_tree)
        else:
             # 如果 pyproj 不可用，使用相机 Lon/Lat 作为占位符
            tree_lon, tree_lat = CAMERA_LON, CAMERA_LAT 
        
        # --- 步骤 3 & 4: 计算树的高度 h 和直径 w ---
        Z_px, Z_prime_px = Z_bottom, Z_top 
        delta_rad = np.deg2rad(180.0 / H * (Z_px - H / 2))
        delta_prime_rad = np.deg2rad(180.0 / H * (Z_prime_px - H / 2))
        h = D * (np.tan(delta_prime_rad) - np.tan(delta_rad))
        
        Y_px = W - xmax
        Y_prime_px = W - xmin
        mu_rad = np.deg2rad(360.0 / W * (Y_px - W / 2))
        mu_prime_rad = np.deg2rad(360.0 / W * (Y_prime_px - W / 2))
        w = D * (np.tan(mu_rad) - np.tan(mu_prime_rad))

        results.append({
            'id': i + 1,
            'label': det['label'],
            'D (meters)': D,
            'height (meters)': abs(h), 
            'canopy_diameter (meters)': abs(w), 
            'Yaw_Angle_phi (deg)': phi_deg,
            'Tree_X_UTM50N_meters': x_tree,
            'Tree_Y_UTM50N_meters': y_tree,
            'Tree_Lon_WGS84': tree_lon, 
            'Tree_Lat_WGS84': tree_lat, 
        })

    return results

# ====================================================================
# 5. 执行代码
# ====================================================================

print(f"相机 WGS84 经纬度: ({CAMERA_LON}, {CAMERA_LAT})")
print(f"SVI 默认航向角 (θ₀): {YAW_ANGLE_THETA_0_DEG} 度")
print(f"UTM Zone 50N 转换状态: {'✅ 成功加载' if pyproj_loaded else '❌ 失败/模拟'}")

calculated_results = calculate_tree_parameters_FINAL(
    detections, MONODEPTH_OUTPUT_PATH, W, H, YAW_ANGLE_THETA_0_DEG, CAMERA_LON, CAMERA_LAT, pyproj_loaded
)

print("\n--- 🌳 街景树尺寸参数计算结果 (基于 Monodepth2 & pyproj 准确坐标) ---")
for res in calculated_results:
    print(f"\n# 树木 ID: {res['id']} ({res['label']})")
    print(f"  - 深度 D: {res['D (meters)']:.2f} 米")
    print(f"  - 高度 h: {res['height (meters)']:.2f} 米")
    print(f"  - 冠幅直径 w: {res['canopy_diameter (meters)']:.2f} 米")
    print(f"  - UTM50N 坐标 (X, Y): ({res['Tree_X_UTM50N_meters']:.2f}, {res['Tree_Y_UTM50N_meters']:.2f}) 米")
    print(f"  - WGS84 经纬度 (Lon, Lat): ({res['Tree_Lon_WGS84']:.6f}, {res['Tree_Lat_WGS84']:.6f})")
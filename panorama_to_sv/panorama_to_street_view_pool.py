# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# 全局变量，用于子进程共享缓存矩阵
CACHE_MAPS = []

class PanoConverter:
    """工具类：专门负责计算重映射矩阵"""
    @staticmethod
    def create_maps(fov, theta, phi, canvas_h, canvas_w, src_h, src_w):
        f = 0.5 * canvas_w / np.tan(0.5 * fov / 180.0 * np.pi)
        cx, cy = (canvas_w - 1) / 2.0, (canvas_h - 1) / 2.0
        K = np.array([
            [f, 0, cx],
            [0, f, cy],
            [0, 0, 1],
        ], dtype=np.float32)
        K_inv = np.linalg.inv(K)

        x, y = np.meshgrid(np.arange(canvas_w), np.arange(canvas_h))
        xyz = np.stack([x, y, np.ones_like(x)], axis=-1).astype(np.float32)
        xyz = xyz @ K_inv.T

        y_axis = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        R1, _ = cv2.Rodrigues(y_axis * np.radians(theta))
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(phi))
        R = R2 @ R1
        
        xyz = xyz @ R.T
        norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
        xyz_norm = xyz / norm
        
        lon = np.arctan2(xyz_norm[..., 0], xyz_norm[..., 2])
        lat = np.arcsin(xyz_norm[..., 1])

        map_x = (lon / (2 * np.pi) + 0.5) * (src_w - 1)
        map_y = (lat / np.pi + 0.5) * (src_h - 1)
        return map_x.astype(np.float32), map_y.astype(np.float32)

def init_worker(maps):
    """子进程初始化函数，将矩阵存入全局变量"""
    global CACHE_MAPS
    CACHE_MAPS = maps

def process_image_task(task_info):
    """单张图片的实际处理逻辑"""
    img_path, output_info = task_info
    try:
        # 1. 读取图像 (处理中文路径)
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None: return False, img_path, "读取失败"
        
        h, w = img.shape[:2]
        # 保证 2:1 比例（如果输入图比例不对，此处做一次 resize）
        if w != 2 * h:
            img = cv2.resize(img, (2 * h, h), interpolation=cv2.INTER_LINEAR)

        # 2. 遍历预存的 map 进行变换
        for degree, out_path, map_idx in output_info:
            # 直接从全局变量获取缓存好的 map，无需重新计算
            map_x, map_y = CACHE_MAPS[map_idx]
            
            # 执行重映射 (使用线性插值平衡速度与质量)
            persp = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            
            # 保存图片 (处理中文路径)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            res, encoded_img = cv2.imencode('.jpg', persp, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            if res:
                encoded_img.tofile(out_path)
                
        return True, img_path, "OK"
    except Exception as e:
        return False, img_path, str(e)

def run_conversion(input_dir, fov, degree_count, phi, out_h, out_w):
    # 1. 扫描文件
    exts = ('.jpg', '.jpeg', '.png', '.bmp')
    all_files = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(exts):
                all_files.append(os.path.join(root, f))
    
    if not all_files:
        print("未找到图片！")
        return

    # 2. 预计算所有角度的 Maps (仅需一次)
    print("正在预计算重映射矩阵...")
    degrees = [i * (360 / degree_count) for i in range(degree_count)]
    # 获取第一张图的尺寸作为基准（假设所有全景图尺寸一致，若不一致代码内有resize兼容）
    sample_img = cv2.imdecode(np.fromfile(all_files[0], dtype=np.uint8), cv2.IMREAD_COLOR)
    src_h, src_w = sample_img.shape[:2]
    if src_w != 2 * src_h: src_w = 2 * src_h
    
    precomputed_maps = []
    for d in degrees:
        m_x, m_y = PanoConverter.create_maps(fov, d, phi, out_h, out_w, src_h, src_w)
        precomputed_maps.append((m_x, m_y))

    # 3. 准备任务列表
    tasks = []
    for path in all_files:
        output_info = []
        for i, d in enumerate(degrees):
            # 构建输出路径：将 sv_pan01 替换为 街景
            out_p = path.replace('sv_pan01', '街景').replace('.j', f'_{int(d)}.j')
            if not os.path.exists(out_p):
                output_info.append((d, out_p, i))
        
        if output_info:
            tasks.append((path, output_info))

    # 4. 多进程执行
    print(f"开始并行处理，图片总数: {len(all_files)}, 待处理: {len(tasks)}")
    workers = max(1, cpu_count() - 1)
    
    # 使用 initializer 将预计算的 maps 传递给每个子进程
    with Pool(processes=workers, initializer=init_worker, initargs=(precomputed_maps,)) as pool:
        results = list(tqdm(pool.imap_unordered(process_image_task, tasks), total=len(tasks), desc="转换中"))

    # 5. 统计结果
    success = sum(1 for r in results if r[0])
    print(f"\n处理完成！成功: {success}, 失败: {len(tasks) - success}")

if __name__ == "__main__":
    # 配置参数
    CONFIG = {
        "input_dir": r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\泉州市\sv_pan01',
        "fov": 90,
        "phi": 0,
        "degree_count": 4,
        "width": 2048,
        "height": 1536
    }

    run_conversion(
        CONFIG["input_dir"], 
        CONFIG["fov"], 
        CONFIG["degree_count"], 
        CONFIG["phi"], 
        CONFIG["height"], 
        CONFIG["width"]
    )
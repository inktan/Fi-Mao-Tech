import json
import numpy as np
import cv2
import os

def find_structural_change_point(width_series):
    """
    模拟 R 语言 strucchange 包中的 Fstats 原理
    寻找宽度序列中残差平方和最小的突变点
    """
    n = len(width_series)
    if n < 10: return 0  # 序列太短无法计算
    
    best_break_point = 0
    min_rss = float('inf')
    
    # 按照论文原理，在序列中寻找使前后两部分回归残差之和最小的点
    # 这里简化为寻找均值差异最显著的点（即宽度从树干到树冠的跳变）
    for t in range(int(n*0.1), int(n*0.9)):  # 避开极端的顶部和底部
        part1 = width_series[:t]
        part2 = width_series[t:]
        
        # 计算残差平方和 (RSS)
        rss = np.sum((part1 - np.mean(part1))**2) + np.sum((part2 - np.mean(part2))**2)
        
        if rss < min_rss:
            min_rss = rss
            best_break_point = t
            
    return best_break_point

def process_tree_structure(json_path, seg_map_path):
    # 1. 读取 JSON 中的 Bounding Box [cite: 156, 171]
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # 2. 读取语义分割图
    # 假设分割图是 RGB 格式
    seg_map = cv2.imread(seg_map_path)
    seg_map = cv2.cvtColor(seg_map, cv2.COLOR_BGR2RGB)
    
    # 定义树木颜色 [cite: 267]
    tree_color = np.array([4, 200, 3])
    
    results = []
    
    for det in data.get("detections", []):
        if det.get("label") != "tree":
            continue
            
        # 获取 bbox: [xmin, ymin, xmax, ymax]
        bbox = det.get("bbox")
        xmin, ymin, xmax, ymax = map(int, bbox)
        
        # 3. 定位单棵树并提取轮廓
        # 裁剪语义分割图中的对应区域
        roi = seg_map[ymin:ymax, xmin:xmax]
        
        # 创建掩码：匹配颜色 (4, 200, 3)
        mask = cv2.inRange(roi, tree_color, tree_color)
        
        # 4. 计算垂直宽度序列 [cite: 377, 382]
        # 每一行属于树木的像素个数 (Ni)
        width_series = np.sum(mask > 0, axis=1)
        
        # 5. 应用突变点检测识别分界点 
        # 注意：由于图像坐标 y 是从上到下的，序列顶部是树冠，底部是树干
        break_point_idx = find_structural_change_point(width_series)
        
        # 计算在原图中的像素高度坐标
        interface_y = ymin + break_point_idx
        
        results.append({
            "bbox": bbox,
            "interface_y": interface_y,
            "bole_height_px": ymax - interface_y, # 树干部分像素高度
            "crown_height_px": interface_y - ymin # 树冠部分像素高度
        })
        
    return results

# 调用示例
json_file = r"e:\work\sv_pangpang\sv_pano_20251219\grounding_dino_results\FID_0_2021-03_pano_detection_results.json"
seg_file = r"e:\work\sv_pangpang\sv_pano_20251219\ade_20k\ColorBblock_resize\FID_0_2021-03_pano.png"

tree_info = process_tree_structure(json_file, seg_file)

import json
import numpy as np
import cv2
import os
import glob
from PIL import Image, ImageDraw, ImageFont

def get_rescaling_factors(y, y_mid, H):
    """计算垂直(Cv)和水平(Ch)修正因子 [cite: 285, 286]"""
    Di = abs(y - y_mid)
    sin_theta = (2.0 * Di) / H
    sin_theta = np.clip(sin_theta, -1.0, 1.0)
    cos_theta = np.sqrt(1.0 - sin_theta**2)
    
    # Cv = sec(theta), Ch = cos(theta) [cite: 286, 289]
    cv = 1.0 / cos_theta if cos_theta > 0 else 1.0
    ch = cos_theta
    return cv, ch

def find_interface_point(width_series):
    """利用残差平方和最小值识别树干与树冠分界点 [cite: 332, 347]"""
    n = len(width_series)
    if n < 10: return n // 2
    
    min_rss = float('inf')
    break_point = 0
    
    for t in range(int(n*0.1), int(n*0.9)):
        seg1 = width_series[:t]
        seg2 = width_series[t:]
        rss = np.sum((seg1 - np.mean(seg1))**2) + np.sum((seg2 - np.mean(seg2))**2)
        if rss < min_rss:
            min_rss = rss
            break_point = t
    return break_point

def process_and_enrich_data(json_path, seg_path, VH=2.5):
    """计算物理指标并更新数据结构 [cite: 205, 390]"""
    if not os.path.exists(json_path) or not os.path.exists(seg_path):
        return None, None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    seg_map = cv2.imread(seg_path)
    if seg_map is None: return None, None
        
    seg_map = cv2.cvtColor(seg_map, cv2.COLOR_BGR2RGB)
    H, W, _ = seg_map.shape
    y_mid = H / 2.0
    tree_rgb = (4, 200, 3) 

    valid_results = []

    for det in data.get("detections", []):
        if det.get("label") != "tree": continue
        
        bbox = det.get("bbox")
        xmin, ymin = max(0, int(bbox[0])), max(0, int(bbox[1]))
        xmax, ymax = min(W, int(bbox[2])), min(H, int(bbox[3]))
        
        if ymin >= ymax or xmin >= xmax: continue

        roi = seg_map[ymin:ymax, xmin:xmax]
        if roi.size == 0: continue
        mask = cv2.inRange(roi, tree_rgb, tree_rgb)

        # 计算尺度因子 wr [cite: 328]
        cv_sum_wr = 0.0
        start_y, end_y = int(min(y_mid, ymax)), int(max(y_mid, ymax))
        for y in range(start_y, end_y + 1):
            cv, _ = get_rescaling_factors(y, y_mid, H)
            cv_sum_wr += cv
        
        if cv_sum_wr == 0: continue
        wr = VH / cv_sum_wr 

        h_tree = 0.0
        width_phys_series = [] 
        for local_y in range(mask.shape[0]):
            global_y = ymin + local_y
            cv, ch = get_rescaling_factors(global_y, y_mid, H)
            h_tree += cv * wr
            # 基于物理像素宽度 [cite: 377, 378]
            width_phys_series.append(np.sum(mask[local_y] > 0) * ch * wr)

        break_idx = find_interface_point(width_phys_series)
        interface_y = ymin + break_idx
        
        # 更新 JSON 数据字段 
        det["total_height"] = round(h_tree, 2)
        det["crown_width"] = round(max(width_phys_series[:break_idx]), 2) if break_idx > 0 else 0
        det["dbh_diameter"] = round(np.median(width_phys_series[break_idx:]), 2) if break_idx < len(width_phys_series) else 0
        det["crown_height"] = round(sum(get_rescaling_factors(y, y_mid, H)[0] * wr for y in range(ymin, interface_y)), 2)
        det["bole_height"] = round(det["total_height"] - det["crown_height"], 2)
        det["interface_y"] = int(interface_y)
        
        valid_results.append(det)

    return data, valid_results

def draw_results_on_image(image_path, calculated_results, output_path):
    """将参数绘制在图像上，修正 NameError 并增加自适应文字 [cite: 241, 723]"""
    if not calculated_results: return

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"打开图像失败: {e}")
        return

    draw = ImageDraw.Draw(img)
    W, H = img.size
    # 自适应字体大小：图像宽度的 1.5%
    font_size = max(20, int(W * 0.015))
    
    try:
        font = ImageFont.truetype("simsun.ttc", size=font_size)
    except:
        font = ImageFont.load_default()

    for res in calculated_results:
        xmin, ymin, xmax, ymax = res['bbox']
        # 绘制边界框
        draw.rectangle([xmin, ymin, xmax, ymax], outline='red', width=max(2, int(W*0.002)))
        
        # 绘制分界线 [cite: 332]
        if 'interface_y' in res:
            draw.line([xmin, res['interface_y'], xmax, res['interface_y']], fill='yellow', width=2)

        info_text = (f"树高: {res['total_height']}m\n"
                     f"冠幅高度: {res['crown_height']}m\n"
                     f"冠幅宽度: {res['crown_width']}m\n"
                     f"胸径: {res['dbh_diameter']}m")
        
        # 计算文本框大小 [cite: 241]
        text_bbox = draw.textbbox((xmin + 5, ymin), info_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        # 确定文本绘制的起始 Y 坐标（默认在框内顶部，若太小则放框外）
        draw_y = ymin - text_h - 10 if ymin - text_h - 10 > 0 else ymax + 5
        
        # 绘制半透明背景
        final_text_bbox = [xmin, draw_y, xmin + text_w + 10, draw_y + text_h + 5]
        draw.rectangle(final_text_bbox, fill=(0, 0, 0, 150))
        draw.text((xmin + 5, draw_y), info_text, fill="white", font=font)

    img.save(output_path)

# --- 主程序入口 ---
from tqdm import tqdm
if __name__ == "__main__":
    JSON_DIR = r'E:\work\sv_pangpang\sv_pano_20251219\grounding_dino_results'
    SEG_DIR = r'E:\work\sv_pangpang\sv_pano_20251219\ade_20k\ColorBblock_resize'
    IMG_DIR = r'E:\work\sv_pangpang\sv_pano_20251219\CoS_30m_pano_cut'
    OUTPUT_DIR = r'E:\work\sv_pangpang\sv_pano_20251219\enriched_results'
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_list = glob.glob(os.path.join(JSON_DIR, "*.json"))

    for j_file in tqdm(json_list, total=len(json_list), desc='处理进度'):
        base = os.path.basename(j_file).replace('_detection_results.json', '')
        s_file = os.path.join(SEG_DIR, f"{base}.png")
        i_file = os.path.join(IMG_DIR, f"{base}.png")
        
        # 1. 计算物理指标 [cite: 390]
        enriched_json, draw_data = process_and_enrich_data(j_file, s_file)
        
        if enriched_json:
            # 2. 保存增强后的 JSON [cite: 389]
            json_out = os.path.join(OUTPUT_DIR, f"{base}_enriched.json")
            with open(json_out, 'w', encoding='utf-8') as f:
                json.dump(enriched_json, f, indent=2, ensure_ascii=False)
            
            # 3. 绘制结果图 [cite: 241]
            img_out = os.path.join(OUTPUT_DIR, f"{base}_viz.png")
            draw_results_on_image(i_file, draw_data, img_out)
            # print(f"已成功处理并导出: {base}")
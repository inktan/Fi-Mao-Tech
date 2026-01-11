import json
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont 

def batch_estimate_tree_height_from_json(json_path, camera_height=2.5):
    """
    读取JSON文件并批量计算树高
    :param json_path: 包含检测框数据的JSON文件路径
    :param camera_height: 相机安装高度 (VH)，论文默认为 2.5m 
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 获取图像尺寸以确定全景图总高度 H
    image_path = data.get("image_path", "")
    if not os.path.exists(image_path):
        print(f"警告: 图像路径不存在 {image_path}，请手动确认全景图高度。")
        # 假设高度为论文中的 832，实际应用中建议从图片读取 
        H = 832
    else:
        with Image.open(image_path) as img:
            _, H = img.size

    y_mid = H / 2.0  # 图像中线 (POV) 
    results = []

    def get_cv_factor(y):
        """计算特定y坐标像素的垂直修正因子 Cv [cite: 285]"""
        Di = abs(y - y_mid)
        # sin(theta) = 2 * Di / H [cite: 280]
        sin_theta = (2.0 * Di) / H
        sin_theta = min(max(sin_theta, -1.0), 1.0) # 边界检查
        # Cv = sec(theta) = 1 / cos(theta) = 1 / sqrt(1 - sin^2)
        cos_theta = np.sqrt(1.0 - sin_theta**2)
        return 1.0 / cos_theta if cos_theta > 0 else 1.0

    for idx, det in enumerate(data.get("detections", [])):
        if det.get("label") != "tree":
            continue
            
        # 提取 bbox: [xmin, ymin, xmax, ymax]
        bbox = det.get("bbox")
        tree_top_y = bbox[1]    # 树顶 ymin 
        tree_base_y = bbox[3]   # 树底 ymax 

        # 1. 计算参考像素高度 wr [cite: 328]
        # wr = VH / sum(Cv) 从树底到中线
        start_y = int(min(y_mid, tree_base_y))
        end_y = int(max(y_mid, tree_base_y))
        
        cv_sum_for_wr = sum(get_cv_factor(y) for y in range(start_y, end_y + 1))

        if cv_sum_for_wr == 0:
            print(f"树木 {idx} 坐标异常，跳过。")
            continue
            
        wr = camera_height / cv_sum_for_wr

        # 2. 计算整棵树的高度 h_tree [cite: 352]
        # h_tree = sum(Cv * wr) 从树底到树顶
        h_tree = sum(get_cv_factor(y) * wr for y in range(int(tree_top_y), int(tree_base_y) + 1))

        results.append({
            "tree_index": idx,
            "confidence": det.get("confidence"),
            "height (meters)": round(h_tree, 2),
            "bbox": bbox
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
    FONT_SIZE = 20 
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
        # label = res['label']
        
        # 1. 绘制边界框
        # box_color = color_map.get(label, 'red') 
        draw.rectangle([xmin, ymin, xmax, ymax], outline='red', width=3)
        
        # 2. 准备所有参数文本
        # d_text = f"深度(D): {res['D (meters)']:.1f} m"
        # if res['D (meters)'] == 13.5: 
        #     d_text += "(默认)" 

        # 这里约定规则，全景图从左往右为0-360度
        text_lines = [
            # f"ID: {res['id']} - {label} ({res['confidence']:.2f})",
            # d_text,
            f"高度(h): {res['height (meters)']:.1f} m",
            # f"冠幅宽度(w): {res['canopy_diameter (meters)']:.1f} m",
            # f"相对正北角度: {res['Yaw_Angle_phi (deg)']:.0f}°",
            # f"WGS84:({res['Tree_Lon_WGS84']:.5f}, {res['Tree_Lat_WGS84']:.5f})",
            # f"asset_id: {res['asset_id']}",
            # f"SpeciesNam: {res['SpeciesNam']}",
            # f"CommonName: {res['CommonName']}",
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
        # box_color = color_map.get(label, 'white') 
        draw.rectangle(text_bbox, fill='white', width=0)
        draw.text((text_x, text_y), info_text, fill="black", font=font) 

    # try:
    #     img = Image.open(image_path).convert("RGB")
    # except FileNotFoundError:
    #     print(f"Error: Cannot open image file at {image_path} for drawing.")
    #     return

    # draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("simsun.ttc", size=10) 
    # draw.text((100, 3400),  f"约定规则，全景图从左往右为0-360度", fill="red", font=font) 
    # draw.text((100, 3600),  f"正北对应全景图角度(φ): {calculated_results[0]['North_degree (deg)']:.0f}°", fill="red", font=font) 

    # 绘制正北像所在像素位置
    # xmin = calculated_results[0]['North_degree (deg)']/360*8192
    xmax = xmin + 20
    ymin = 0
    ymax = 4096
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



# 使用示例
json_data_path = r"e:\work\sv_pangpang\sv_pano_20251219\grounding_dino_results\FID_0_2021-03_pano_detection_results.json"
tree_heights = batch_estimate_tree_height_from_json(json_data_path)
# for tree in tree_heights:
#     print(f"树木索引: {tree['tree_index']}, 估算高度: {tree['estimated_height_m']} 米")

IMAGE_PATH = r'e:\work\sv_pangpang\sv_pano_20251219\CoS_30m_pano_cut\FID_0_2021-03_pano.png'
calculated_results = tree_heights
OUTPUT_PATH = r'e:\work\sv_pangpang\sv_pano_20251219\CoS_30m_pano_cut_date\FID_0_2021-03_pano.png'

draw_results_on_image(IMAGE_PATH, calculated_results, OUTPUT_PATH)

import cv2
import numpy as np
import os

def remove_background_by_color(input_root, output_root_name, target_color=(239, 239, 239), tolerance=10):
    """
    target_color: RGB格式的背景色
    tolerance: 容差，数值越小越精确，数值越大抠除范围越广
    """
    # OpenCV 使用 BGR，所以转换一下
    target_bgr = np.array([target_color[2], target_color[1], target_color[0]])
    
    lower_bound = np.clip(target_bgr - tolerance, 0, 255)
    upper_bound = np.clip(target_bgr + tolerance, 0, 255)

    for root, dirs, files in os.walk(input_root):
        for filename in files:
            if filename.lower().endswith('.png'):
                input_path = os.path.join(root, filename)
                
                # 路径替换逻辑
                relative_path = os.path.relpath(input_path, os.path.dirname(input_root))
                path_parts = relative_path.split(os.sep)
                path_parts[0] = output_root_name
                output_path = os.path.join(os.path.dirname(input_root), *path_parts)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # 读取图片 (带Alpha通道读取，如果没有则创建)
                img = cv2.imread(input_path)
                if img is None: continue
                
                # 转换为 BGRA
                b, g, r = cv2.split(img)
                alpha = np.ones(b.shape, dtype=b.dtype) * 255
                img_bgra = cv2.merge([b, g, r, alpha])

                # 创建掩模：在颜色范围内的像素设为白色(255)，其余黑色(0)
                mask = cv2.inRange(img, lower_bound, upper_bound)

                # 将掩模对应位置的 Alpha 通道设为 0（透明）
                img_bgra[mask != 0, 3] = 0

                # 保存为透明 PNG
                cv2.imwrite(output_path, img_bgra)
                print(f"已扣除背景: {filename}")

# --- 配置 ---
remove_background_by_color(
    input_root=r"C:\Users\wang.tan.GOA\Pictures\loopparade\frames", 
    output_root_name="transparent_frames_manual",
    target_color=(239, 239, 239),
    tolerance=5  # 因为你给出了精确值，建议先从 5 开始尝试
)
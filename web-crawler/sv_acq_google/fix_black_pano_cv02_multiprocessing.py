import os
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

def crop_non_black_area(image_path):
    """
    裁剪图片中的非黑色区域（全程使用Pillow处理中文路径，仅计算时用OpenCV）
    """
    try:
        # 1. 使用Pillow读取图片（原生支持中文路径）
        pil_img = Image.open(image_path).convert('RGB')  # 统一转为RGB格式，避免灰度图问题
        image = np.array(pil_img)  # 转为numpy数组供OpenCV处理
        
        # 2. 转换为灰度图（用于计算非黑色区域）
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 3. 找到非黑色像素的边界
        non_black_points = cv2.findNonZero(gray)
        if non_black_points is None:
            return None  # 全黑图片
        
        # 4. 获取边界框并裁剪（基于numpy数组裁剪）
        x, y, w, h = cv2.boundingRect(non_black_points)
        cropped_array = image[y:y+h, x:x+w]
        
        # 5. 将裁剪后的numpy数组转回Pillow对象（方便后续保存）
        cropped_pil_img = Image.fromarray(cropped_array)
        return cropped_pil_img
    
    except Exception as e:
        print(f"读取/处理错误 {image_path}: {e}")
        return None

def process_single_image(image_path):
    """
    单张图片的处理逻辑（使用Pillow保存，支持中文路径）
    """
    try:
        # 生成保存路径
        img_save_path = image_path.replace('svi_google', 'svi_google_fixed')
        
        # 如果已存在则跳过
        if os.path.exists(img_save_path):
            return True

        # 确保目录存在
        folder_path = os.path.dirname(img_save_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        # 执行裁剪（返回Pillow对象）
        cropped_pil_img = crop_non_black_area(image_path)
        
        if cropped_pil_img is not None:
            # 关键：使用Pillow保存（支持中文路径），替代cv2.imwrite
            cropped_pil_img.save(img_save_path)
            return True
        else:
            return False
    except Exception as e:
        print(f"处理失败 {image_path}: {e}")
        return False

def run_multiprocessing(img_paths, max_workers=None):
    """
    多进程运行函数
    :param img_paths: 图片路径列表
    :param max_workers: 使用的CPU核心数，None表示使用所有核心
    """
    # 使用 tqdm 显示进度
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_single_image, path) for path in img_paths]
        
        # 实时显示进度条
        for _ in tqdm(as_completed(futures), total=len(img_paths), desc="正在多核处理图片"):
            pass

def main():
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")
    folder_path_list = [
        r'F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\澳门特别行政区\svi_google',
    ]
    
    img_paths = []
    for folder_path in folder_path_list:
        if not os.path.exists(folder_path):
            print(f"路径不存在: {folder_path}")
            continue
            
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(accepted_formats):
                    img_paths.append(os.path.join(root, file))
    
    print(f"共发现 {len(img_paths)} 张图片，准备开始多进程处理...")
    
    # 启动多进程
    run_multiprocessing(img_paths)

if __name__ == '__main__':
    # 在 Windows 上使用多进程必须放在 if __name__ == '__main__': 之下
    main()
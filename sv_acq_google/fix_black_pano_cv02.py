import os
import cv2
import numpy as np
import time
from tqdm import tqdm
from PIL import Image
import numpy as np

def crop_non_black_area(image_path):
    # 加载图片
    image = cv2.imread(image_path)
    if image is None:
        print("图片无法加载，请检查路径是否正确")
        return
    # 获取原图像尺寸
    original_height, original_width = image.shape[:2]
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 找到非黑色像素
    non_black_points = cv2.findNonZero(gray)
    # 获取这些点的边界
    x, y, w, h = cv2.boundingRect(non_black_points)
    # 裁剪图片
    cropped_image = image[y:y+h, x:x+w]
    # 获取裁剪后图像尺寸
    cropped_height, cropped_width = cropped_image.shape[:2]
    
    # 检查尺寸是否相同
    if cropped_height == original_height and cropped_width == original_width:
        # print("裁剪后的图像尺寸与原图像尺寸相同，不保存。")
        return
        
    # 返回裁剪后的图片
    return cropped_image


def fix_black_images(img_paths):
    for i, image_path in enumerate(tqdm(img_paths)):
        if i<=50000:
            continue
        if i>60000:
            continue
        try:
            cropped_img = crop_non_black_area(image_path)  # 添加缩放尺寸
            # 保存图片到image文件夹
            img_save_path = image_path.replace('sv_pan_zoom3',f'sv_pan_zoom3_fixedBlack')
            folder_path = os.path.dirname(img_save_path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            try:
                # 保存裁剪后的图像
                cv2.imwrite(img_save_path, cropped_img)
            except Exception as e:
                continue
        except Exception as e:
            print(f"{image_path} 失败: {e}")
            continue
            # print(f"删除文件 {file_path} 失败: {e}")

def main():
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    folder_path_list =[
        r'F:\work\sv_ran\sv_pan\sv_points_ori_times\sv_pan_zoom3',
        ]
    
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)
    print(len(img_paths))
    fix_black_images(img_paths)

if __name__ == '__main__':
    print('a01')
    main()

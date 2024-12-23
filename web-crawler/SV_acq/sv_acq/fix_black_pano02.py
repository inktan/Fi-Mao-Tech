import os
import cv2
import numpy as np
import time
from tqdm import tqdm
from PIL import Image
import numpy as np

def remove_black_borders(image):
    """去除图像中的黑边"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

def load_image(path, target_size):
    try:
        e_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if e_img is None:
            raise ValueError(f"Error loading image at path: {path}")
        
        total_pixels = e_img.shape[0] * e_img.shape[1]
        black_pixels = np.sum(np.all(e_img[:, :, :3] == [0, 0, 0], axis=-1))
        black_pixel_ratio = black_pixels / total_pixels
        if black_pixel_ratio > 0.10:
            print('qwe')
            e_img = remove_black_borders(e_img)
            e_img = cv2.resize(e_img, target_size, interpolation=cv2.INTER_LINEAR)

        if e_img.shape[-1] == 4:  # RGBA
            e_img = cv2.cvtColor(e_img, cv2.COLOR_BGRA2RGBA)
        else:
            e_img = cv2.cvtColor(e_img, cv2.COLOR_BGR2RGB)

        pillow_img = Image.fromarray(e_img)

        return pillow_img
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def fix_black_images(img_paths):
    for i, file_path in enumerate(tqdm(img_paths)):
        try:
            # pillow_img = load_image(file_path, (15360, 7680))  # 添加缩放尺寸
            pillow_img = load_image(file_path, (4096, 2048))  # 添加缩放尺寸
            # 保存图片到image文件夹
            img_save_path = file_path.replace('zoom3',f'zoom3_fixedBlack')
            folder_path = os.path.dirname(img_save_path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            pillow_img.save(img_save_path)

        except Exception as e:
            print(f"{file_path} 失败: {e}")
            continue
            # print(f"删除文件 {file_path} 失败: {e}")

def main():
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    folder_path_list =[
        r'E:\work\sv_yantu\sv_pan_zoom3',
        # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
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

import os
import cv2
import numpy as np
import time
from tqdm import tqdm
from PIL import Image
import numpy as np

from PIL import Image

# 人工定位找黑色边界
def find_first_non_black_pixel(img):

    rect_xy = [0,0,0,0]

    width, height = img.size
    for x in range(width):
        r, g, b = img.getpixel((x, 250))
        if x==width-1:
            break
        r1, g1, b1 = img.getpixel((x+1, 250))
        if (r, g, b) == (0, 0, 0) and (r1, g1, b1) == (0, 0, 0):
            rect_xy[2] = x-1
            break

    for y in range(width):
        if y == height-1:
            break

        r, g, b = img.getpixel((0, y))
        r1, g1, b1 = img.getpixel((0, y+1))
        if (r, g, b) == (0, 0, 0) and (r1, g1, b1) == (0, 0, 0):
            rect_xy[3] = y-1
            break

    if rect_xy[2] ==0:
        rect_xy[2] = width-1

    if rect_xy[3] ==0:
        rect_xy[3] = height-1
    
    return rect_xy

def fix_black_images(img_paths):
    for i, image_path in enumerate(tqdm(img_paths)):
        # if i < 0:
        #     continue
        # if i >= 111:
        #     continue
        try:
            with Image.open(image_path) as img:
                img_save_path = image_path.replace('zoom3',f'zoom3_fixedBlack')
                if os.path.exists(img_save_path):
                    continue

                folder_path = os.path.dirname(img_save_path)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                rect_xy = find_first_non_black_pixel(img)
                # print(image_path)
                # print(rect_xy)

                cropped_img = img.crop((rect_xy[0], rect_xy[1], rect_xy[2], rect_xy[3]))
                # resized_img = cropped_img.resize((4096, 2048))

                height = cropped_img.height
                width = int(height * 2)
                cropped_img = cropped_img.crop((0, 0, width, height))

                cropped_img.save(img_save_path)
                # resized_img.save(img_save_path)

        except Exception as e:
            print(f"{image_path} 失败: {e}")
            continue
            # print(f"删除文件 {file_path} 失败: {e}")

def main():
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    folder_path_list =[
        r'E:\work\sv_shushu\谷歌\sv_pan_zoom3',
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

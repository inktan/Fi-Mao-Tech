# -*- coding: utf-8 -*-

import os
from PIL import Image
from tqdm import tqdm

def seg_cal(input_folder):

    # roots = []
    # img_names = []
    img_paths = []

    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(accepted_formats):
                # roots.append(root)
                # img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    for index, image_name_path in enumerate(tqdm(list(img_paths))):
        # if index <= -1:
        #     continue
        # if index > 400000:
        #     continue

        # 检查文件是否存在
        if not os.path.exists(image_name_path):
            continue

        pil_image = Image.open(image_name_path)
        
        ss_rgb_tmp = image_name_path.replace('sv_degree_960_720','ss_rgb')
        if ".jpg" in ss_rgb_tmp:
            ss_rgb_tmp = ss_rgb_tmp.replace(".jpg",".png")
        elif ".jpeg" in ss_rgb_tmp:
            ss_rgb_tmp = ss_rgb_tmp.replace(".jpeg",".png")
            
        # 检查文件是否存在
        if not os.path.exists(ss_rgb_tmp):
            continue

        ss_rgb_tmp_image = Image.open(ss_rgb_tmp)
        
        tmp = image_name_path.replace('sv_degree_960_720','ss_mask')
        folder_path = os.path.dirname(tmp)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if ".jpg" in tmp:
            tmp = tmp.replace(".jpg",".png")
        elif ".jpeg" in tmp:
            tmp = tmp.replace(".jpeg",".png")
        Image.blend(ss_rgb_tmp_image , pil_image, 0.3).save(tmp)

if __name__ == "__main__":
    # 街景文件夹
    input_folder = r'E:\work\sv_renleihuoshifen\sv_degree_960_720'
    seg_cal(input_folder)


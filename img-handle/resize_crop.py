from PIL import Image
import os
import Equirec2Perspec as E2P 
import cv2
import os  
from tqdm import tqdm
from PIL import Image  
import numpy as np  

def resize_imgs(input_dir):

    # 定义图片文件类型  
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')  
        
    # 遍历输入文件夹中的所有图片文件，并进行处理
    img_paths = []
    roots = []
    img_names = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
                roots.append(root)

    for i,image_path in enumerate(tqdm(img_paths)): 
        # 判断文件是否为图片类型  
        if image_path.lower().endswith(image_types):
            if i < 0:
                continue
            if i >= 111:
                continue

            try:
                image_path_save = image_path.replace('sv_pan_zoom3_fixedBlack','sv_pan_zoom3_fixedBlack_resize')
                if os.path.exists(image_path_save):
                    continue
                
                img = Image.open(image_path)
                img_resized = img.resize((4096, 2048))

                folder_path = os.path.dirname(image_path_save)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                img_resized.save(image_path_save)
           
            except Exception as e:
                print(e)

# ------------Main Function -------------------
if __name__ == "__main__":
    input = r'Y:\GOA-AIGC\02-Model\安装包\temp\sv_pan_zoom3_fixedBlack'
    resize_imgs(input)

print("所有图片已处理并保存到输出文件夹。")


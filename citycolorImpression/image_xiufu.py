import os

from PIL import Image, ImageEnhance  
import numpy as np  

# 文件夹路径
folder_path = r'E:\sv\huaian\test_xiufu' # 需要分析的文件夹路径
# folder_out_path = r'E:\sv\huaian\extract_arch_main_color' # 保存文件结果的文件夹路径

img_paths = []
img_names = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

for i in range(len(img_paths)):
    img = Image.open(img_paths[i])
    enhancer = ImageEnhance.Brightness(img)  
    enhanced_img = enhancer.enhance(2.0)  
    
    # 保存修复后的图像  
    enhanced_img.save(img_paths[i].replace('.png', '_xiufu.png'))




    
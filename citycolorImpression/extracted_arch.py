import numpy as np  
from PIL import Image  
import os
from tqdm import tqdm

def extracted_arch(img_paths,img_names):
    for i,img_path in enumerate(tqdm(img_paths)):

        file_path = os.path.join(img_path, img_names[i])
        # 加载灰度图和RGB色彩图  
        grey_image_path = file_path.replace('.jpg','.png').replace('degree','sv_grey')
        if not os.path.isfile(file_path):
            continue
        if not os.path.isfile(grey_image_path):
            continue
        grey_image = Image.open(grey_image_path).convert("L")  
        rgb_image = Image.open(file_path)  
        
        # 将图像转换为NumPy数组  
        gray_array = np.array(grey_image)  
        rgb_array = np.array(rgb_image)  

        # 创建一个全零数组，用于存放提取的像素  
        extracted_array = np.zeros_like(rgb_array) 
        extracted_array[:] = 255
        # 使用布尔索引将满足条件的像素值填入提取数组
        index_np = gray_array != 4 # 提取不是树的所有元素
        # 剔除建筑存在为0的图像
        if index_np.sum() == 0:
            continue
        extracted_array[index_np] = rgb_array[index_np]  
        # 确保提取数组的数据类型为uint8  
        extracted_array = extracted_array.astype(np.uint8)  
        
        # 将提取的数组转换回图像  
        extracted_image = Image.fromarray(extracted_array)  
        
        # 保存提取的图像  
        extracted_image.save(file_path.replace('degree','sv_arch'))

if __name__ == "__main__":

    img_paths = []
    img_names = []
    image_folder =r'f:\build\degree'

    folder_path = image_folder.replace('degree','sv_arch')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for root, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png"):
                img_paths.append(root)
                img_names.append(file)

    extracted_arch(img_paths,img_names)


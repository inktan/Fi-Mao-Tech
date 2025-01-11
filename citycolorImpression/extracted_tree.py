import numpy as np  
from PIL import Image  
import os
from tqdm import tqdm

def extracted_arch(img_paths,img_names):
    for i,img_path in enumerate(tqdm(img_paths)):

        file_path = os.path.join(img_path, img_names[i])
        grey_image_path = os.path.join(img_path, img_names[i])
        # 加载灰度图和RGB色彩图
        if ".jpg" in file_path:
            grey_image_path = file_path.replace(".jpg",".png")
        elif ".jpeg" in file_path:
            grey_image_path = file_path.replace(".jpeg",".png")

        grey_image_path = grey_image_path.replace('degree','sv_grey')

        if not os.path.isfile(file_path):
            continue
        if not os.path.isfile(grey_image_path):
            continue

        rgb_image = Image.open(file_path)  
        # 获取图像的宽度和高度  
        width, height = rgb_image.size  
        # 计算总像素数量  
        total_pixels = width * height  
        # 如果像素数量大于指定的最大值，进行缩放  
        max_pixels = 1000000 # 4g显存可以跑4000000
        if total_pixels > max_pixels:  
            # 计算缩放比例  
            scale = (max_pixels / total_pixels) ** 0.5  
            # 计算新的宽度和高度  
            new_width = int(width * scale)  
            new_height = int(height * scale)  
            # 创建一个新的缩放后的图像  
            rgb_image = rgb_image.resize((new_width, new_height))

        grey_image = Image.open(grey_image_path).convert("L")  
        
        # 将图像转换为NumPy数组  
        gray_array = np.array(grey_image)  
        rgb_array = np.array(rgb_image)  

        # 创建一个全零数组，用于存放提取的像素  
        extracted_array = np.zeros_like(rgb_array) 
        extracted_array[:] = 255
        # 使用布尔索引将满足条件的像素值填入提取数组
        index_np = (gray_array == 4) | (gray_array == 17) | (gray_array == 66) #提取所有的树
        # 剔除建筑存在为0的图像
        if index_np.sum() == 0:
            continue
        extracted_array[index_np] = rgb_array[index_np]  
        # 确保提取数组的数据类型为uint8  
        extracted_array = extracted_array.astype(np.uint8)  
        
        # 将提取的数组转换回图像  
        extracted_image = Image.fromarray(extracted_array)  
        
        # 保存提取的图像  
        file_path=file_path.replace('degree','sv_tree')
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        extracted_image.save(file_path)

if __name__ == "__main__":

    img_paths = []
    img_names = []
    image_folder =r'F:\plant_color\degree'

    for root, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png"):
                img_paths.append(root)
                img_names.append(file)

    extracted_arch(img_paths,img_names)


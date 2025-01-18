import numpy as np  
from PIL import Image  
import os
from tqdm import tqdm

def extracted_arch(ss_rgb_img_paths,ss_rgb_image_folder,sv_image_folder,sv_tree_folder):
    for i,ss_rgb_image_path in enumerate(tqdm(ss_rgb_img_paths)):

        sv_image_path = ss_rgb_image_path.replace(ss_rgb_image_folder,sv_image_folder).replace('png','jpg')
        if not os.path.isfile(sv_image_path):
            continue

        sv_image = Image.open(sv_image_path).convert('RGB')
        # 获取图像的宽度和高度  
        width, height = sv_image.size  
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
            sv_image = sv_image.resize((new_width, new_height))

        ss_rgb_image = Image.open(ss_rgb_image_path).convert('RGB')
        
        # 将图像转换为NumPy数组  
        ss_rgb_array = np.array(ss_rgb_image)  
        sv_array = np.array(sv_image)  

        # 创建一个全白数组（所有值为255），用于存放提取的像素（如果不需要初始化为255，可以省略这一步）
        extracted_array = np.full_like(sv_array, 255)
        # 定义要检查的颜色，注意这里不需要转换为列表
        colors_to_ignore = np.array([[4, 200, 3], [4, 250, 7]])
        
        # 创建一个形状为 (height, width, num_colors) 的布尔数组，表示每个像素是否与每个颜色匹配
        matches = (ss_rgb_array[:, :, None, :] == colors_to_ignore[None, None, :, :]).all(axis=3)
        # 找出每个像素是否匹配任何颜色
        ignore_mask = matches.any(axis=2)
        
        # 使用布尔索引来更新extracted_array
        extracted_array[ignore_mask] = sv_array[ignore_mask]
        # 将提取的数组转换回图像  
        extracted_image = Image.fromarray(extracted_array)  
        # 保存提取的图像  
        file_path=ss_rgb_image_path.replace(ss_rgb_image_folder,sv_tree_folder)
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        extracted_image.save(file_path)

if __name__ == "__main__":

    ss_rgb_img_paths = []
    ss_rgb_img_names = []
    # 语义分割色块路径
    ss_rgb_image_folder =r'D:\BaiduNetdiskDownload\sv_j_ran\temp\ss_suzhou_test\ss_rgb'

    for root, dirs, files in os.walk(ss_rgb_image_folder):
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(root, file)
                ss_rgb_img_paths.append(file_path)
                ss_rgb_img_names.append(file)
                
    # 街景图像文件路径
    sv_image_folder =r'D:\BaiduNetdiskDownload\sv_j_ran\temp\sv_suzhou_test'
    sv_tree_folder =r'D:\BaiduNetdiskDownload\sv_j_ran\temp\sv_tree'

    extracted_arch(ss_rgb_img_paths,ss_rgb_image_folder,sv_image_folder,sv_tree_folder)


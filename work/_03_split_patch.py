# -*- coding: utf-8 -*-

import os
from PIL import Image
from tqdm import tqdm

def crop_images(image_info):
    # 打开原始图像
    original_image = Image.open(image_info[0])

    # 获取原始图像的宽度和高度
    width, height = original_image.size

    # 计算每个子图像的水平和垂直数量
    num_horizontal = image_info[4]
    num_vertical = image_info[3]

    patch_width = width//image_info[4]
    patch_height = height//image_info[3]

    # 裁剪图像
    for j in range(num_vertical):
        for i in range(num_horizontal):
            left = i * patch_width
            upper = j * patch_height
            right = left + patch_width
            lower = upper + patch_height
            cropped_image = original_image.crop((left, upper, right, lower))
            output_path = f"{image_info[2]}/{image_info[1]}_part_{i}_{j}.png" 
            cropped_image.save(output_path)

def main(image_folder, output_dir,col_patch_num, row_patch_num):
    '''
    切割图片为瓦片
    '''

    for i,j,k in os.walk(image_folder):
        for image_name in tqdm(k):
            image_name_path = '{}/{}'.format(i,image_name)
            if not image_name.endswith('.jpg') and image_name.endswith('.png') and  image_name.endswith('.jpeg'):
                continue
            
            image_info=[image_name_path,image_name[:-4],output_dir,row_patch_num,col_patch_num]
            crop_images(image_info)

    print('split end')

if __name__ == "__main__":
    
    # 设置图片分割瓦片的水平和垂直数量
    col_patch_num = 4
    row_patch_num = 4

    # 被分割图片文件夹
    image_folder=r"E:\work\spatio_evo_urbanvisenv_svi\patch_kmeans\sv_original\sv_grey"
    # 保存图片瓦片的文件夹
    output_dir= image_folder.replace('sv_original','sv_split')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    main(image_folder, output_dir,col_patch_num, row_patch_num)

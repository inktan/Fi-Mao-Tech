# -*- coding: utf-8 -*-
from PIL import Image
import os

def resize_image(image_path, target_width):
    '''
    缩放
    '''
    # 打开图像
    image = Image.open(image_path)

    # 获取原始图像的宽度和高度
    width, height = image.size

    # 判断宽度是否为目标宽度
    if width > target_width:
        # 计算等比例缩放后的高度
        target_height = int(height * (target_width / width))

        # 进行缩放
        resized_image = image.resize((target_width, target_height))

        # 返回缩放后的图像
        return resized_image

    # 如果宽度已经是目标宽度，则直接返回原始图像
    return image
def crop_image(image,target_height):
    '''
    裁剪
    '''
    # 获取原始图像的宽度和高度
    width, height = image.size

    # 判断高度是否大于 400 像素
    if height > target_height:
        # 计算裁剪区域的上下边界
        top = height // 2 - target_height*0.5
        bottom = height // 2 + target_height*0.5
        # 进行裁剪
        cropped_image = image.crop((0, top, width, bottom))
        # 返回裁剪后的图像
        return cropped_image
    # 如果高度不大于 400 像素，则直接返回原始图像
    return image
def main(target_width, target_height, image_folder, output_dir):
    '''
    运行
    '''
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)  

    for i,j,k in os.walk(image_folder):
        for image_name in k:
            image_path = '{}/{}'.format(i,image_name)

            if not image_name.endswith('.jpg') and  image_name.endswith('.png') and  image_name.endswith('.jpeg'):
                continue
        
            resized_image = resize_image(image_path, target_width)
            cropped_image = crop_image(resized_image,target_height)
            cropped_image.save('{}/{}'.format(output_dir,image_name))

if __name__ == "__main__":
    # 缩放与裁剪图像的宽度和高度
    target_width = 800
    target_height = 400
    # 需要裁剪与缩放的图片文件夹
    image_folder= 'E:\sv\work\sv/00-sv'
    # 保存缩放与裁剪后的图片文件夹
    output_dir= r'E:\sv\work\sv/01-resize'

    main(target_width, target_height, image_folder, output_dir)
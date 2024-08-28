# from PIL import Image
# import json

# 打开一个名为'image.jpg'的图片文件
# path = r'd:\Ai-clip-seacher\Ai_Basic_Architecture_Library\Architizer\cf-moller-architects\National Maritime Museum London - the Sammy Ofer Wing by Malcolm Reading Consultants, Purcell Architects, Churchman Landscape, C.F. Møller Architects - Architizer\1ace41e7.jpg'
# image = Image.open(path)

# 显示图片
# image.show()
# path = r'\\?\D:\Ai-clip-seacher\Ai_Basic_Architecture_Library\Architizer\cf-moller-architects\National Maritime Museum London - the Sammy Ofer Wing by Malcolm Reading Consultants, Purcell Architects, Churchman Landscape, C.F. Møller Architects - Architizer\project_info.json'

# Create and write to the JSON file
# with open(path, 'w') as json_file:
#     json.dump({'json_content':123}, json_file)

# import json

# file_path = r'd:\Ai-clip-seacher\Ai_Basic_Architecture_Library\archcollege\西山智谷——北京协同创新园 _ CAA建筑事务所\project_info.json'

# with open(file_path, 'r') as file:
#     data = json.load(file)

# print(data['project_info']['path_name_guid'])
# 批量新建文件夹，以"goa_"开头，假设我们要创建10个这样的文件夹
# import os

# folder_prefix = r"D:\Ai-clip-seacher\Ai_Basic_Architecture_Library_01\goa_"
# number_of_folders = 100
# folder_base_path = "."

# 创建文件夹
# for i in range(1, number_of_folders + 1):
#     folder_name = f"{folder_prefix}{i}"
#     os.makedirs(os.path.join(folder_base_path, folder_name), exist_ok=True)

# 返回创建的文件夹列表
# created_folders = [f"{folder_prefix}{i}" for i in range(1, number_of_folders + 1)]
# created_folders

# for i in range(100000000):
#     print(i//5000+1)
# import numpy as np
# from PIL import Image

# def count_dark_black_pixels(image_path, threshold=250):
    # 打开图片
    # with Image.open(image_path) as img:
        # 将图片转换为numpy数组
        # img_array = np.array(img)
        # 检查图片是否为灰度图
        # if len(img_array.shape) == 2:
            # 灰度图只有一个颜色通道
        #     dark_black_pixels = np.sum(img_array < threshold)
        # else:
            # 彩色图有三个颜色通道
            # sum_rgb = img_array.sum(axis=2)
            # dark_black_pixels = np.sum(sum_rgb < threshold*3)
        # 获取图片的宽度和高度
        # width, height = img.size
        # 计算总像素数
        # total_pixels = width * height
        # 计算深灰色像素的比率
#         dark_gray_pixel_ratio = dark_black_pixels / total_pixels
#         return dark_black_pixels,dark_gray_pixel_ratio
    
# image_path = r'd:\Ai-clip-seacher\AiArchLib\goa_4\0CUE3xllwi\1_1523962207317947.bmp'  # 替换为你的图片路径
# dark_black_pixels,dark_gray_pixel_ratio = count_dark_black_pixels(image_path)
# print(f'深灰色像素占比: {dark_black_pixels}: {dark_gray_pixel_ratio:.2%}')
# 第一个列表，决定了元素的排序顺序  
order_list = [20, 12, 25, 69]  
  
# 创建一个从元素到索引的映射字典  
order_dict = {val: idx for idx, val in enumerate(order_list)}  
  
# 需要排序的元组列表  
tuples_list = [(20, 'qwe'), (25, 'asd'), (12, 'zxc'), (69, 'qaz')]  
tuples_list = [(20, 'qwe'), (25, 'asd'), (69, 'qaz')]  
  
# 使用列表推导式和映射字典来排序  
sorted_tuples = sorted(tuples_list, key=lambda x: order_dict[x[0]])  
  
# 输出排序后的元组列表  
print(sorted_tuples)


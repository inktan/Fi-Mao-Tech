# import os
# from PIL import Image

# # 设置源文件夹和目标文件夹路径
# source_folder = 'E:\work\sv_quchetou20240902\sv'  # 替换为您的源文件夹路径
# target_folder = 'E:\work\sv_quchetou20240902\sv_01'  # 替换为您的目标文件夹路径

# # 确保目标文件夹存在
# if not os.path.exists(target_folder):
#     os.makedirs(target_folder)

# # 遍历源文件夹中的所有文件
# for filename in os.listdir(source_folder):
#     if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
#         # 图片文件的完整路径
#         image_path = os.path.join(source_folder, filename)
#         # 打开图片
#         with Image.open(image_path) as image:
#             # 裁剪图片高度为1300像素
#             height = 1300
#             if image.height > height:
#                 # 计算裁剪区域
#                 crop_area = (0, 0, image.width , height)
#                 # 裁剪图片
#                 cropped_image = image.crop(crop_area)
#             else:
#                 # 如果图片高度小于1300像素，则不裁剪
#                 cropped_image = image
            
#             # 保存裁剪后的图片到目标文件夹
#             cropped_image.save(os.path.join(target_folder, filename))

# print("裁剪完成")
# import json

# # 确保你的JSON文件路径是正确的
# file_path = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'

# # 使用with语句确保文件正确关闭
# with open(file_path, 'r', encoding='utf-8') as file:
#     data05 = json.load(file)

# # 现在 data 变量包含了文件中的JSON数据
# # print(data05)
# print(len(data05.keys()))

import os  
import json  
  
def load_json_files_from_folder(folder_path):  
    """  
    加载指定文件夹中的所有JSON文件，合并它们的内容到一个字典中，  
    并自动处理重复的key。  
    """  
    merged_data = {}  
    for filename in os.listdir(folder_path):  
        if filename.endswith(".json"):  
            file_path = os.path.join(folder_path, filename)  
            with open(file_path, 'r', encoding='utf-8') as file:  
                data = json.load(file)  
                # 更新merged_data，如果key已存在，则不会改变（因为字典键唯一）  
                merged_data.update(data)  
    return merged_data  
  
def save_dict_to_json(data, output_file):  
    """  
    将字典保存到JSON文件中。  
    """  
    with open(output_file, 'w', encoding='utf-8') as file:  
        json.dump(data, file, ensure_ascii=False, indent=4)  
  
# 使用函数  
folder_path = r'E:\work\sv_chenlong20240907'  # 更改为你的JSON文件所在文件夹的路径  
output_file = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'  # 合并后的JSON文件保存路径  
  
merged_data = load_json_files_from_folder(folder_path)  
save_dict_to_json(merged_data, output_file)  
  
print(f"数据已合并并保存到 {output_file}")
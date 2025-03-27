import os
import csv

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_拉萨'

# rate_lists = []
# image_ss_csv = r'E:\work\sv_nadingzichidefangtoushi\points_15m\sv_panoid_info\sv_pan_zoom3.csv'
# with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(rate_lists)

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            
            # rate_list =[file] 
            # rate_lists.append(rate_list)

            # with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
            #     writer = csv.writer(f)
            #     writer.writerows(rate_lists)
            # rate_lists = []

print(len(img_names))
# for i in img_paths:
#     print(i)

# 每个点4张街景，共1259360张街景

# ids = []
# for file_name in img_names:
#     # 使用'_'分割文件名
#     parts = file_name.split('_')
#     # 假设ID是分割后的第一个部分
#     id_ = parts[0]
#     # 将ID添加到列表中
#     ids.append(id_)

# len(ids)

# number_list = []
# for s in img_names:
#     try:
#         # 尝试分割并转换
#         number = int(s.split("_")[0])
#         number_list.append(int(number))
#     except (IndexError, ValueError):
#         # 如果分割失败或转换失败，跳过该字符串
#         print(f"跳过无效字符串: {s}")

# # print(number_list)

# # 生成从 1 到 21515 的整数列表
# integer_list = list(range(1, 21516))

# # 输出结果
# # print(integer_list)

# # 使用集合差集操作找到 list1 中存在但 list2 中不存在的元素
# result = list(set(integer_list) - set(number_list))

# # 输出结果
# print(len(result))
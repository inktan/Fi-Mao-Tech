# import os
# import csv

# img_paths = []
# img_names = []
# accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

# folder_path = r'Y:\GOA-AIGC\02-Model\安装包\temp\sv_degree_960_720'

# for root, dirs, files in os.walk(folder_path):
#     for file in files:
#         if file.endswith(accepted_formats):
#             file_path = os.path.join(root, file)
#             img_paths.append(file_path)
#             img_names.append(file)

# print(len(img_names))
# # for i in img_paths:
# #     print(i)


import os

folder_path = r"F:\GoogleDrive\wt282532\我的云端硬盘\sv_points_surrounding_times\sv_pan_zoom3 (1)"  # 替换为你的文件夹路径
subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

print(f"共有 {len(subfolders)} 个子文件夹：")
# for folder in subfolders:
#     print(folder)
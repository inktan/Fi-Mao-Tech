import os
import csv

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'Y:\GOA-AIGC\02-Model\安装包\temp\sv_degree_960_720'

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

print(len(img_names))
# for i in img_paths:
#     print(i)

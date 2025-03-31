import os
import shutil
import os
import csv

# source_dir = r"F:\work\sv_ran\sv_pan_fisheye\surrounding_fixedBlack"
# target_dir = r"F:\work\sv_ran\sv_pan_fisheye\sv_points_surrounding"

# source_dir = r"F:\work\sv_ran\sv_pan\surrounding_fixedBlack"
# target_dir = r"F:\work\sv_ran\sv_pan\sv_points_surrounding"

# # 确保目标文件夹存在
# os.makedirs(target_dir, exist_ok=True)

# # 遍历源文件夹中的所有文件
# for filename in os.listdir(source_dir):
#     if filename.lower().endswith('.jpg'):
#         source_path = os.path.join(source_dir, filename)
#         target_path = os.path.join(target_dir, filename)
#         try:
#             # 移动文件
#             shutil.move(source_path, target_path)
#             print(f"Moved: {filename}")
#         except Exception as e:
#             continue

# print("All JPG files have been moved.")

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'F:\work\sv_ran\sv_pan\sv_points_ori_times\sv_pan_zoom3_fixedBlack'
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            
            source_path = file_path
            target_path = file_path.replace('sv_pan_zoom3_fixedBlack','sv_pan_zoom3')
            try:
                # 移动文件
                shutil.move(source_path, target_path)
                print(f"Moved: {source_path}")
            except Exception as e:
                continue

print(len(img_names))






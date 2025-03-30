import os
import shutil

# source_dir = r"F:\work\sv_ran\ss_rgb"
# target_dir = r"F:\work\sv_ran\ss_rgb\sv_points_surrounding"

source_dir = r"F:\work\sv_ran\sv_pan\sv_points_ori\sv_pan_zoom3"
target_dir = r"F:\work\sv_ran\sv_pan\sv_points_ori"

# 确保目标文件夹存在
os.makedirs(target_dir, exist_ok=True)

# 遍历源文件夹中的所有文件
for filename in os.listdir(source_dir):
    if filename.lower().endswith('.jpg'):
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)
        try:
            # 移动文件
            shutil.move(source_path, target_path)
            print(f"Moved: {filename}")
        except Exception as e:
            continue

print("All JPG files have been moved.")
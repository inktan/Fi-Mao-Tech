import os  
import shutil  

target_folders = [r'E:\work\sv_levon\sv_points_1028\sv_pan_new',r'E:\work\sv_levon\sv_points_1028\sv_pan_2017',]

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path_list =[r'E:\work\sv_levon\sv_points_1028\sv_pan']
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
                    
for file_path in img_paths:
    # print(file_path)
    year_ = int(file_path[-10:-6])
    if year_ > 2017: 
        file_name = os.path.basename(file_path)
        target_file_path = os.path.join(target_folders[0], file_name)
        shutil.move(file_path, target_file_path)
    if year_ < 2018:
        file_name = os.path.basename(file_path)
        target_file_path = os.path.join(target_folders[1], file_name)
        shutil.move(file_path, target_file_path)

print('Finished processing.')





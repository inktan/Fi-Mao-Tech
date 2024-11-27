import os  
from tqdm import tqdm
from PIL import Image
import os  
import shutil  

source_folder_new = r'E:\work\sv_j_ran\sv_pan'
# source_folder_2017 = r'E:\work\sv_levon\sv_points_1028\sv_pan_2017'
img_paths_new = []
img_names_new = []
# img_paths_2017 = []
# img_names_2017 = []

accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(source_folder_new):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths_new.append(file_path)
            img_names_new.append(file)

for file_path in img_paths_new:
    file_name = os.path.basename(file_path)
    print(file_name[-6:-4])


# for root, dirs, files in os.walk(source_folder_2017):
#     for file in files:
#         if file.endswith(accepted_formats):
#             file_path = os.path.join(root, file)
#             img_paths_2017.append(file_path)
#             img_names_2017.append(file)

# count = 0
# for i in range(1, 10000):
#     img_name_new = [name for name in img_names_new if name.startswith(f"{i}_")]
    # img_name_2017 = [name for name in img_names_2017 if name.startswith(f"{i}_")]

    # if len(img_name_2017) == 2:
    #     print(img_name_2017)

    # if len(img_name_new) == 0 and len(img_name_2017) == 1:
    # if len(img_name_new) == 0 and len(img_name_2017) == 1:
        # print(img_name_new)
        # print(img_name_2017)
        # count += 1
        # os.remove(r'E:\work\sv_levon\folder-01\sv_degree_hor_2017/'+img_name_2017[0])
        # shutil.copy2(source_folder_2017 +'\\'+ img_name_2017[0], r'E:\work\sv_levon\sv_points_1028\sv_pan_temp'+'/')

# print(count)


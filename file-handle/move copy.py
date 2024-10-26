import os  
import shutil  

months01 = ['03.', '04.', '05.']
months02 = ['06.', '07.', '08.']
months03 = ['09.', '10.', '11.']
months04 = ['01.', '02.', '12.']

target_folders = [r'E:\work\sv_amzon\siji\春',r'E:\work\sv_amzon\siji\夏',r'E:\work\sv_amzon\siji\秋',r'E:\work\sv_amzon\siji\冬',]

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path_list =[r'E:\work\sv_amzon\sv_amazon_points']
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
                    
for file_path in img_paths:
    print(file_path)
    if any(month in file_path for month in months01):  
        file_name = os.path.basename(file_path)  
        target_file_path = os.path.join(target_folders[0], file_name)  
        shutil.move(file_path, target_file_path)  
    if any(month in file_path for month in months02):  
        file_name = os.path.basename(file_path)  
        target_file_path = os.path.join(target_folders[1], file_name)  
        shutil.move(file_path, target_file_path)  
    if any(month in file_path for month in months03):  
        file_name = os.path.basename(file_path)  
        target_file_path = os.path.join(target_folders[2], file_name)  
        shutil.move(file_path, target_file_path)  
    if any(month in file_path for month in months04):  
        file_name = os.path.basename(file_path)  
        target_file_path = os.path.join(target_folders[3], file_name)  
        shutil.move(file_path, target_file_path)  

print('Finished processing.')
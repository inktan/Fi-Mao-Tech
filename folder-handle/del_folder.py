import shutil  
from tqdm import tqdm
import os  
  
folder_path = r'F:\sv_shanghai\sv_degree_960_720'  
  
try:
    if os.path.exists(folder_path):  
        shutil.rmtree(folder_path)  
        print(f"文件夹 '{folder_path}' 已成功删除。")
    else:  
        print(f"文件夹 '{folder_path}' 不存在。")
except Exception as e:
    print(f"删除文件时出错: {e}")
    
# try:
#     if os.path.exists(folder_path):  
#         shutil.rmtree(folder_path)  
#         print(f"文件夹 '{folder_path}' 已成功删除。")
#     else:  
#         print(f"文件夹 '{folder_path}' 不存在。")
# except Exception as e:
#     print(f"删除文件时出错: {e}")

# def del_files(img_paths):
#     for i, file_path in enumerate(tqdm(img_paths)):
#         try:
#             os.remove(file_path)
#             print(f"文件 {file_path} 已被删除。")
#         except Exception as e:
#             print(f"删除文件时出错: {e}")

# def main():
    
#     # 图片库所在文件夹
#     folder_path_list =[
        
#         r'F:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_ss_mask',# 01
#         r'F:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_ss_rgb',# 02

#         ]
    # 图片库所在文件夹
    folder_path_list =[
        folder_path,# 02\
        r'F:\sv_shanghai\sv_degree_960_720',
        r'F:\sv_shanghai\sv_pan'
        ]

#     # 获取文件夹中的所有文件信息(含多级的子文件夹)
#     img_paths = []
#     img_names = []
#     # accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

#     for folder_path in folder_path_list:
#         for root, dirs, files in os.walk(folder_path):
#             for file in files:
#                 # if file.endswith(accepted_formats):
#                     file_path = os.path.join(root, file)
#                     img_paths.append(file_path)
#                     img_names.append(file)

#     print(len(img_paths))
#     del_files(img_paths)

# if __name__ == '__main__':
#     print('a01')
#     main()



import shutil  
from tqdm import tqdm
import os  
  
base_destination = r'D:\work'

# 生成所有文件夹名称
# folders = []
# for i in range(490000, 2340001, 10000):
#     folders.append(f"sv_pano_{i}_{i + 10000}")

# folder_paths = []

# for index, folder in enumerate(folders, 1):
#     dest_path = os.path.join(base_destination, folder)
#     folder_paths.append(dest_path)
    
folder_paths = [
   r'D:\work',
]

for folder_path in folder_paths:
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

def del_files(img_paths):
    for i, file_path in enumerate(tqdm(img_paths)):
        try:
            os.remove(file_path)
            # print(f"文件 {file_path} 已被删除。")
        except Exception as e:
            print(f"删除文件时出错: {e}")

def main():
    
    # 图片库所在文件夹
    folder_path_list =[
        # r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_林芝',# 02
        ]

    # 获取文件夹中的所有文件信息(含多级的子文件夹)
    img_paths = []
    img_names = []
    # accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")
    accepted_formats = (".png")

    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)

    print(len(img_paths))
    del_files(img_paths)

if __name__ == '__main__':
    print('a01')
    main()



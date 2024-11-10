import os  
import shutil

def is_empty_dir(dir_path):  
    """  
    检查目录是否为空  
    :param dir_path: 目录路径  
    :return: 如果目录为空则返回True，否则返回False  
    """  
    # 检查目录是否存在  
    if not os.path.isdir(dir_path):  
        return False  
    # os.listdir列出目录下的所有文件和子目录名，然后检查这个列表是否为空  
    return len(os.listdir(dir_path)) == 0  
  
def is_empty_images(dir_path):
    
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
    return len(img_paths) == 0  
  
def delete_empty_images(dir_path):  
    """  
    如果目录为空，则删除该目录  
    :param dir_path: 目录路径  
    """  
    if is_empty_images(dir_path):  
        shutil.rmtree(dir_path)
        # os.rmdir(dir_path)  
        print(f"已删除空目录: {dir_path}")

def delete_empty_dir(dir_path):  
    """  
    如果目录为空，则删除该目录  
    :param dir_path: 目录路径  
    """  
    if is_empty_dir(dir_path):  
        os.rmdir(dir_path)  
        print(f"已删除空目录: {dir_path}")
    # else:  
    #     print(f"目录 {dir_path} 不为空，无法删除。")  
  
current_directory = r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus'
entries = os.listdir(current_directory)

folders = [os.path.join(current_directory, entry) for entry in entries if os.path.isdir(os.path.join(current_directory, entry))]  
  
# 打印出所有一级文件夹的名称  
print(len(folders))
for folder in folders:
    entries = os.listdir(folder)
    folders_02 = [os.path.join(folder, entry) for entry in entries if os.path.isdir(os.path.join(folder, entry))]  
    # 打印出所有一级文件夹的名称  
    print(len(folders_02))
    for folder_02 in folders_02:  
        # print(folder)
        # delete_empty_dir(folder_02)
        # print(folder)
        # delete_empty_dir(folder)
        # print(folder)
        delete_empty_images(folder_02)


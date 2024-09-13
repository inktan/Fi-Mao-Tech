import os  
  
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
  
def delete_empty_dir(dir_path):  
    """  
    如果目录为空，则删除该目录  
    :param dir_path: 目录路径  
    """  
    if is_empty_dir(dir_path):  
        # os.rmdir(dir_path)  
        print(f"已删除空目录: {dir_path}")  
    # else:  
    #     print(f"目录 {dir_path} 不为空，无法删除。")  
  
current_directory = r'D:\BaiduNetdiskDownload\sv_j_ran\sv_google_20240903\sv_pan'
entries = os.listdir(current_directory)  
folders = [entry for entry in entries if os.path.isdir(os.path.join(current_directory, entry))]  
  
# 打印出所有一级文件夹的名称  
print(len(folders))
for folder in folders:  
    # print(folder)
    delete_empty_dir(folder)


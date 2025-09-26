import os

def count_files_in_subfolders(root_dir):
    # 检查根目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误：目录 '{root_dir}' 不存在")
        return
    
    # 检查是否为有效目录
    if not os.path.isdir(root_dir):
        print(f"错误：'{root_dir}' 不是一个有效的目录")
        return
    
    # 获取根目录下的所有子文件夹
    subfolders = [f for f in os.listdir(root_dir) 
                 if os.path.isdir(os.path.join(root_dir, f))]
    
    if not subfolders:
        print(f"在 '{root_dir}' 中未找到任何子文件夹")
        return
    
    all_file_count = 0
    # 统计每个子文件夹中的文件数量
    print(f"根目录: {root_dir}\n")
    print("子文件夹文件数量统计:")
    print("-" * 50)
    
    for folder in subfolders:
        folder_path = os.path.join(root_dir, folder)
        # 统计该文件夹中的文件数量（不包括子文件夹）
        file_count = len([f for f in os.listdir(folder_path) 
                         if os.path.isfile(os.path.join(folder_path, f))])
        
        all_file_count+=file_count
        
        print(f"{folder}: {file_count} 个文件")
    
    print("-" * 50)
    print(f"总计 {len(subfolders)} 个子文件夹")
    print(f"总计 {all_file_count} 个文件")

if __name__ == "__main__":
    # 目标根目录
    root_directory = r"E:\svi_panorama"
    count_files_in_subfolders(root_directory)
    
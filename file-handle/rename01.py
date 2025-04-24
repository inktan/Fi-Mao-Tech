import os

# 文件夹路径
folder_path = r'E:\work\sv_quanzhou\sv_pan'

# 获取文件夹中的所有文件
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# 遍历文件并重命名
for index, filename in enumerate(files):
    # 构造新的文件名
    new_filename = f"{index}_{filename}"
    
    # 原始文件的完整路径
    old_file_path = os.path.join(folder_path, filename)
    
    # 新文件的完整路径
    new_file_path = os.path.join(folder_path, new_filename)
    
    # 重命名文件
    os.rename(old_file_path, new_file_path)
    
    # print(f"Renamed: {filename} -> {new_filename}")

print("All files have been renamed successfully!")
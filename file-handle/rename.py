import os

# 指定文件夹路径
folder_path = r'E:\work\sv_juanjuanmao\指标计算\业态混合度'


# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件扩展名是否为.csv
    if filename.endswith('.csv'):
        # 使用下划线分割文件名，并获取第一个部分
        first_part = filename.split('_')[0]
        # 生成新的文件名，这里只保留第一个字符串，并加上.csv扩展名
        # 注意：如果原始文件名中不包含下划线，first_part将是整个文件名
        # 如果你想要避免文件名冲突，可以考虑添加一些唯一标识符（如时间戳）
        new_filename = f"{first_part}.csv"
        # 构建完整的旧文件路径和新文件路径
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        
        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: {filename} -> {new_filename}")
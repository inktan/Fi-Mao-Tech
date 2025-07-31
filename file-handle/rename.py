import os

# 设置目标文件夹路径（替换为你的文件夹路径）
folder_path = r"F:\立方数据\上海poi\上海市2021\shp"  # 例如：r"C:\Users\YourName\Documents\Files"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if "上海市_" in filename:
        # 构造新文件名（移除 "上海市_"）
        new_filename = filename.replace("上海市_", "")
        
        # 获取旧文件和新文件的完整路径
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        
        # 重命名文件
        os.rename(old_file, new_file)
        print(f"Renamed: {filename} -> {new_filename}")

print("所有文件重命名完成！")





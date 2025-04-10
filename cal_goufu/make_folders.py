import os

# 基础路径
base_path = r"E:\work\sv_goufu\MLP"

# 要创建的年份范围 (1998-2023)
start_year = 1998
end_year = 2023

# 创建文件夹
for year in range(start_year, end_year + 1):
    # 格式化年份为两位数字 (98, 99, 00, 01, ..., 23)
    year_str = f"year{str(year)[2:]}"
    folder_path = os.path.join(base_path, year_str)
    
    # 如果文件夹不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"已创建文件夹: {folder_path}")
    else:
        print(f"文件夹已存在: {folder_path}")

print("\n文件夹创建完成！")
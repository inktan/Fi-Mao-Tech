import os
import pandas as pd

# 指定文件夹路径（替换为你的目标文件夹）
folder_path = r"E:\work\sv_zhaolu\roads"  # 例如："./data"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith("_unique_Spatial_Balance.csv"):
        file_path = os.path.join(folder_path, filename)
        
        # 读取 CSV 文件
        df = pd.read_csv(file_path)
        
        # 检查是否有至少一列数据
        if not df.empty:
            # 获取当前第一列的列名
            first_col = df.columns[0]
            
            # 修改第一列的列名为 "index"
            df.rename(columns={first_col: "index"}, inplace=True)
            
            # 保存修改后的 CSV 文件（覆盖原文件）
            df.to_csv(file_path, index=False)
            
            print(f"已修改文件: {filename}，第一列 '{first_col}' 改为 'index'")
        else:
            print(f"文件 {filename} 无数据，跳过处理")

print("所有 CSV 文件处理完成！")
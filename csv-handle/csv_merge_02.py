import pandas as pd
import os

# 假设你的CSV文件都存放在一个指定的文件夹中
folder_path = r'E:\work\sv_nadingzichidefangtoushi'
output_file = r'E:\work\sv_nadingzichidefangtoushi\merged_coordinates.csv'

# 用于存储所有提取的经纬度数据的列表
all_data = []

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查是否包含longitude和latitude列
        if 'longitude' in df.columns and 'latitude' in df.columns:
            # 提取这两列数据，并添加到列表中
            all_data.append(df[['longitude', 'latitude']])

# 将所有提取的数据合并为一个DataFrame
merged_df = pd.concat(all_data, ignore_index=True)

# 将合并后的DataFrame保存为一个新的CSV文件
merged_df.to_csv(output_file, index=False)

print(f"合并后的经纬度数据已保存到 {output_file}")
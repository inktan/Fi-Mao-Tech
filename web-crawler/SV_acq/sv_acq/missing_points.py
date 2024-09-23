import os  
import pandas as pd  
  
# 读取CSV文件  
csv_file = r'e:\work\shixudian\shixu_.csv'  # 替换为你的CSV文件名  
df = pd.read_csv(csv_file)  
csv_ids = set(df['OBJECTID'])  # 假设第一列的名称为'id'  
# print(csv_ids)
  
# 列出文件夹中的文件并提取ID  
folder_path = r'E:\work\shixudian\sv\sv'  # 替换为你的文件夹路径  
file_ids = set()  
for file_name in os.listdir(folder_path):  
    if '_' in file_name:  
        file_id = file_name.split('_')[0]  
        file_ids.add(int(file_id))  
  
# 找出不存在的ID  
# missing_ids = csv_ids - file_ids  
  
# 筛选并保存CSV行  
# print(file_ids)
missing_rows = df[~df['OBJECTID'].isin(file_ids)]  
missing_rows.to_csv(r'e:\work\shixudian\missing_ids.csv', index=False)  # 保存为新的CSV文件

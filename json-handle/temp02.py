import json
file_path = r'e:\work\sv_chenlong20240907\id_panoramas_infos_02.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data05 = json.load(file)

# 现在 data 变量包含了文件中的JSON数据
# print(data05)
given_list = list(data05.keys())
given_list_int = [int(item) for item in given_list]

# print(data05.keys())
print(len(data05.keys()))
# print(list(data05.values()))

import pandas as pd

csv_file_path = r'e:\work\sv_chenlong20240907\RoadPoints_50m_unique.csv'
df = pd.read_csv(csv_file_path)

df['id'] = df['PointID'].astype(int)

filtered_df = df[~df['id'].isin(given_list_int)]

# 将筛选后的数据保存为新的CSV文件
output_csv_file_path = r'e:\work\sv_chenlong20240907\RoadPoints_50m_miss.csv'
filtered_df.to_csv(output_csv_file_path, index=False)

output_csv_file_path

  
  
  
  
  
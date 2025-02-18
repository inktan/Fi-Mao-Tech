import pandas as pd

# 读取csv文件
df = pd.read_csv(r'e:\work\sv_j_ran\points\data_coor_unique_500_circle.csv')

# 修改列名
df.rename(columns={'longitude_circle.1': 'latitude_circle'}, inplace=True)

# 保存修改后的DataFrame到新的csv文件
df.to_csv(r'e:\work\sv_j_ran\points\data_coor_unique_500_circle.csv', index=False)
import pandas as pd

# 读取并处理文件
input_csv = r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique01.csv'
df = pd.read_csv(input_csv)
# df = df[['FacCol_Vis', 'id']]
# df = df.drop(columns=['geometry'])
df = df.drop(columns=['osm_id_y','index'])

# df = pd.read_csv(input_csv).drop(['id', 'index'], axis=1, errors='ignore')

output_csv = input_csv
df.to_csv(output_csv, index=False)

import pandas as pd

# 读取并处理文件
input_csv = r'e:\work\sv_huammengmaomao\金门\_network01_10m_unique.csv'
df = pd.read_csv(input_csv)
# df = df[['FacCol_Vis', 'id']]
df = df.drop(columns=['geometry'])
# df = df.drop(columns=['osm_id_y','geometry'])

# df = pd.read_csv(input_csv).drop(['id', 'index'], axis=1, errors='ignore')

output_csv = input_csv
df.to_csv(output_csv, index=False)

import pandas as pd

# 读取并处理文件
input_csv = r'd:\work\sv_yj\sv_phoenix\merged_data_04.csv'

df = pd.read_csv(input_csv)
# df = df[['FacCol_Vis', 'id']]
# df = df.drop(columns=['geometry'])
df = df.drop(columns=['pano_lat','pano_lon','img_id'])

# df = pd.read_csv(input_csv).drop(['id', 'index'], axis=1, errors='ignore')

output_csv = r'd:\work\sv_yj\sv_phoenix\merged_data_05.csv'
df.to_csv(output_csv, index=False)

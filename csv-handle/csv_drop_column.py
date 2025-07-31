import pandas as pd

# 读取并处理文件
input_csv = r'e:\work\sv_xiufenganning\地理数据\harmony_results_01.csv'
df = pd.read_csv(input_csv)
df = df[['FacCol_Vis', 'id']]

# df = pd.read_csv(input_csv).drop(['id', 'index'], axis=1, errors='ignore')

output_csv = input_csv
df.to_csv(output_csv, index=False)

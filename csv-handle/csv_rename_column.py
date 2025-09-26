import pandas as pd

# 读取并处理文件
input_csv = r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_7.5_ifference_15.csv'
df = pd.read_csv(input_csv)

df = df.rename(columns={
    'osm_id_x': 'osm_id',
    })

print(df.columns)
print(df.head())

output_csv = input_csv
df.to_csv(output_csv, index=False)



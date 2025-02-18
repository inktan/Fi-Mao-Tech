import pandas as pd

# 读取Excel文件
df = pd.read_excel('e:\work\sv_renleihuoshifen\研究-指标.xlsx', engine='openpyxl')

# 打印id列的每一行数据
for index, row in df.iterrows():
    print(row['name'])
    # print(f"ID: {row['id']}, Data: {row}")

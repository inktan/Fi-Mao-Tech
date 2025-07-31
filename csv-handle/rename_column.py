import pandas as pd

# 读取csv文件
df = pd.read_csv(r'e:\work\sv_xiufenganning\地理数据\harmony_results_01.csv')

# 修改列名
df.rename(columns={'Hue STD (Normalized)': 'FacCol_Vis'}, inplace=True)

# 保存修改后的DataFrame到新的csv文件
df.to_csv(r'e:\work\sv_xiufenganning\地理数据\harmony_results_01.csv', index=False)
import pandas as pd

# 读取 Excel 文件
file_path = r"e:\work\sv_xiufenganning\20250815\类别情感03.xlsx"  # 替换为你的文件路径
df = pd.read_excel(file_path)

# result_df = df.groupby(['lon', 'lat'], as_index=False).mean()
result_df = df.groupby(["Unnamed", "地点", "地址"], as_index=False).sum()
# result_df = df.groupby(['id'], as_index=False).mean()

# 保存结果到新CSV文件
result_df.to_excel(r'e:\work\sv_xiufenganning\20250815\类别情感04.xlsx', index=False)

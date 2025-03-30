import pandas as pd

# 将以下路径替换为您的实际CSV文件路径
csvfilepath1 = r'f:\work\sv_ran\ss_01_surrounding_fixedBlack01.csv'  # 第一个CSV文件路径
csvfilepath2 = r'f:\work\sv_ran\ss_01.csv'  # 第二个CSV文件路径
newcsvfilepath = r'f:\work\sv_ran\ss_01_surrounding_01.csv'  # 新的CSV文件保存路径

# 读取两个CSV文件
df1 = pd.read_csv(csvfilepath1)
df2 = pd.read_csv(csvfilepath2)

# 找出df2中不在df1['id']中的行
new_rows = df2[~df2['id'].isin(df1['id'])]

# 将这些新行添加到df1中
df1 = pd.concat([df1, new_rows], ignore_index=True)

# 保存新的csv文件
df1.to_csv(newcsvfilepath, index=False)

# 输出新的csv文件路径
print(f'新的CSV文件已保存到 {newcsvfilepath}')

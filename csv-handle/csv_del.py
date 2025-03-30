import pandas as pd

# 将此路径替换为您的实际CSV文件路径
csvfilepath = r'f:\work\sv_ran\ss_01_surrounding_01.csv'  # 新的CSV文件保存路径

newcsvfilepath = r'f:\work\sv_ran\ss_01_surrounding_02.csv'  # 新的CSV文件保存路径


# 读取CSV文件
df = pd.read_csv(csvfilepath)

# 删除id列以特定字符串开头的行
df = df[~df['id'].str.startswith('F:\\work\\sv_ran\\sv_pan\\sv_points_ori')]

# 保存新的csv文件
df.to_csv(newcsvfilepath, index=False)

# 输出新的csv文件路径
print(f'新的CSV文件已保存到 {newcsvfilepath}')

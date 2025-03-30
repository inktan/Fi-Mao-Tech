import pandas as pd

# 将此路径替换为您的实际CSV文件路径
csv_file_path = 'f:\work\sv_ran\ss_01_surrounding_fixedBlack.csv'

# 读取csv文件
df = pd.read_csv(csv_file_path)

# 进行字符串替换
df['id'] = df['id'].str.replace('F:\\work\\sv_ran\\sv_pan\\surrounding_fixedBlack', 'F:\work\sv_ran\sv_pan\sv_points_surrounding')

# 将此路径替换为新的CSV文件保存路径
new_csv_file_path = 'f:\work\sv_ran\ss_01_surrounding_fixedBlack01.csv'

# 保存新的csv文件
df.to_csv(new_csv_file_path, index=False)

# 输出新的csv文件路径
print(df.iloc[0,0])

import pandas as pd

# 将此路径替换为您的实际CSV文件路径
csv_file_path = 'd:\work\sv_yj\sv_phoenix\merged_data_07.csv'

# 读取csv文件
df = pd.read_csv(csv_file_path)

# 进行字符串替换
df['img_save_path'] = df['img_save_path'].str.replace('/content/gdrive/MyDrive/temp/sv_20250901/', '')

# 将此路径替换为新的CSV文件保存路径
new_csv_file_path = 'd:\work\sv_yj\sv_phoenix\phoenix_with_gl.csv'

# 保存新的csv文件
df.to_csv(new_csv_file_path, index=False)

# 输出新的csv文件路径
print(df.head())
# print(df.iloc[0,0])

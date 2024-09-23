import pandas as pd

csv_file = f'e:\work\sv_zhoujunling\modified_arch_file.csv'

df = pd.read_csv(csv_file)

print(df)

# 替换字符串并保存到新列
df['file_path'] = df['file_path'].str.replace(r'E:\work\sv_zhoujunling', '/root/autodl-tmp')
df['file_path'] = df['file_path'].str.replace(r'\\', '/')

# 将修改后的DataFrame保存为新的CSV文件
output_file_path = f'e:\work\sv_zhoujunling\macao_histirical_arch_autodl.csv'
df.to_csv(output_file_path, index=False)
print(df)

# data_list = df['label-name'].tolist()

# unique_data = set(data_list)
# sorted_data = sorted(unique_data)
# print(sorted_data)

# dictionary = {}
# for i, item in enumerate(sorted_data):
#     dictionary[item] = i

# print(dictionary)

# df['label-index'] = df['label-name'].map(dictionary)
# print(df)

# # 保存修改后的数据到新的CSV文件
# df.to_csv( f'e:\work\sv_zhoujunling\macao_histirical_arch_decorate.csv', index=False)
import logging

# 配置日志
logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# 使用logging模块打印信息
logging.info("这是一条日志信息。")

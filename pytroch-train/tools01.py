import pandas as pd

csv_file = f'e:\work\sv_zhoujunling\data.csv'

df = pd.read_csv(csv_file)
data_list = df['label-name'].tolist()

unique_data = set(data_list)
sorted_data = sorted(unique_data)
print(sorted_data)

dictionary = {}
for i, item in enumerate(sorted_data):
    dictionary[item] = i

print(dictionary)

df['label-index'] = df['label-name'].map(dictionary)
print(df)

# 保存修改后的数据到新的CSV文件
df.to_csv( f'e:\work\sv_zhoujunling\macao_histirical_arch_decorate.csv', index=False)

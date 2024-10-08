# import pandas as pd

# # 1. 读取 CSV 文件
# input_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output_0.csv'
# df = pd.read_csv(input_file)

# # 2. 每10行提取一行 (使用iloc进行行索引)
# intervel_count = 100
# sampled_df = df.iloc[::intervel_count, :]

# # 3. 保存提取的数据为新的 CSV 文件
# output_file = f'e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output_{intervel_count}.csv'
# sampled_df.to_csv(output_file, index=False)

# print(f"已提取数据并保存为 {output_file}")

# import pandas as pd
# category = 'lively'

# # 读取CSV文件，处理第一列数据，并保存为新的CSV文件
# df = pd.read_csv(f'e:\work\sv_畫畫_20240923\csv_results\handle\{category}_0.csv')
# df['iamge_name'] = df['iamge_name'].str.split('_').str[0]
# df.to_csv(f'e:\work\sv_畫畫_20240923\csv_results\handle\{category}_1.csv', index=False)


import pandas as pd
category = 'lively'

# 读取CSV文件，处理第一列数据，并保存为新的CSV文件
df = pd.read_csv(r'e:\work\sv_畫畫_20240923\csv_results\ss.csv')
df['iamge_name'] = df['id'].str.split('_').str[0]
df.to_csv(r'e:\work\sv_畫畫_20240923\csv_results\ss_0.csv', index=False)




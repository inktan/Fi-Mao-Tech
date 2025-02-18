import pandas as pd
import numpy as np
import math

# 添加一列名为'result_index'，默认值为0
h_value_df = pd.DataFrame(columns=['index','Name','result_index'])

# 显示修改后的DataFrame以验证
# print(df.columns)
# print(df.head())
 
# 读取CSV文件到一个DataFrame中
df = pd.read_csv(r'e:\work\sv_juanjuanmao\指标计算\业态混合度\merged_file.csv', )
 
# 遍历DataFrame中的每一行
for index, row in df.iterrows():
    # print(row)
    # print(row['Name'])
    # print(row.values[2:])

    numbers = row.values[2:]
    non_zero_elements = [num for num in numbers if num != 0]

    total_sum = np.sum(non_zero_elements)

    result = [ (num / total_sum)*math.log(num / total_sum) for num in non_zero_elements]
    h_value = np.sum(result)*(-1)
    rate_list = [row['index'],row['Name'],h_value]
    h_value_df.loc[len(h_value_df)] = rate_list
    # if len(non_zero_elements) > 10:
    #     break

h_value_df.to_csv(r'e:\work\sv_juanjuanmao\指标计算\业态混合度\h_value_file.csv', index=False)

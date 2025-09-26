import pandas as pd

# 读取数据
df = pd.read_csv(r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id_02.csv')

# 获取所有列名
all_columns = df.columns.tolist()

# 要移动的列
columns_to_move = ['image_id', 'image_name', 'image_path', 'panoid']

# 从原列名列表中移除要移动的列
remaining_columns = [col for col in all_columns if col not in columns_to_move]

# 重新排列列顺序：其他列在前，要移动的列在后
new_column_order = remaining_columns + columns_to_move

# 重新排列列
df_reordered = df[new_column_order]

# 显示结果
print("原始列顺序:", all_columns)
print("新的列顺序:", new_column_order)
print("\n处理后的数据前5行:")
print(df_reordered.head())

df_reordered.to_csv(r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id_03.csv', index=False)

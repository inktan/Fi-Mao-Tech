import pandas as pd

# 读取 CSV 文件
df = pd.read_csv(r'd:\work\sv_yj\sv_phoenix\merged_data_06.csv')  # 替换为您的文件路径

# 方法1: 使用 rename() 函数指定要修改的列
df = df.rename(columns={
    'pano_panoid':'panoid',
    'pano_pitch':'pitch',
    'pano_heading':'heading',
    'pano_fov01':'fov01',
    'pano_fov02':'fov02',
    'pano_year':'year',
    'pano_month':'month',
})

# 方法2: 如果只想修改这四个列，其他列保持不变
# 创建一个映射字典
# rename_dict = {}
# for col in ['heading', 'pitch', 'fov1', 'fov2']:
#     if col in df.columns:
#         rename_dict[col] = col + '_ori'

# df = df.rename(columns=rename_dict)

# 显示修改后的列名
print("修改后的列名:")
print(df.columns.tolist())

# 显示前几行数据
print("\n前几行数据:")
print(df.head())

# 如果需要保存到新的CSV文件
df.to_csv(r'd:\work\sv_yj\sv_phoenix\merged_data_07.csv', index=False)





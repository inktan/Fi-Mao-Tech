import pandas as pd


# 输入和输出文件路径
input_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_05-_.csv'

output_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_06-_.csv'

# 读取CSV文件
df = pd.read_csv(input_file)

# 删除id列（如果存在）
if 'id' in df.columns:
    df.drop('id', axis=1, inplace=True)
else:
    print("警告：未找到'id'列")

# 保存为新的CSV文件
df.to_csv(output_file, index=False)

print(f"处理完成，结果已保存到 {output_file}")
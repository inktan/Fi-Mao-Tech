import pandas as pd

# 读取CSV文件
df = pd.read_csv(r'e:\work\sv_shushu\所有指标\ss_merged_file.csv')  # 替换为你的输入文件名

# 处理ID列 - 使用反斜杠分割并保留最后一项
df['id'] = df['id'].str.split('\\').str[-1]  # 注意：反斜杠需要转义

# 保存为新的CSV文件
df.to_csv(r'e:\work\sv_shushu\ss02.csv', index=False)  # 替换为你想要的输出文件名
 
import pandas as pd

# 读取CSV文件
df = pd.read_csv(r'e:\work\sv_shushu\所有指标\ss_merged_file.csv')  # 替换为你的输入文件名

# 处理ID列 - 使用反斜杠分割并保留最后一项
df['id'] = df['id'].str.split('\\').str[-1]  # 注意：反斜杠需要转义

# 保存为新的CSV文件
df.to_csv(r'e:\work\sv_shushu\ss02.csv', index=False)  # 替换为你想要的输出文件名
 
import pandas as pd

# 读取CSV文件（假设列名为 'path'）
df = pd.read_csv('your_file.csv')

# 分割路径，提取最后两部分
split_result = df['path'].str.split(r'\\', expand=True)  # 注意转义反斜杠

# 获取倒数第二列（folder_name）和最后一列（file_name）
df['folder_name'] = split_result.iloc[:, -2]  # 倒数第二列
df['file_name'] = split_result.iloc[:, -1]    # 最后一列

# 查看结果
print(df[['path', 'folder_name', 'file_name']].head())





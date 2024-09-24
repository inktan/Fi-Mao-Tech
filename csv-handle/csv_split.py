import pandas as pd

# 1. 读取 CSV 文件
input_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output.csv'
df = pd.read_csv(input_file)

# 2. 每10行提取一行 (使用iloc进行行索引)
sampled_df = df.iloc[::100, :]

# 3. 保存提取的数据为新的 CSV 文件
output_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output_100.csv'
sampled_df.to_csv(output_file, index=False)

print(f"已提取数据并保存为 {output_file}")






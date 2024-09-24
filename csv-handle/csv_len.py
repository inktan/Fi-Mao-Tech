import pandas as pd

# 1. 读取 CSV 文件
input_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output_100.csv'
df = pd.read_csv(input_file)

length_of_csv = len(df)

print(length_of_csv)

import pandas as pd
import shutil
import os

# 1. 读取 CSV 文件
input_file = r'f:\sv_shanghai\20220720-上海\sv_pan\ss_01.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
print(len(headers))
print(df.head())
print(df.shape)


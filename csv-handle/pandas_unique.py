import json
import pandas as pd
import os
# df = pd.read_csv("e:\work\sv_hukejia\sv\丽水市_100msv_infos_.csv")
# df['longitude'] = df['longitude'].astype(float)
# df['latitude'] = df['latitude'].astype(float)
# df.to_csv("E:\work\sv_hukejia\sv\handle\丽水市_100msv_infos_01.csv", index=False)
# print("转换完成，已保存为新的CSV文件。")

# df = pd.read_csv(r'c:\Users\wang.tan.GOA\Desktop\id007.csv')
# print(df.shape)
# print(df.head(5))

# df_unique = df.drop_duplicates(subset=['longitude', 'latitude'])
# print(df_unique.shape)
# print(df_unique.head(5))

# df_unique.to_csv(r'c:\Users\wang.tan.GOA\Desktop\id007_unique.csv', index=False)

# 1. 读取 CSV 文件
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_new_file.csv'
# df = pd.read_csv(input_file)
# headers = df.columns
# print(headers)

# 假设文件夹路径为 "folder_path"
folder_path = r"E:\work\sv_hukejia\sv\handle\points01_panoid01"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        # 使用pandas读取csv文件
        df = pd.read_csv(file_path)
        # df['longitude'] = df['longitude'].astype(float)
        # df['latitude'] = df['latitude'].astype(float)
        # df_unique = df.drop_duplicates(subset=['longitude', 'latitude'])
        df_unique = df.drop_duplicates(subset=['ID'])
        df_unique.to_csv(file_path.replace(r"points01_panoid01",r'points01_panoid02'), index=False)

        # 打印DataFrame的shape值
        # print(f"文件 {filename} 的 shape 值为: {df.shape}")
        # count+=df.shape[0]
print('end')


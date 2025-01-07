import pandas as pd

input_files = []

# 1. 读取 CSV 文件
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_new_file.csv'
# df = pd.read_csv(input_file)
# headers = df.columns
# print(headers)
import os
import pandas as pd

# 假设文件夹路径为 "folder_path"
folder_path = r"E:\work\sv_hukejia\sv"

count=0
# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith("_100m_.csv"):
        file_path = os.path.join(folder_path, filename)
        # 使用pandas读取csv文件
        df = pd.read_csv(file_path)
        # 打印DataFrame的shape值
        print(f"文件 {filename} 的 shape 值为: {df.shape}")
        count+=df.shape[0]

print("总行数：",count)


 丽水市_100m 的点数为: 378872 
 台州市_100m 的点数为: 411437 
 嘉兴市_100m 的点数为: 425560 
 宁波市_100m 的点数为: 713634 
 杭州市_100m 的点数为: 1121627 
 温州市_100m 的点数为: 728615 
 湖州市_100m 的点数为: 268809 
 绍兴市_100m 的点数为: 350319 
 舟山市_100m 的点数为: 110196 
 衢州市_100m 的点数为: 744357 
 金华市_100m 的点数为: 481600 

 浙江省_100m 的点数为: di5735026
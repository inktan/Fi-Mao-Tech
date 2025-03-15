
import os
import pandas as pd
import os
import csv

csv_paths = []
csv_names = []
accepted_formats = ("_z_score_w.csv")

csv_path_list =[
    r'E:\work\sv_juanjuanmao\20250308\吸引力数据',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)
                
print(csv_paths)

# for file_path in csv_paths:
#     print(file_path)
#     df = pd.read_csv(file_path)
#     print(df.head(5))

    # df["微博"] = pd.to_numeric(df["微博"], errors='coerce').fillna(0).astype(int) + 1

    # output_file = file_path.replace('.csv','add_1.csv')
    # df.to_csv(output_file, index=False, encoding='utf-8-sig')

    # print(f"成功: '微博' 列数据已加 1，并保存到 '{output_file}'。")

# for file_path in csv_paths:
#     print(file_path)
#     df = pd.read_csv(file_path)
#     print(df.head(5))

#     # 选择指定的列
#     selected_columns = df[["大类", "小类", "name", "微博"]]

#     # 保存为新的 CSV 文件
#     selected_columns.to_csv(file_path, index=False, encoding='utf-8-sig')

# for file_path in csv_paths:
#     print(file_path)
#     df = pd.read_csv(file_path)
#     print(df.head(5))

#     # 将 "aaa" 列的数据转换为整数
#     df["微博"] = pd.to_numeric(df["微博"], errors='coerce').fillna(0).astype(int)

#     # 计算总和、平均值和标准差
#     id = os.path.basename(file_path)
#     mean = df["微博"].mean()
#     std = df["微博"].std()

#     # 计算并添加新列
#     df["z_score"] = (df["微博"]  * mean) / std

#     output_file = file_path.replace('add_1.csv','_z_score.csv')
#     df.to_csv(output_file, index=False, encoding='utf-8-sig')

#     print(f"成功保存到 '{output_file}'。")

# dict_w = {  '旅游娱乐':0.858,
#             '餐饮服务':0.094,
#             '住宿服务':0.027,
#             '商业服务':0.021,}

# for file_path in csv_paths:
#     print(file_path)
#     df = pd.read_csv(file_path)
#     print(df.head(5))

#     df["w"] = df["大类"].map(dict_w)
#     print(df.head(5))

#     output_file = file_path.replace('_z_score.csv','_z_score_w.csv')
#     df.to_csv(output_file, index=False, encoding='utf-8-sig')

#     print(f"成功保存到 '{output_file}'。")

for file_path in csv_paths:
    # print(file_path)
    df = pd.read_csv(file_path)
    # print(df.head(5))

    # 将 "a" 列和 "b" 列的数据转换为数值类型，并相乘
    df["z_score"] = pd.to_numeric(df["z_score"], errors='coerce')
    df["w"] = pd.to_numeric(df["w"], errors='coerce')
    df["attractive_force"] = df["z_score"] * df["w"]

    # 计算乘积的总和
    # total_sum = df["attractive_force"].sum()
    total_sum = df["attractive_force"].mean()
    print(file_path,total_sum)

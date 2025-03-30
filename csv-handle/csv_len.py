import os
import pandas as pd

csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_list =[
    r'E:\work\sv_shushu\谷歌\pre预测声景指标',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)
                
csv_paths = [
     r'e:\work\spatio_evo_urbanvisenv_svi_leo371\20250224\color_拉萨_complexity_harmony.csv'
    ]

total_rows = 0
for file_path in csv_paths:
    print(file_path)
    try:
        # df = pd.read_csv(file_path, encoding='GBK')
        df = pd.read_csv(file_path)
        print(df.shape)
        print(df.columns)
        print(df.iloc[0,0])
        # print(df.columns[2])
        print(df.head(15))
        # print(f"{len(df)}")
        # total_rows += len(df)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

# print(f"Total number of rows in all matching CSV files: {total_rows}")

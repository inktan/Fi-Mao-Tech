import os
import pandas as pd

csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_list =[
    # r'E:\work\sv_YJ_20240924\points',
    r'DF:\BaiduNetdiskDownload\sv_roadpoints_50m',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)
                
csv_paths = [
    # r'E:\work\sv_YJ_20240924\points',
    r'f:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_person_01.csv',
    r'f:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_person_03.csv',
    ]

total_rows = 0
for file_path in csv_paths:
    try:
        df = pd.read_csv(file_path)
        total_rows += len(df)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

print(f"Total number of rows in all matching CSV files: {total_rows}")
import os
import pandas as pd

csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_list =[
    # r'F:\work\sv_ran\ss_rgb_fisheye_shp\sv_points_surrounding_pd_pf',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)
                
csv_paths = [
    r'e:\work\sv_momo\sv_20250512\points.csv'
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

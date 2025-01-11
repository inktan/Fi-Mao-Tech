import pandas as pd

input_files = []

# 1. 读取 CSV 文件
input_file = r'f:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_person_03.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
print(df.head())
print(df.shape)

# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_01_ss.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_01_ss_01.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_02_ss_01.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_02_ss_02.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_02_ss_03.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_02_ss_04.csv'
# input_files.append(input_file)
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_pan_02_ss_05.csv'
# input_files.append(input_file)

# for i in input_files:
    # df = pd.read_csv(i, header=None)
    # new_df = pd.DataFrame(df.values, columns=df.columns)
    # new_df.to_csv(i, index=False)
    
    # df = pd.read_csv(i)
    # print(df.shape)
    # print(df.head())
    
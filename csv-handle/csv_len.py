import pandas as pd

input_files = []

# 1. 读取 CSV 文件
input_file = r'f:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02_person_03.csv'
df = pd.read_csv(input_file)
headers = df.columns
print(headers)
print(df.head())
print(df.shape)

# 假设文件夹路径为 "folder_path"
folder_path = r"E:\work\sv_nadingzichidefangtoushi"

count=0
# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        # 使用pandas读取csv文件
        df = pd.read_csv(file_path)
        # 打印DataFrame的shape值
        print(f"文件 {filename} 的 shape 值为: {df.shape}")
                        
        headers = df.columns
        print(len(headers))
        print(df.head())
        print(df.shape)
        count+=df.shape[0]

print("总行数：",count)

import pandas as pd  
import os  
import glob  
import os   
# 读取原始CSV文件  
df = pd.read_csv(r'e:\work\sv_levon\50M-Distance-WGS84-4326.csv', dtype={'Id': int, 'SomeNumber': int})  

# 定义构建文件路径的函数  
def build_file_path(row):  
    # 假设文件路径的格式为：'some_directory/{id}_{num}.txt'  
    # 你可以根据实际情况修改这个格式  
    return f'E:\work\sv_levon\sv_degree_hor_new/{int(row["Id"])}_{row["lng"]}_{row["lat"]}'

# 定义构建文件路径的函数  
def build_file_path_prefix(row):  
    # 假设文件路径的格式为：'some_directory/{id}_{num}.txt'  
    # 你可以根据实际情况修改这个格式  
    return f'E:\work\sv_levon\sv_degree_hor_new/{int(row["Id"])}_{row["lng"]}_{row["lat"]}*'
  
# 创建一个空列表来存储行数据  
rows = []  

# 遍历每一行数据  
for index, row in df.iterrows():  
    # 构建文件路径前缀  
    prefix = build_file_path_prefix(row)  
    # 使用glob模块匹配以该前缀开始的文件  
    matching_files = glob.glob(prefix)  
    # 检查是否有匹配的文件  
    if not matching_files:  
        # 如果没有匹配的文件，则将该行添加到新的DataFrame中  
        # new_df = new_df.append(row, ignore_index=True)  
        rows.append(row.to_dict())  # 将行转换为字典并添加到列表中  

# 遍历每一行数据  
# for index, row in df.iterrows():  
#     file_path = build_file_path(row)  
    # 检查路径是否存在  
    # if not os.path.exists(file_path):  
        # 如果路径不存在，则将该行添加到新的DataFrame中  
        # new_df = new_df.append(row, ignore_index=True)  

# 使用列表创建新的 DataFrame  
new_df = pd.DataFrame(rows)

# 将新的DataFrame保存为新的CSV文件  
new_df.to_csv('e:\work\sv_levon\50M-01.csv', index=False)
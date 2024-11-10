import os  
import fnmatch  
import pandas as pd  
  
# 定义文件夹路径  
folder_path = r'E:\work\sv_levon\folder-01'  # 请替换为实际的文件夹路径  
  
# 初始化一个空的DataFrame，用于存储合并后的数据  
combined_df = pd.DataFrame()  

# 定义文件前缀  
file_prefix = 'sv_hor_2017_'  
  
# 遍历文件夹中的所有文件  
for filename in os.listdir(folder_path):  
    # 检查文件名是否以指定的前缀开头并且文件扩展名为.csv  
    if filename.startswith(file_prefix) and filename.endswith('.csv'):  
        # 构建文件的完整路径  
        file_path = os.path.join(folder_path, filename)  
          
        # 读取CSV文件到DataFrame中  
        df = pd.read_csv(file_path)  
          
        # 将读取到的DataFrame追加到combined_df中  
        combined_df = pd.concat([combined_df, df], ignore_index=True)  
  
# 输出合并后的DataFrame（或者你可以将其保存到新的CSV文件中）  
print(combined_df)  
combined_df.to_csv(r'E:\work\sv_levon\folder-01\sv_hor_2017.csv', index=False)
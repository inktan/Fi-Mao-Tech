import os
import pandas as pd

# 指定文件夹路径
folder_path = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_林芝'  # 替换为你的文件夹路径

# 获取文件夹中的所有文件夹名
folder_names = [name for name in os.listdir(folder_path) 
                if os.path.isdir(os.path.join(folder_path, name))]

# 分割文件夹名并创建 DataFrame
data = []
for name in folder_names:
    parts = name.split('_')
    if len(parts) >= 3:  # 确保文件名可以分割成至少三部分
        data.append({
            'id': parts[0],
            'lon': parts[1],
            'lat': parts[2]
        })

# 创建 DataFrame
df = pd.DataFrame(data)

output_csv = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_林芝_points.csv'         # 输出的CSV文件名
df.to_csv(output_csv, index=False)

print(f"数据已保存到 {output_csv}")

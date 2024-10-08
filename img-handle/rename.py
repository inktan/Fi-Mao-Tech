import pandas as pd
import os

# 指定目标文件夹路径
folder_path = 'E:\work\sv_畫畫_20240923\sv_degrees'

# 读取 CSV 文件
df = pd.read_csv(r'e:\work\sv_畫畫_20240923\aomen.csv')

# 逐行打印
for index, row in df.iterrows():
    print(index)
    name_index = str(row['OBJECTID']) + '_'

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为 .jpg 格式
        if filename.endswith('.jpg'):
            if filename.startswith(name_index):
                # 去掉文件扩展名，然后根据 _ 进行分割，获取第一个元素
                name_without_ext = os.path.splitext(filename)[0]  # 去掉文件扩展名
                first_element = name_without_ext.split('_')[0]    # 根据 _ 分割并获取第一个元素
                old_name = folder_path+'/'+filename
                new_name = folder_path+'/' + str(row['OBJECTID']) + '_'+ str(row['lng']) + '_' + str(row['lat']) + '_' + filename.split('_')[-1] 
                os.rename(old_name, new_name)
                print(f"图片名称已从 '{old_name}' 修改为 '{new_name}'")


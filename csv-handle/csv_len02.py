import pandas as pd
import shutil
import os

input_files = []

# 1. 读取 CSV 文件
# input_file = r'd:\BaiduNetdiskDownload\sv_roadpoints_50m\seg_\sv_new_file.csv'
# df = pd.read_csv(input_file)
# headers = df.columns
# print(headers)

input_file = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\拉萨传统商业街区风貌得分.csv'
input_files.append(input_file)
input_file = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\山南、林芝传统商业街区风貌得分.csv'
input_files.append(input_file)

for i in input_files:
    df = pd.read_csv(i)
    if 'id' in df.columns:
        for id_value in df['id']:
            print(id_value)
            # 源文件路径
            src_file = os.path.join(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\拉萨市传统商业街区街景\test' , id_value +'.jpg')
            # src_file = os.path.join(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\山南、林芝传统商业街景\test' , id_value +'.jpg')
            print(src_file)
            # 目标文件夹路径
            dst_folder = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai\sv_degree'
            # 确保目标文件夹存在
            if not os.path.exists(dst_folder):
                os.makedirs(dst_folder)
            # 构建目标文件路径（在目标文件夹中保持相同的文件名）
            dst_file = os.path.join(dst_folder, id_value +'.jpg')
            print(dst_file)

            # 复制文件

            try:
                shutil.copy2(src_file, dst_file)
            except Exception as e:
                print(e)

            print(f"文件已复制到: {dst_file}")
            # print(id_value)
    else:
        print("CSV文件中没有名为'id'的列")
    
    # df = pd.read_csv(i, header=None)
    # df = pd.read_csv(i)
    # df = pd.read_csv(i.replace('.csv','_a01.csv'))
        
        # 替换表头
    # df.columns = headers
    
    # new_df = pd.DataFrame(df.values, columns=df.columns)
    # df.to_csv(i, index=False)
    
    # df = pd.read_csv(i)
    # print(df.shape)
    # print(df.head())

    # 检查第一列的数据是否等于'id'，并删除这些行
    # df = df[df.iloc[:, 0] != 'id']

    # 保存修改后的DataFrame到新的CSV文件（或者覆盖原文件）
    # df.to_csv(i.replace('.csv','_a01.csv'), index=False)
    # df = pd.read_csv(i)
    # print(df.shape)
    # print(df.head())
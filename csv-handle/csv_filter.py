import pandas as pd
import os
import shutil

for location_name in ['山南']:

    # 1. 读取 CSV 文件
    input_file = f'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_{location_name}_a01.csv'
    df = pd.read_csv(input_file)

    # 筛选score列大于1的行
    filtered_df = df[df["building;edifice"] > 0.4 ]
    print(filtered_df)

    folder01 = f'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_{location_name}'
    folder02 = f'E:\work\spatio_evo_urbanvisenv_svi_leo371\街景建筑分类\sv_{location_name}_a01'

    # 确保目标文件夹存在
    if not os.path.exists(folder02):
        os.makedirs(folder02)

    # 遍历DataFrame中的每一行
    for index, row in filtered_df.iterrows():
        # 生成原文件路径
        original_file_path = os.path.join(folder01, row['folder_name'], row['file_name'])
        # 生成目标文件路径
        target_file_path = os.path.join(folder02, row['folder_name'], row['file_name'])
        # 移动文件
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)  # 确保目标文件夹存在
        # 确保目标文件夹存在
        if not os.path.exists(folder02):
            os.makedirs(folder02)

        shutil.copy(original_file_path, target_file_path)

    # import pandas as pd

    # # 读取CSV文件
    # df = pd.read_csv(r'f:\work\sv_ran\ss_rgb_fisheye_shp\sv_points_surrounding_pd_pf.csv')  # 替换'your_file.csv'为你的文件路径

    # # 筛选出id列为'住宅a'或'住宅b'的行
    # filtered_df = df[df['中类'].isin(['别墅区', '住宅区'])]

    # # 保存为新的CSV文件
    # filtered_df.to_csv(r'f:\work\sv_ran\ss_rgb_fisheye_shp\sv_points_surrounding_pd_pf01.csv', index=False)  # 替换'filtered_file.csv'为你希望保存的新文件名


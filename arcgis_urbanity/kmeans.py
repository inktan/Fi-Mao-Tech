import pandas as pd
import geopandas as gpd

import numpy as np
from sklearn.cluster import KMeans

import os
from tqdm import tqdm

import shutil

output_filepath = r'e:\work\sv_shushu\谷歌\index\six_sv_scaler.shp'
polygons_gdf = gpd.read_file(output_filepath)
x = polygons_gdf.iloc[:, 1:-1]

kmeans = KMeans(n_clusters=6, max_iter=500)    # 为了避免时间太长 k_means最大迭代次数限制在300次以内
kmeans.fit(x)
# 获取聚类结果
labels = kmeans.labels_

# 将聚类结果添加到原始DataFrame中
polygons_gdf['cluster'] = labels
file_name = f"E:\work\sv_shushu\Export_Output-澳门\ss_point_kmeans.shp"
polygons_gdf.to_file(file_name, index=False)
print(polygons_gdf['cluster'].value_counts())
centroids = kmeans.cluster_centers_

# 遍历DataFrame的每一行
# for index, row in tqdm(df1.iterrows()):
#     # 获取文件夹路径
#     folder_path = 'E:\\work\\spatio_evo_urbanvisenv_svi\\sv\\kmeans\\' + str(int(row.iloc[-1]))

#     # # 检查文件夹是否存在，如果不存在，则创建
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
    
#     # # 构建文件名
#     folder_name_ = str(int(row.iloc[0]))+'_'+str(row.iloc[1])+'_'+str(row.iloc[2])
#     file_name = str(int(row.iloc[0]))+'_'+str(row.iloc[1])+'_'+str(row.iloc[2])+'_'+str(int(row.iloc[3]))+'_'+str(int(row.iloc[4]))+'.jpg'
#     # 源文件路径
#     source_file = f'E:\work\spatio_evo_urbanvisenv_svi\sv\degree\{folder_name_}\{file_name}'

#     # 目标文件路径
#     destination_file = f'{folder_path}\{file_name}'
    
#     # 复制文件
#     shutil.copy(source_file, destination_file)
    # break

# print("文件复制完成。")


# %%

# for label_id in tqdm(range(n_clusters)):
#     idxs = np.where(clt.labels_ == label_id)[0] # 取出对应聚类id的图片id
#     patch_save_dir = os.path.join(result_dir, str(label_id))   # 保存聚类结果的子文件夹路径
#     if not os.path.exists(patch_save_dir):
#         os.makedirs(patch_save_dir)
#     for i in idxs:
#         shutil.copy(feature_img_path[i], patch_save_dir)



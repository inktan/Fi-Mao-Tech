# -*- coding: utf-8 -*-

import numpy as np
from sklearn.cluster import KMeans
from image_searcher import Search

import os
from tqdm import tqdm

import shutil

def main(image_fold,result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    searcher = Search(image_dir_path=image_fold,save_path=result_dir,traverse=True,include_faces=False)
    imgs_path = searcher.stored_embeddings.embeddings.keys() # 街景pathc路径
    imgs_embeddings = searcher.stored_embeddings.embeddings.values() # 街景pathc-embeddings
    feature_img_path=list(imgs_path)
    all_features_ = [i['image_embedding'].numpy().flatten() for i in imgs_embeddings]
    
    clt = KMeans(n_clusters=n_clusters, max_iter=500)    # 为了避免时间太长 k_means最大迭代次数限制在300次以内
    clt.fit(all_features_)
    for label_id in tqdm(range(n_clusters)):
        idxs = np.where(clt.labels_ == label_id)[0] # 取出对应聚类id的图片id
        patch_save_dir = os.path.join(result_dir, str(label_id))   # 保存聚类结果的子文件夹路径
        if not os.path.exists(patch_save_dir):
            os.makedirs(patch_save_dir)
        for i in idxs:
            shutil.copy(feature_img_path[i], patch_save_dir)

if __name__ == "__main__":
    # 目标瓦片数据集
    image_fold = r'E:\work\spatio_evo_urbanvisenv_svi\patch_kmeans\sv_split\sv_patch_retain'

    # 设置目标聚类数量
    n_clusters = 200
    result_dir = r'E:\work\spatio_evo_urbanvisenv_svi\patch_kmeans\sv_split\sv_clip_kmeans_'+str(n_clusters)
    
    main(image_fold,result_dir)
    

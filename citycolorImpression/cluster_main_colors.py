# -*- coding: utf-8 -*-

from sklearn import cluster
import os
from tqdm import tqdm
import csv
from PIL import Image
import numpy as np
from scipy.spatial import distance
import matplotlib.pylab as plt
import colorsys

def rgb_to_hsv_(r, g, b):
    '''度-百分比-百分比'''
    # 将RGB值转换为0到1的范围
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # 使用colorsys模块转换到HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # 返回HSV值
    return h*360, s, v

def cluster_main_colors(img_path, img_name, results_folder_path, n_clusters):
    image = Image.open(img_path)
    pixels = np.array(image)
    # height, width, _ = pixels.shape

    pix_datas = pixels.reshape(-1, 3)
    color_sums = np.sum(pix_datas, axis=1)
    # 剔除白色像素
    pix_datas_without_white = pix_datas[color_sums < 759]
    # kmeans聚类
    km=cluster.KMeans(n_clusters)
    # 对去除了白色像素的像素数据集进行KMeans聚类。
    km.fit(pix_datas_without_white)

    # 将聚类中心的颜色转换为无符号8位整数（适合表示像素值），并转换为列表格式。
    cluster_centers_colors = np.array(km.cluster_centers_, dtype=np.uint8).tolist()

    cluster_color_csv = [img_name] 
    cluster_color_csv.extend(cluster_centers_colors)
    # with open(results_csv,'a' ,newline='') as f:
    #     writer = csv.writer(f)
    #     try:
    #         writer.writerow(cluster_color_csv)
    #     except Exception as e :
    #         print(f'error:{e}')
    
    # return 
    # 计算每个像素到每个聚类中心的距离，得到一个距离矩阵。每个像素点到聚类中心的距离列表，数量为n
    dist_matrix = distance.cdist(pix_datas_without_white, cluster_centers_colors)
    # 对于每个像素，找到最近的聚类中心的索引。
    closest_indices = np.argmin(dist_matrix, axis=1)
    # 计算每个聚类中心的像素数量。minlength参数确保计数数组的长度与聚类中心的数量相同
    cluster_color_counts = np.bincount(closest_indices, minlength=n_clusters)
    # 计算每个聚类中心颜色的比例，即每个聚类中心颜色的像素数除以总像素数。
    cluster_color_ratios = cluster_color_counts /  len(pix_datas_without_white)

    # 输出表格

    sorted_cluster_color_ratios = sorted(cluster_color_ratios, reverse=True)
    sorted_indices = sorted(range(len(cluster_color_ratios)), key=lambda k: cluster_color_ratios[k], reverse=True)
    sorted_cluster_centers_colors = [cluster_centers_colors[i] for i in sorted_indices]

    cluster_color_csv = [img_name] 
    cluster_color_csv.extend(sorted_cluster_centers_colors)
    cluster_color_csv.extend(sorted_cluster_color_ratios)

    with open(results_csv,'a' ,newline='') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(cluster_color_csv)
        except Exception as e :
            print(f'error:{e}')
    
    # return 
    # 绘制图案
    # 1 绘制图片
    fig = plt.figure(figsize=(8, 5))
    grid = plt.GridSpec(1, 2, hspace=0, wspace=0, width_ratios=[4, 1])
    ax = fig.add_subplot(grid[0, 0])
    ax.imshow(image)
    ax.axis('off')
    # 2 绘制主色调
    ax2 = fig.add_subplot(grid[0, 1])
    colors = ['#%02x%02x%02x' % tuple(rgb) for rgb in sorted_cluster_centers_colors]
    rects = ax2.barh(range(n_clusters), sorted_cluster_color_ratios, height=0.6,color=colors)
    ax2.yaxis.set_ticks([])
    ax2.set_xlim(0, 1.0)
    ax2.set_title('')
    ax2.bar_label(rects, padding=0, labels=[f'{x*100:.0f}%' for x in sorted_cluster_color_ratios], color="r",fontsize=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.set_anchor('W')
    # plt.show()
    plt.tight_layout()
    plt.savefig(results_folder_path+'\\'+img_name)
    plt.close('all')

if __name__ == "__main__":
    
    iamges_folder_path = r'E:\work\sv_renleihuoshifen\sv_degree_960_720'
    results_folder_path = r'E:\work\sv_renleihuoshifen\images_cluster_colors'
    results_csv = r'E:\work\sv_renleihuoshifen\images_cluster_colors.csv'
    
    if not os.path.exists(results_folder_path):
        os.makedirs(results_folder_path)

    img_paths = []
    img_names = []

    for root, dirs, files in os.walk(iamges_folder_path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)

    headers =["File_Name","Color_tone_1","Color_tone_2","Color_tone_3","Color_tone_4","Color_tone_5","Color_tone_6","Color_tone_7","Color_tone_8",
                         "Percentage_1","Percentage_2","Percentage_3","Percentage_4","Percentage_5","Percentage_6","Percentage_7","Percentage_8"]
    
    with open(results_csv,'w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
 
    n_clusters = 8
    for i ,img_path in enumerate(tqdm(img_paths)):
        try:
            cluster_main_colors(img_path, img_names[i],results_folder_path,n_clusters)
            # break
        except Exception as e :
            print(f'error:{e}')
            continue
# import cv2
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from skimage import color
import os
from tqdm import tqdm
import csv

def calculate_color_complexity(image,kmeans, n_clusters=10):
    """
    计算图像的色彩复杂度
    :param image_path: 图像路径
    :param n_clusters: 聚类数量（主色彩数量）
    :return: 色彩复杂度
    # """
    # # 读取图像
    # # 使用Pillow读取图像
    # image = Image.open(image_path)
    # image = image.convert("RGB")  # 确保图像是RGB模式
    # image = np.array(image)  # 将Pillow图像转换为NumPy数组
    # image = image.reshape(-1, 3)  # 将图像展平为二维数组

    # # 使用KMeans聚类提取主色彩
    # kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    # kmeans.fit(image)
    colors = kmeans.cluster_centers_  # 主色彩
    labels = kmeans.labels_  # 每个像素的标签

    # 计算每种色彩的占比
    color_ratios = np.bincount(labels) / len(image)

    # 计算色彩复杂度
    complexity = 1 - np.sum(color_ratios ** 2)
    return complexity
def calculate_color_harmony(image,kmeans, n_clusters=10):
    """
    计算图像的色彩协调度
    :param image_path: 图像路径
    :param n_clusters: 聚类数量（主色彩数量）
    :return: 色彩协调度
    """
    # # 使用Pillow读取图像
    # image = Image.open(image_path)
    # image = image.convert("RGB")  # 确保图像是RGB模式
    # image = np.array(image)  # 将Pillow图像转换为NumPy数组
    # image = image.reshape(-1, 3)  # 将图像展平为二维数组

    # # 使用KMeans聚类提取主色彩
    # kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    # kmeans.fit(image)
    colors = kmeans.cluster_centers_  # 主色彩
    labels = kmeans.labels_  # 每个像素的标签

    # 计算每种色彩的占比
    color_ratios = np.bincount(labels) / len(image)

    # 将RGB颜色转换为Lab颜色空间
    lab_colors = color.rgb2lab(colors / 255.0)

    # 使用NumPy广播机制优化色彩协调度计算
    # 计算所有色彩对之间的色差ΔE
    delta_e_matrix = np.sqrt(np.sum((lab_colors[:, np.newaxis] - lab_colors) ** 2, axis=2))
    
    # 创建权重矩阵，排除自身比较的情况（对角线为0）
    weight_matrix = np.outer(color_ratios, color_ratios) * (1 - np.eye(n_clusters))
    
    # 计算加权平均色差
    harmony = np.sum(delta_e_matrix * weight_matrix) / (n_clusters * (n_clusters - 1) / 2)

    return harmony
def calculate_color_harmony_(image_path, n_clusters=10):
    """
    计算图像的色彩协调度
    :param image_path: 图像路径
    :param n_clusters: 聚类数量（主色彩数量）
    :return: 色彩协调度
    """
    # 读取图像
    # 使用Pillow读取图像
    image = Image.open(image_path)
    image = image.convert("RGB")  # 确保图像是RGB模式
    image = np.array(image)  # 将Pillow图像转换为NumPy数组
    image = image.reshape(-1, 3)  # 将图像展平为二维数组

    # 使用KMeans聚类提取主色彩
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    kmeans.fit(image)
    colors = kmeans.cluster_centers_  # 主色彩
    labels = kmeans.labels_  # 每个像素的标签

    # 计算每种色彩的占比
    color_ratios = np.bincount(labels) / len(image)

    # 将RGB颜色转换为Lab颜色空间
    lab_colors = color.rgb2lab(colors / 255.0)

    # 计算色彩协调度
    harmony = 0
    for i in range(n_clusters):
        for j in range(n_clusters):
            if i != j:
                # 计算色彩之间的色差ΔE
                delta_e = np.sqrt(np.sum((lab_colors[i] - lab_colors[j]) ** 2))
                # 加权平均
                harmony += color_ratios[i] * color_ratios[j] * delta_e

    # 归一化
    harmony /= (n_clusters * (n_clusters - 1) / 2)
    return harmony


img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(r'e:\work\20250709_sv_michinen\20251021\svi\ade_20k\_05_sv_extracted'):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

# color_complexity_harmony_csv = r'e:\work\sv_mubibai\图片分析792\色彩协调度.csv'
color_complexity_harmony_csv = r'e:\work\20250709_sv_michinen\20251021\svi\ade_20k\色彩复杂度.csv'
with open(color_complexity_harmony_csv,'w' ,newline='') as f:
    writer = csv.writer(f)
    # writer.writerow(['img_path','complexity','harmony'])
    writer.writerow(['img_path','色彩丰富度','色彩协调度'])
    # writer.writerow(['img_path','色彩协调度'])
    # writer.writerow(['img_path','色彩复杂度'])

for i,img_path in enumerate(tqdm(img_paths)):
    try:
        image = Image.open(img_path)
        image = image.convert("RGB")  # 确保图像是RGB模式
        image = np.array(image)  # 将Pillow图像转换为NumPy数组
        image = image.reshape(-1, 3)  # 将图像展平为二维数组

        # 使用KMeans聚类提取主色彩
        kmeans = KMeans(n_clusters=10, n_init=10, random_state=42)
        kmeans.fit(image)
        colors = kmeans.cluster_centers_  # 主色彩
        labels = kmeans.labels_  # 每个像素的标签

        complexity = calculate_color_complexity(image,kmeans, 10)
        harmony = calculate_color_harmony(image,kmeans, 10)
        # print(complexity,harmony)
        print(f"色彩复杂度: {complexity:.4f}")
        # print(f"色彩协调度: {harmony:.4f}")
        # break
        with open(color_complexity_harmony_csv,'a' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow([img_path,complexity,harmony])
            # writer.writerow([img_path,harmony])
            # writer.writerow([img_path, complexity])
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        continue

# 示例使用
# image_path = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_拉萨\sv_拉萨\1_91.1398777_29.6662155\1_91.1398777_29.6662155_201608_0.jpg"  # 替换为你的图像路径
# 读取图像
# 使用Pillow读取图像
# image = Image.open(image_path)
# image = image.convert("RGB")  # 确保图像是RGB模式
# image = np.array(image)  # 将Pillow图像转换为NumPy数组
# image = image.reshape(-1, 3)  # 将图像展平为二维数组

# # 使用KMeans聚类提取主色彩
# kmeans = KMeans(n_clusters=10, n_init=10, random_state=42)
# kmeans.fit(image)
# colors = kmeans.cluster_centers_  # 主色彩
# labels = kmeans.labels_  # 每个像素的标签


# complexity = calculate_color_complexity(image,kmeans, 10)
# harmony = calculate_color_harmony(image,kmeans, n_clusters)

# print(f"色彩复杂度: {complexity:.4f}")
# print(f"色彩协调度: {harmony:.4f}")
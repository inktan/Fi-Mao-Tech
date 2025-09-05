import cv2
import numpy as np
import pandas as pd
import os
from sklearn.cluster import KMeans
from scipy.stats import entropy

def calculate_visual_complexity(img, color_clusters=5):
    """
    计算图像的视觉复杂度（0~100）
    :param img: 已读取的图像数据
    :param color_clusters: 颜色聚类数量（默认5）
    :return: 综合复杂度评分和各项指标
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换为RGB格式
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # 转换为灰度图
    h, w = gray.shape[:2]
    total_pixels = h * w

    # 1. 边缘密度（Canny边缘检测）
    edges = cv2.Canny(gray, 100, 200)  # 边缘检测
    edge_pixels = np.sum(edges > 0)
    edge_density = edge_pixels / total_pixels  # 边缘像素占比

    # 2. 颜色多样性（K-Means聚类分析主色调分布）
    pixels = img_rgb.reshape(-1, 3)  # 展平像素
    kmeans = KMeans(n_clusters=color_clusters, random_state=42)
    kmeans.fit(pixels)
    cluster_counts = np.bincount(kmeans.labels_)
    color_distribution = cluster_counts / total_pixels  # 颜色分布概率
    color_diversity = entropy(color_distribution)  # 颜色分布的熵

    # 3. 信息熵（灰度图的熵值）
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist / total_pixels  # 归一化直方图
    gray_entropy = entropy(hist.flatten())  # 灰度熵

    # 标准化各项指标（映射到0~1）
    # 边缘密度：最大值约0.5（极端边缘图）
    edge_score = min(edge_density * 2, 1.0)
    # 颜色多样性：熵的最大值为log2(color_clusters)，标准化到0~1
    max_color_entropy = np.log2(color_clusters)
    color_score = color_diversity / max_color_entropy if max_color_entropy != 0 else 0
    # 灰度熵：最大值约8（2^8=256级灰度）
    gray_score = gray_entropy / 8.0

    # 综合评分（加权平均，权重可根据需求调整）
    weights = [0.3, 0.3, 0.4]  # 边缘、颜色、熵的权重
    complexity = (edge_score * weights[0] + color_score * weights[1] + gray_score * weights[2]) * 100
    
    # 返回所有指标
    return {
        'filename': '',
        'complexity': round(complexity, 2),
        'edge_density': round(edge_density, 4),
        'edge_score': round(edge_score, 4),
        'color_diversity': round(color_diversity, 4),
        'color_score': round(color_score, 4),
        'gray_entropy': round(gray_entropy, 4),
        'gray_score': round(gray_score, 4)
    }

def process_folder(folder_path, output_csv='visual_complexity.csv'):
    """
    处理文件夹中的所有图片并保存结果到CSV
    :param folder_path: 图片文件夹路径
    :param output_csv: 输出CSV文件名
    """
    # 支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
    
    # 收集所有结果
    results = []
    
    # 遍历文件夹
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            try:
                img_path = os.path.join(folder_path, filename)
                # img = cv2.imread(img_path)
                img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)

                if img is not None:
                    result = calculate_visual_complexity(img)
                    result['filename'] = filename  # 添加文件名
                    results.append(result)
                    print(f"处理完成: {filename} - 复杂度: {result['complexity']}")
                else:
                    print(f"警告: 无法读取图像 {filename}")
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")
    
    # 转换为DataFrame并保存
    if results:
        df = pd.DataFrame(results)
        # 重新排列列顺序
        columns = ['filename', 'complexity', 'edge_density', 'edge_score', 
                   'color_diversity', 'color_score', 'gray_entropy', 'gray_score']
        df = df[columns]
        df.to_csv(output_csv, index=False)
        print(f"结果已保存到 {output_csv}")
    else:
        print("没有找到可处理的图像文件")

# 示例用法
if __name__ == "__main__":
    folder_path = r"E:\work\sv_lntano1802\75补"  # 替换为你的文件夹路径
    output_csv =  r"E:\work\sv_lntano1802\visual_complexity_results.csv"  # 输出文件名
    
    if os.path.isdir(folder_path):
        process_folder(folder_path, output_csv)
    else:
        print(f"错误: 文件夹路径 {folder_path} 不存在")




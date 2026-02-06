import os
import pandas as pd
from PIL import Image
from tqdm import tqdm

def analyze_image_storage(folder_path):
    file_sizes = []
    resolutions = set()
    
    # 获取目录下所有文件
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not files:
        print("文件夹中未找到图片文件。")
        return

    print(f"正在分析 {len(files)} 张图片...")

    for file in tqdm(files):
        file_path = os.path.join(folder_path, file)
        # 获取文件大小 (Bytes)
        file_sizes.append(os.path.getsize(file_path))
        
        # 仅读取第一张图片的分辨率（假设如你所说全一致）
        if len(resolutions) == 0:
            with Image.open(file_path) as img:
                resolutions.add(img.size)

    # 转换为 DataFrame 方便计算
    df = pd.Series(file_sizes) / (1024 * 1024)  # 转换为 MB
    
    res_w, res_h = list(resolutions)[0]
    avg_size = df.mean()
    max_size = df.max()
    min_size = df.min()
    
    print("\n" + "="*30)
    print(f"分析报告 - 路径: {folder_path}")
    print(f"图片分辨率: {res_w} x {res_h}")
    print(f"样本数量: {len(files)} 张")
    print("-" * 30)
    print(f"平均单张大小: {avg_size:.2f} MB")
    print(f"最大单张大小: {max_size:.2f} MB")
    print(f"最小单张大小: {min_size:.2f} MB")
    print("-" * 30)
    print(f"预估 10,000 张所需空间: {avg_size * 10000 / 1024:.2f} GB")
    print(f"预估 1,000,000 张所需空间: {avg_size * 1000000 / 1024 / 1024:.2f} TB")
    print("="*30)

if __name__ == '__main__':
    target_path = r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\泉州市\sv_pan01'
    analyze_image_storage(target_path)
import pandas as pd
import numpy as np
import colorsys
import ast
from skimage import color

def process_rgb_csv(input_file, output_file):
    # 1. 读取 CSV 文件
    df = pd.read_csv(input_file)

    def parse_rgb(s):
        """将字符串格式的 '[r, g, b]' 转换为数值列表"""
        return ast.literal_eval(s)

    def rgb_to_hsl(rgb):
        """将 RGB (0-255) 转换为 HSL (H:0-360, S:0-100, L:0-100)"""
        r, g, b = [x / 255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return [round(h * 360, 2), round(s * 100, 2), round(l * 100, 2)]

    def rgb_to_lab(rgb):
        """将 RGB (0-255) 转换为 CIELAB"""
        # skimage 需要输入范围为 [0, 1] 的 3D 数组 (1, 1, 3)
        rgb_normalized = np.array(rgb).reshape(1, 1, 3) / 255.0
        lab = color.rgb2lab(rgb_normalized)
        return [round(x, 2) for x in lab.flatten().tolist()]

    # 2. 遍历 4 列数据进行转换
    for i in range(1, 5):
        rgb_col = f'rgb{i}'
        # 将字符串解析为列表
        rgb_series = df[rgb_col].apply(parse_rgb)
        
        # 添加 HSL 列
        df[f'hsl{i}'] = rgb_series.apply(rgb_to_hsl)
        
        # 添加 Lab 列
        df[f'Lab{i}'] = rgb_series.apply(rgb_to_lab)

    # 3. 保存结果
    df.to_csv(output_file, index=False)
    print(f"处理完成！结果已保存至: {output_file}")
    return df

# 使用示例
df_result = process_rgb_csv(r'e:\work\sv_npc\cluster_colors.csv', r'e:\work\sv_npc\cluster_colors01.csv')
import geopandas as gpd
import pandas as pd

# 1. 读取SHP文件
shp_file_path = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path, encoding='latin1')
gdf['name_2'] = gdf['name_2'].str.encode('latin1').str.decode('utf-8')  # 尝试 latin1 → gbk

# 2. 检查name_2列是否存在
if 'name_2' not in gdf.columns:
    print("错误：SHP文件中没有'name_2'列")
    print("可用列名：", gdf.columns.tolist())
else:
    # 3. 获取每个唯一值的第一行数据（可改为其他选择逻辑）
    unique_samples = gdf.drop_duplicates(subset=['name_2'], keep='first')
    
    # 4. 保存为CSV（不保存几何列）
    output_csv = r'E:\work\sv_daxiangshuaishuai\StreetViewSampling\unique_name_2_samples.csv'
    
    # 4.1 方法一：保存所有属性列（排除几何列）
    unique_samples.drop(columns='geometry').to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    # 4.2 方法二：只保存name_2和相关列（示例）
    # selected_cols = ['name_2', 'other_col1', 'other_col2']  # 选择需要的列
    # unique_samples[selected_cols].to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"提取完成，共找到 {len(unique_samples)} 个唯一值")
    print(f"结果已保存到: {output_csv}")
    print("\n示例数据：")
    print(unique_samples.head().drop(columns='geometry'))
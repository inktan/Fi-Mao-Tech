import geopandas as gpd
import os

# 设置文件夹路径
input_folder = r"E:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data"  # 替换为你的输入文件夹路径
output_folder = r"E:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data_32633"  # 替换为你的输出文件夹路径

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 遍历文件夹中的所有文件
for filename in os.listdir(input_folder):
    if filename.endswith(".shp"):
        # 构建完整文件路径
        input_path = os.path.join(input_folder, filename)
        
        # 读取SHP文件
        gdf = gpd.read_file(input_path)
        
        # 转换坐标系到EPSG:32633
        gdf = gdf.to_crs("EPSG:32633")
        
        # 构建输出文件路径
        output_path = os.path.join(output_folder, filename)
        
        # 保存为新的SHP文件
        gdf.to_file(output_path, encoding='utf-8')
        
        print(f"已处理: {filename}")

print("所有文件处理完成！")




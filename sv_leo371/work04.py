import os
import geopandas as gpd

# 配置参数
input_folder = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_with_avg"  # 替换为你的输入文件夹路径
output_folder = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_kmeans_class"  # 替换为你的输出文件夹路径
os.makedirs(output_folder, exist_ok=True)  # 创建输出文件夹(如果不存在)

# 需要提取的字段列表
target_fields = [
    'osm_id', 'code', 'fclass', 'name', 
    'oneway', 'maxspeed', 'layer', 
    'bridge', 'tunnel', 'fclass_cn', 'type', 'cluster'
]

# 遍历输入文件夹中的所有SHP文件
for shp_file in os.listdir(input_folder):
    if shp_file.endswith('02.shp'):
        input_path = os.path.join(input_folder, shp_file)
        output_path = input_path.replace('_with_avg_clustered02.shp','.shp').replace('output_lines_with_avg','output_lines_kmeans_class')
        
        print(f"正在处理文件: {shp_file}")
        
        try:
            # 读取SHP文件
            gdf = gpd.read_file(input_path)
            
            # 检查目标字段是否存在
            available_fields = [col for col in target_fields if col in gdf.columns]
            missing_fields = set(target_fields) - set(available_fields)
            
            if missing_fields:
                print(f"警告: 文件 {shp_file} 缺少以下字段: {', '.join(missing_fields)}")
            
            if not available_fields:
                print(f"错误: 文件 {shp_file} 不包含任何目标字段，跳过处理")
                continue
            
            # 提取目标字段(始终包含geometry字段)
            extracted_gdf = gdf[available_fields + ['geometry']]
            
            # 保存为新的SHP文件
            extracted_gdf.to_file(output_path)
            print(f"已保存提取后的文件: {output_path}")
            
        except Exception as e:
            print(f"处理文件 {shp_file} 时出错: {str(e)}")

print("所有文件处理完成！")
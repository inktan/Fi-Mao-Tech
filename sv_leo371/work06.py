import os
import geopandas as gpd

def process_shp_files(input_folder, output_folder):
    """
    处理文件夹中的所有SHP文件，仅保留osm_id列并保存到新文件夹
    
    参数:
        input_folder: 输入文件夹路径（包含SHP文件）
        output_folder: 输出文件夹路径（将保存处理后的SHP文件）
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历输入文件夹中的所有文件
    for file in os.listdir(input_folder):
        if file.endswith('.shp'):
            input_path = os.path.join(input_folder, file)
            input_path = r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省.shp'
            try:
                # 读取SHP文件

                gdf = gpd.read_file(input_path)
                
                # 检查是否存在osm_id列
                if 'osm_id' in gdf.columns:
                    # 仅保留osm_id列和几何列
                    gdf = gdf[['osm_id', gdf.geometry.name]]
                    
                    # 构建输出路径
                    # output_path = os.path.join(output_folder, file)
                    output_path = input_path.replace('.shp', '_osm_id.shp')
                    
                    # 保存为新的SHP文件
                    gdf.to_file(output_path)
                    print(f"处理成功: {file} -> {output_path}")
                    break
                else:
                    print(f"跳过 {file}: 未找到osm_id列")
                    
            except Exception as e:
                print(f"处理 {file} 时出错: {str(e)}")

# 使用示例
if __name__ == "__main__":
    input_folder = r"E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines"  # 替换为你的输入文件夹路径
    output_folder = r"E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines01"  # 替换为输出文件夹路径
    
    process_shp_files(input_folder, output_folder)
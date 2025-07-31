import os
import geopandas as gpd

def find_shp_files(root_dir):
    """递归查找目录下所有的.shp文件"""
    shp_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.shp'):
                shp_files.append(os.path.join(root, file))
    return shp_files

def process_shp_files(shp_files):
    """处理所有找到的shp文件，删除指定列并保存"""
    for shp_file in shp_files:
        try:
            # 读取shapefile
            gdf = gpd.read_file(shp_file)
            
            # 检查是否存在'statement'列
            if 'statement' in gdf.columns:
                # 删除指定列
                gdf = gdf.drop(columns=['statement'])
                
                # 保存修改后的文件（覆盖原文件）
                gdf.to_file(shp_file)
                print(f"已处理文件: {shp_file}")
            else:
                print(f"文件 {shp_file} 中没有'statement'列，跳过处理")
                
        except Exception as e:
            print(f"处理文件 {shp_file} 时出错: {str(e)}")

if __name__ == "__main__":
    # 设置要搜索的根目录
    root_directory =r'F:\立方数据\2025年道路数据'
    
    # 查找所有.shp文件
    shapefiles = find_shp_files(root_directory)
    
    if not shapefiles:
        print("没有找到任何.shp文件")
    else:
        print(f"找到 {len(shapefiles)} 个.shp文件:")
        for sf in shapefiles:
            print(sf)
        
        # 处理所有找到的.shp文件
        process_shp_files(shapefiles)
        print("处理完成")
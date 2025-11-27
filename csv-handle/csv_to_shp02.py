import os
import glob
import pandas as pd
import geopandas as gpd
from pathlib import Path

def convert_csv_to_shp(csv_file_path):
    """
    将CSV文件转换为SHP文件
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file_path)
        
        # 检查必要的列是否存在
        if 'longitude' not in df.columns or 'latitude' not in df.columns:
            print(f"跳过文件 {csv_file_path}，缺少longitude或latitude列")
            return None
        
        # 创建GeoDataFrame
        dst_crs = 'EPSG:4326'
        gdf = gpd.GeoDataFrame(
            df, 
            geometry=gpd.points_from_xy(df.longitude, df.latitude), 
            crs=dst_crs
        )
        
        # 构建新的SHP文件路径
        csv_path = Path(csv_file_path)
        
        # 替换路径中的字段名
        new_dir_path = str(csv_path.parent).replace(
            '分城市的道路数据_50m_svinof_csv', 
            '分城市的道路数据_50m_svinof_shp'
        )
        
        # 确保目标目录存在
        os.makedirs(new_dir_path, exist_ok=True)
        
        # 构建SHP文件路径（保持相同的文件名，但扩展名为.shp）
        shp_file_path = os.path.join(
            new_dir_path, 
            csv_path.stem + '.shp'
        )
        
        # 保存为SHP文件
        gdf.to_file(shp_file_path, driver='ESRI Shapefile')
        print(f"成功转换: {csv_file_path} -> {shp_file_path}")
        
        return shp_file_path
        
    except Exception as e:
        print(f"转换文件 {csv_file_path} 时出错: {str(e)}")
        return None

def main():
    # 根目录路径
    root_dir = r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_svinof_csv'
    
    # 查找所有CSV文件（包括嵌套文件夹）
    csv_pattern = os.path.join(root_dir, '**', '*.csv')
    csv_files = glob.glob(csv_pattern, recursive=True)
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 转换每个CSV文件
    successful_conversions = 0
    for csv_file in csv_files:
        result = convert_csv_to_shp(csv_file)
        if result:
            successful_conversions += 1
    
    print(f"转换完成！成功转换 {successful_conversions}/{len(csv_files)} 个文件")

if __name__ == "__main__":
    main()
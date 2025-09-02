import geopandas as gpd
import pandas as pd

def merge_shapefiles(shp1_path, shp2_path, output_path):
    """
    合并两个SHP文件（按行方向）
    
    参数:
    shp1_path: 第一个SHP文件路径
    shp2_path: 第二个SHP文件路径
    output_path: 输出SHP文件路径
    """
    
    try:
        # 1. 读取两个SHP文件
        print(f"正在读取文件: {shp1_path}")
        gdf1 = gpd.read_file(shp1_path)
        print(f"文件1包含 {len(gdf1)} 个要素")
        
        print(f"正在读取文件: {shp2_path}")
        gdf2 = gpd.read_file(shp2_path)
        print(f"文件2包含 {len(gdf2)} 个要素")
        
        # 2. 检查坐标系是否一致
        if gdf1.crs != gdf2.crs:
            print("警告: 两个文件的坐标系不一致，正在将文件2转换为文件1的坐标系")
            gdf2 = gdf2.to_crs(gdf1.crs)
        
        # 3. 检查字段结构
        print("\n文件1字段:", list(gdf1.columns))
        print("文件2字段:", list(gdf2.columns))
        
        # 4. 统一字段结构（可选）
        # 找出两个文件共有的字段
        common_columns = list(set(gdf1.columns) & set(gdf2.columns))
        print(f"共有字段: {common_columns}")
        
        # 如果字段结构不同，可以选择只保留共有字段
        if set(gdf1.columns) != set(gdf2.columns):
            print("字段结构不同，将只保留共有字段进行合并")
            gdf1 = gdf1[common_columns]
            gdf2 = gdf2[common_columns]
        
        # 5. 按行合并（纵向合并）
        print("正在合并文件...")
        merged_gdf = pd.concat([gdf1, gdf2], ignore_index=True)
        
        # 6. 确保结果仍然是GeoDataFrame
        if not isinstance(merged_gdf, gpd.GeoDataFrame):
            merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry', crs=gdf1.crs)
        
        # 7. 保存合并后的文件
        print(f"合并后共 {len(merged_gdf)} 个要素")
        merged_gdf.to_file(output_path, driver='ESRI Shapefile')
        print(f"合并完成！已保存到: {output_path}")
        
        return merged_gdf
        
    except Exception as e:
        print(f"合并过程中出现错误: {str(e)}")
        raise

# 使用示例
if __name__ == "__main__":
    # 输入文件路径
    shp_file1 = r"e:\work\sv_xiufenganning\20250819\ade_20k_语义00分割比例数据_03-_gcj02.shp"
    shp_file2 = r"e:\work\sv_xiufenganning\20250819\ade_20k_语义分割比例数据_01-_bd09.shp"
    
    # 输出文件路径
    output_file = r"e:\work\sv_xiufenganning\20250819\ade_20k_语义分割比例数据_bd09.shp"
    
    # 执行合并
    try:
        result = merge_shapefiles(shp_file1, shp_file2, output_file)
        print("\n合并成功！")
        print(f"总要素数量: {len(result)}")
        print(f"坐标系: {result.crs}")
        
    except Exception as e:
        print(f"合并失败: {e}")
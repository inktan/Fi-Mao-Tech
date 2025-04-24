import geopandas as gpd

def filter_points_by_y(input_shp, output_shp, y_threshold=22.176076):
    """
    过滤点SHP文件中Y坐标小于指定值的点
    
    参数:
        input_shp: 输入点SHP文件路径
        output_shp: 输出SHP文件路径
        y_threshold: Y坐标阈值
    """
    try:
        # 1. 读取SHP文件
        gdf = gpd.read_file(input_shp)
        
        # 2. 检查是否是点图层
        if not all(gdf.geometry.type == 'Point'):
            print("错误: 输入文件不是点图层")
            return False
        
        # 3. 提取Y坐标并过滤
        gdf['y_coord'] = gdf.geometry.y
        filtered_gdf = gdf[gdf['y_coord'] < y_threshold].copy()
        
        # 4. 检查是否有数据保留
        if len(filtered_gdf) == 0:
            print("警告: 没有点满足Y坐标小于{}的条件".format(y_threshold))
            return False
        
        # 5. 保存结果
        filtered_gdf.to_file(output_shp, encoding='utf-8')
        print("成功保存过滤后的点数据到:", output_shp)
        print("原始点数:", len(gdf), "| 过滤后点数:", len(filtered_gdf))
        return True
        
    except Exception as e:
        print("处理过程中发生错误:", e)
        return False

# 使用示例
if __name__ == "__main__":
    input_file = r"e:\work\sv_shushu\20250423\all_points01\all_points_Spatial_Balance.shp"  # 替换为你的输入SHP文件路径
    output_file = r"e:\work\sv_shushu\20250423\all_points01\all_points_Spatial_Balance01.shp"  # 替换为你想要的输出路径
    
    filter_points_by_y(input_file, output_file, y_threshold=22.176076)
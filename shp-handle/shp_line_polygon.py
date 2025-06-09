import geopandas as gpd

def extract_lines_on_polygons(line_shp_path, polygon_shp_path, output_shp_path):
    """
    读取线状和面状SHP文件，提取落在面上的线，并保存为新SHP文件
    
    参数:
        line_shp_path: 线状SHP文件路径
        polygon_shp_path: 面状SHP文件路径
        output_shp_path: 输出SHP文件路径
    """
    # 读取SHP文件
    lines = gpd.read_file(line_shp_path)
    polygons = gpd.read_file(polygon_shp_path)
    polygons = polygons[polygons['县名'] == r'秦淮区']  # 或 polygons['NAME']等
    
    # 确保两个文件使用相同的坐标参考系统(CRS)
    if lines.crs != polygons.crs:
        polygons = polygons.to_crs(lines.crs)
    
    # 合并所有多边形为一个几何体（如果需要处理多个多边形）
    combined_polygon = polygons.unary_union
    
    # 找出完全或部分落在多边形内的线
    # 使用within检查完全在面内的线，或者使用intersects检查与面相交的线
    lines_on_polygons = lines[lines.intersects(combined_polygon)]
    
    # 保存结果
    lines_on_polygons.to_file(output_shp_path)
    
    print(f"成功保存落在面上的线到: {output_shp_path}")
    print(f"共找到 {len(lines_on_polygons)} 条符合条件的线")

# 使用示例
if __name__ == "__main__":
    line_shp = r"f:\立方数据\2025年道路数据\【立方数据学社】南京市\南京市.shp"  # 替换为你的线SHP文件路径
    polygon_shp = r"f:\立方数据\202405更新_2024年省市县三级行政区划数据（审图号：GS（2024）0650号）\shp格式的数据（调整过行政区划代码，补全省市县信息）\县.shp"  # 替换为你的面SHP文件路径
    output_shp = r"E:\work\sv_nanjing_qinhuaiqu/lines_on_polygons.shp"  # 替换为你想要的输出路径
    
    extract_lines_on_polygons(line_shp, polygon_shp, output_shp)
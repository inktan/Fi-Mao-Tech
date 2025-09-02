import geopandas as gpd

def filter_and_save_visibility_columns(input_shp, output_shp):
    gdf = gpd.read_file(input_shp)
    
    # 定义要保留的列（不区分大小写）
    columns_to_keep = ['地点', '地址', 'Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis','Arch_Vis']
    
    # 查找实际存在于数据中的列（不区分大小写）
    existing_cols = []
    for col in columns_to_keep:
        # 检查列是否存在（不区分大小写）
        matching_cols = [c for c in gdf.columns if c.lower() == col.lower()]
        if matching_cols:
            existing_cols.extend(matching_cols)
        else:
            print(f"警告: 列 '{col}' 不存在于数据中")
    
    # 确保至少保留几何列
    if not existing_cols:
        raise ValueError("错误: 数据中未找到任何指定的可视率列")
    
    # 添加几何列到保留列中
    existing_cols.append(gdf.geometry.name)
    
    # 只保留指定列
    gdf_filtered = gdf[existing_cols]
    
    # 保存结果到新SHP文件
    gdf_filtered.to_file(output_shp, encoding='utf-8')
    
    print(f"处理完成！结果已保存到: {output_shp}")
    print("保留的列:", list(gdf_filtered.columns))

if __name__ == "__main__":
    input_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_07.shp"  # 输出文件路径
    output_file = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_08.shp"  # 输出文件路径
    filter_and_save_visibility_columns(input_file, output_file)

# 莫拉指数分析
# 地理加权回归分析
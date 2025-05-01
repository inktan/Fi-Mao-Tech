import geopandas as gpd

def remove_columns_and_save(input_shp, output_shp, columns_to_remove=['ylight', 'road2', 'Join_Count']):
    """
    删除指定列并保存为新的SHP文件
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
        columns_to_remove: 要删除的列名列表(默认为['ylight', 'road2', 'Join_Count'])
    """
    # 读取SHP文件
    gdf = gpd.read_file(input_shp)
    
    # 检查要删除的列是否存在
    existing_columns = [col for col in columns_to_remove if col in gdf.columns]
    
    if not existing_columns:
        print("没有找到要删除的列，文件将原样保存")
    else:
        print(f"将删除以下列: {existing_columns}")
        # 删除指定列
        gdf = gdf.drop(columns=existing_columns)
    
    # 保存结果
    gdf.to_file(output_shp)
    print(f"处理完成，结果已保存到 {output_shp}")

if __name__ == "__main__":
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        
        # 设置路径
        input_file = f'e:\\work\\sv_goufu\\MLP20250428\\year{year}_03_predictions.shp'
        output_file = input_file.replace('MLP20250428', 'results').replace('_03_predictions.shp', '_predict.shp')
        
        try:
            remove_columns_and_save(input_file, output_file)
        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")
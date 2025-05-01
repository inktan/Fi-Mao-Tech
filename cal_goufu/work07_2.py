import geopandas as gpd

def copy_non_zero_join_count(input_shp, output_shp):
    """
    将Join_Count列中的非0数据赋给predict_列并保存为新文件
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
    """
    # 读取SHP文件
    gdf = gpd.read_file(input_shp)
    
    # 检查Join_Count列是否存在
    if 'Join_Count' not in gdf.columns:
        raise ValueError("输入SHP文件中缺少'Join_Count'列")
    
    # 创建或更新predict_列
    if 'predict_' not in gdf.columns:
        gdf['predict_'] = 0  # 先初始化为0
    
    gdf['predict_'] = gdf['predict_']*10

    # 将Join_Count的非0值赋给predict_
    mask = gdf['Join_Count'] != 0
    gdf.loc[mask, 'predict_'] = gdf.loc[mask, 'Join_Count']
    
    # 保存结果
    gdf.to_file(output_shp)
    print(f"处理完成，结果已保存到 {output_shp}")

if __name__ == "__main__":
    years = ['00','05','10','15','20','24']

    for year in years:
        print(year)
        # main(year)

        input_file = f"e:\\work\\sv_goufu\\MLP20250428\\year{year}_02_predictions.shp"  # 替换为你的输入文件路径
        output_file = f"e:\\work\\sv_goufu\\MLP20250428\\year{year}_03_predictions.shp"  # 替换为你想要的输出文件路径
        
        try:
            copy_non_zero_join_count(input_file, output_file)
        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")
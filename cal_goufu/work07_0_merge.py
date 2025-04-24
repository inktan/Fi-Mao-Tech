import geopandas as gpd

def transfer_predict_values(base_shp_path, predict_shp_path, output_path):
    # 读取两个Shapefile
    base_gdf = gpd.read_file(base_shp_path)
    predict_gdf = gpd.read_file(predict_shp_path)
    
    # 创建预测值字典 {uid: predict_value}
    predict_dict = dict(zip(predict_gdf['uid'], predict_gdf['predicted_']))
    
    # 将预测值赋给基础Shapefile
    base_gdf['predicted_'] = base_gdf['uid'].map(predict_dict).fillna(-9999)
    
    # 保存结果
    base_gdf.to_file(output_path)
    print(f"处理完成，结果已保存到: {output_path}")

# 使用示例
# 使用示例
years = ['98','99','00',
'01','02','03','04','05','06','07','08','09','10',
'11','12','13','14','15','16','17','18','19','20',
'22','23',]

for year in years:
    print(year)
    try:
        # 设置路径
        base_shp = f'e:\\work\\sv_goufu\\MLP\\year{year}\\year{year}.shp'
        predict_shp = f"e:\\work\\sv_goufu\\MLP\\year{year}\\year{year}_valid_data_with_predictions.shp"
        output_shp = base_shp.replace('.shp', '_final_predictions.shp')
        
        # 执行预测值转移
        transfer_predict_values(base_shp, predict_shp, output_shp)
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

# base_shp = f"e:\\work\\sv_goufu\MLP\\year21\\year21.shp"
# predict_shp = f"e:\\work\\sv_goufu\\MLP\\year21\\year21_valid_data_with_predictions.shp"
# output_shp = base_shp.replace('.shp', '_final_predictions.shp')

# transfer_predict_values(base_shp, predict_shp, output_shp)
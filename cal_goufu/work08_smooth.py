import geopandas as gpd
import numpy as np

def smooth_predicted_values(shp_path, output_path, field_name='predicted_'):
    """
    对Shapefile中的预测值进行平滑处理，使其均匀分布在最大值和最小值之间
    
    参数:
        shp_path: 输入的Shapefile路径
        output_path: 输出Shapefile路径
        field_name: 要平滑处理的字段名(默认为'predicted_')
    """
    # 读取Shapefile
    gdf = gpd.read_file(shp_path)
    
    # 检查字段是否存在
    if field_name not in gdf.columns:
        raise ValueError(f"字段 '{field_name}' 不存在于Shapefile中")
    
    # 获取原始值并排序
    original_values = gdf[field_name].values
    sorted_indices = np.argsort(original_values)
    sorted_values = original_values[sorted_indices]
    
    # 计算均匀分布的新值
    min_val = np.min(sorted_values)
    max_val = np.max(sorted_values)
    n = len(sorted_values)
    uniform_values = np.linspace(min_val, max_val, n)
    
    # 恢复原始顺序
    smoothed_values = np.empty_like(uniform_values)
    smoothed_values[sorted_indices] = uniform_values
    
    # 更新GeoDataFrame
    gdf[field_name] = smoothed_values
    
    # 保存结果
    gdf.to_file(output_path)
    print(f"平滑处理完成，结果已保存到: {output_path}")
    print(f"原始值范围: {min_val} - {max_val}")
    print(f"处理后值范围: {np.min(smoothed_values)} - {np.max(smoothed_values)}")

# 使用示例
years = ['98','99','00',
'01','02','03','04','05','06','07','08','09','10',
'11','12','13','14','15','16','17','18','19','20',
'22','23',]

for year in years:
    print(year)
    try:
        # 设置路径
        input_shp = f'e:\\work\\sv_goufu\\MLP\\year{year}\\year{year}_final_predictions_01.shp'
        output_shp = input_shp.replace('.shp', '_smoothed.shp')
        
        # 执行平滑处理
        smooth_predicted_values(input_shp, output_shp)
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

# input_shp = r"e:\work\sv_goufu\MLP\year21\汇总数据-面\year21_final_predictions_01.shp"
# output_shp = input_shp.replace('_01.shp', '_02.shp')

# smooth_predicted_values(input_shp, output_shp)
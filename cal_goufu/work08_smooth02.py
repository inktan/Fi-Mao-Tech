import geopandas as gpd
import numpy as np

def smooth_predicted_values_accelerated(
    shp_path, 
    output_path, 
    field_name='predicted_', 
    target_range=None,
    power=0.5  # 控制非线性程度，0.5表示平方根变换
):
    """
    对Shapefile中的预测值进行非线性平滑处理，使小数值变化大，大数值变化小
    
    参数:
        shp_path: 输入的Shapefile路径
        output_path: 输出Shapefile路径
        field_name: 要平滑处理的字段名(默认为'predicted_')
        target_range: 目标范围(元组形式，如(min, max))
        power: 非线性变换的幂指数（0< power <1，越小则小数值拉伸越强）
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
    
    min_val = np.min(sorted_values)
    max_val = np.max(sorted_values)
    n = len(sorted_values)
    
    # 使用目标范围或原始范围
    if target_range is not None:
        target_min, target_max = target_range
    else:
        target_min, target_max = min_val, max_val
    
    # 非线性变换（拉伸小数值，压缩大数值）
    # 归一化到[0,1]后应用幂变换
    normalized = (sorted_values - min_val) / (max_val - min_val)
    transformed = normalized ** power
    
    # 在变换后的空间内均匀插值
    uniform_transformed = np.linspace(0, 1, n) ** (1/power)  # 逆变换调整
    
    # 映射到目标范围
    uniform_values = uniform_transformed * (target_max - target_min) + target_min
    
    # 恢复原始顺序
    smoothed_values = np.empty_like(uniform_values)
    smoothed_values[sorted_indices] = uniform_values
    
    # 更新GeoDataFrame
    gdf[field_name] = smoothed_values
    
    # 保存结果
    gdf.to_file(output_path)
    print(f"非线性平滑处理完成，结果已保存到: {output_path}")
    print(f"原始值范围: {min_val:.2f} - {max_val:.2f}")
    print(f"处理后值范围: {np.min(smoothed_values):.2f} - {np.max(smoothed_values):.2f}")

# 定义年份和对应的目标范围
year_ranges = {
    '00': (0, 4016),
    '05': (0, 7216),
    '10': (0, 10065),
    '15': (0, 13245),
    '20': (0, 16338),
    '24': (0, 21084)
}

# 处理每个年份的数据
for year, target_range in year_ranges.items():
    print(f"\n处理年份: 20{year}")
    try:
        # 设置路径
        input_shp = f'e:\\work\\sv_goufu\\MLP2025042801\\year{year}_valid_data_with_predictions.shp'
        output_shp = input_shp.replace('MLP2025042801', 'MLP202504280101').replace('valid_data_with_predictions.shp', '_smoothed.shp')
        
        # 执行非线性平滑处理，power参数控制非线性程度
        smooth_predicted_values_accelerated(
            input_shp, 
            output_shp, 
            target_range=target_range,
            power=0.4  # 可调整（0.3-0.6之间效果较好）
        )
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
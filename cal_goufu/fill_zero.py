import geopandas as gpd
from pysal.lib import weights
import numpy as np

def fill_zero_join_count(shp_path, output_path, join_count_field='Join_Count'):
    """
    基于空间关系填充 SHP 文件中 join_count 为 0 的值
    
    参数:
        shp_path: 输入的 SHP 文件路径
        output_path: 输出的 SHP 文件路径
        join_count_field: join_count 字段名
    """
    # 1. 读取 SHP 文件
    gdf = gpd.read_file(shp_path)
    
    # 2. 检查 join_count 字段是否存在
    if join_count_field not in gdf.columns:
        raise ValueError(f"字段 '{join_count_field}' 不存在于 SHP 文件中")
    
    # 3. 创建空间权重矩阵 (这里使用 Queen 邻接关系)
    w = weights.Queen.from_dataframe(gdf)
    
    # 4. 标识需要填充的 0 值位置
    join_counts = gdf[join_count_field].values
    zero_mask = join_counts == 0
    
    # 5. 对每个需要填充的位置，计算邻域非零值的平均值
    for i in np.where(zero_mask)[0]:
        neighbors = w.neighbors[i]
        if not neighbors:  # 如果没有邻居，跳过
            continue
            
        # 获取邻居的非零值
        neighbor_values = [join_counts[j] for j in neighbors if join_counts[j] > 0]
        
        if neighbor_values:  # 如果有非零邻居值
            # 使用邻居的中位数填充 (比平均值更抗异常值)
            gdf.loc[i, join_count_field] = np.median(neighbor_values)
        else:
            # 如果没有非零邻居，可以尝试扩大邻域范围
            # 这里简单保持为0，或者可以实现更复杂的逻辑
            pass
    
    # 6. 保存结果
    gdf.to_file(output_path)
    print(f"处理完成，结果已保存到: {output_path}")

# 使用示例
if __name__ == "__main__":
    input_shp = r"e:\work\sv_goufu\datatrain\bird02\tongji\tj21.shp"  # 替换为你的输入SHP文件路径
    output_shp = r"e:\work\sv_goufu\datatrain\bird02\tongji02\tj21.shp"  # 替换为你想保存的输出路径
    
    fill_zero_join_count(input_shp, output_shp)
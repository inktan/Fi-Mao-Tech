import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm  # 用于显示进度条

def fill_all_missing_values(input_shp, output_shp, missing_value=-9999, power=2, k=5, min_non_missing=5):
    """
    使用反距离加权插值(IDW)填充所有数值型属性列的缺失值
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
        missing_value: 缺失值标记(默认为-9999)
        power: IDW的幂参数(默认为2)
        k: 使用的最近邻点数量(默认为5)
        min_non_missing: 每列至少需要有多少非缺失值才进行插值(默认为5)
    """
    # 读取SHP文件
    gdf = gpd.read_file(input_shp)
    
    # 获取所有数值型列(排除几何列和非数值列)
    numeric_cols = gdf.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        print("没有找到数值型属性列，无需处理")
        return
    
    print(f"将处理以下数值型列: {numeric_cols}")
    
    # 准备有效点和缺失点的坐标
    coords = np.array([(geom.x, geom.y) for geom in gdf.geometry])
    tree = cKDTree(coords)
    
    # 对每个数值列进行处理
    for col in tqdm(numeric_cols, desc="处理列"):
        # 找出当前列的缺失值位置
        missing_mask = (gdf[col] == missing_value) | gdf[col].isna()
        missing_indices = missing_mask[missing_mask].index.tolist()
        
        if not missing_indices:
            continue  # 没有缺失值，跳过
            
        # 获取非缺失值点和它们的值
        valid_mask = ~missing_mask
        valid_values = gdf.loc[valid_mask, col].values
        
        # 如果非缺失值太少，跳过该列
        if len(valid_values) < min_non_missing:
            print(f"\n列 {col} 非缺失值太少({len(valid_values)}个)，跳过插值")
            continue
        
        # 标准化数据(可选，对于不同量纲的列有帮助)
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(valid_values.reshape(-1, 1)).flatten()
        
        # 对每个缺失点进行插值
        for idx in missing_indices:
            point = gdf.geometry[idx]
            x, y = point.x, point.y
            
            # 查询k个最近的非缺失值点
            # 注意: 我们需要查询的是非缺失值点的索引
            valid_coords = coords[valid_mask]
            valid_tree = cKDTree(valid_coords)
            distances, valid_indices = valid_tree.query([x, y], k=min(k, len(valid_values)))
            
            # 防止距离为0的情况
            distances = np.where(distances == 0, 1e-12, distances)
            
            # 计算权重
            weights = 1.0 / (distances ** power)
            weights /= weights.sum()  # 归一化
            
            # 计算加权平均值(使用标准化后的值)
            interpolated_scaled = np.sum(scaled_values[valid_indices] * weights)
            
            # 反标准化得到原始值
            interpolated_value = scaler.inverse_transform([[interpolated_scaled]])[0][0]
            
            # 更新值
            gdf.at[idx, col] = interpolated_value
    
    # 保存结果
    gdf.to_file(output_shp)
    print(f"\n处理完成，结果已保存到 {output_shp}")

# 使用示例
fill_all_missing_values(r'e:\work\sv_goufu\MLP\year21\MLP21_point.shp', r'e:\work\sv_goufu\MLP\year21\MLP21_point_filled.shp')
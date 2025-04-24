import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

def fill_polygon_missing_values(input_shp, output_shp, missing_value=-9999, power=2, k=5, min_non_missing=5):
    """
    使用基于多边形质心的IDW方法填充所有数值型属性列的缺失值
    
    参数:
        input_shp: 输入SHP文件路径
        output_shp: 输出SHP文件路径
        missing_value: 缺失值标记(默认为-9999)
        power: IDW的幂参数(默认为2)
        k: 使用的最近邻多边形数量(默认为5)
        min_non_missing: 每列至少需要有多少非缺失值才进行插值(默认为5)
    """
    # 读取SHP文件
    gdf = gpd.read_file(input_shp)
    
    # 获取所有数值型列
    # numeric_cols = gdf.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = ['predicted_']
    
    if not numeric_cols:
        print("没有找到数值型属性列，无需处理")
        return
    
    print(f"将处理以下数值型列: {numeric_cols}")
    
    # 计算多边形质心坐标
    centroids = np.array([(geom.centroid.x, geom.centroid.y) for geom in gdf.geometry])
    tree = cKDTree(centroids)
    
    # 对每个数值列进行处理
    for col in tqdm(numeric_cols, desc="处理列"):
        # 找出当前列的缺失值位置
        missing_mask = (gdf[col] == missing_value) | gdf[col].isna()
        missing_indices = missing_mask[missing_mask].index.tolist()
        
        if not missing_indices:
            continue
            
        # 获取非缺失值多边形和它们的值
        valid_mask = ~missing_mask
        valid_values = gdf.loc[valid_mask, col].values
        
        if len(valid_values) < min_non_missing:
            print(f"\n列 {col} 非缺失值太少({len(valid_values)}个)，跳过插值")
            continue
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(valid_values.reshape(-1, 1)).flatten()
        
        # 对每个缺失多边形进行插值
        for idx in missing_indices:
            centroid = gdf.geometry[idx].centroid
            x, y = centroid.x, centroid.y
            
            # 查询k个最近的非缺失值多边形
            valid_centroids = centroids[valid_mask]
            valid_tree = cKDTree(valid_centroids)
            distances, valid_indices = valid_tree.query([x, y], k=min(k, len(valid_values)))
            
            distances = np.where(distances == 0, 1e-12, distances)
            weights = 1.0 / (distances ** power)
            weights /= weights.sum()
            
            # 计算加权平均值
            interpolated_scaled = np.sum(scaled_values[valid_indices] * weights)
            interpolated_value = scaler.inverse_transform([[interpolated_scaled]])[0][0]
            
            gdf.at[idx, col] = interpolated_value
    
    # 保存结果
    gdf.to_file(output_shp)
    print(f"\n处理完成，结果已保存到 {output_shp}")

# 使用示例
years = ['98','99','00',
'01','02','03','04','05','06','07','08','09','10',
'11','12','13','14','15','16','17','18','19','20',
'22','23',]

for year in years:
    print(year)
    try:
        # 输入和输出文件路径
        input_shapefile = f'e:\\work\\sv_goufu\\MLP\\year{year}\\year{year}_final_predictions.shp'
        output_shapefile = input_shapefile.replace('.shp', '_01.shp')
        
        fill_polygon_missing_values(input_shapefile, output_shapefile)
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


# input_shapefile = r'e:\work\sv_goufu\MLP\year21\汇总数据-面\year21_final_predictions.shp'
# output_shapefile = input_shapefile.replace('.shp', '_01.shp')

# fill_polygon_missing_values(input_shapefile, output_shapefile)




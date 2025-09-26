import geopandas as gpd
import pandas as pd
from scipy.spatial import cKDTree
import numpy as np

def find_nearest_points_with_commonname(shp1_path, shp2_path, output_csv, k=15):
    """
    找到第一个shp文件中每个点最近的5个第二个shp文件中的点，并保存CommonName列到CSV
    
    参数:
    shp1_path: 第一个shp文件路径
    shp2_path: 第二个shp文件路径  
    output_csv: 输出CSV文件路径
    k: 要查找的最近点数量，默认为5
    """
    
    # 读取两个shp文件
    print("正在读取shp文件...")
    gdf1 = gpd.read_file(shp1_path)
    gdf1 = gdf1.to_crs("EPSG:4326")

    gdf2 = gpd.read_file(shp2_path)
    gdf2 = gdf2.to_crs("EPSG:4326")
    
    # 确保都是点数据
    if not all(gdf1.geometry.type == 'Point'):
        raise ValueError("第一个shp文件不是点数据")
    if not all(gdf2.geometry.type == 'Point'):
        raise ValueError("第二个shp文件不是点数据")
    
    # 检查第二个shp文件是否有CommonName列
    if 'CommonName' not in gdf2.columns:
        raise ValueError("第二个shp文件中没有CommonName列")
    
    # 提取坐标
    print("提取坐标...")
    coords1 = np.array([(geom.x, geom.y) for geom in gdf1.geometry])
    coords2 = np.array([(geom.x, geom.y) for geom in gdf2.geometry])
    
    # 构建KD树用于快速最近邻搜索
    print("构建KD树...")
    tree = cKDTree(coords2)
    
    # 查找每个点的最近k个点
    print("查找最近点...")
    distances, indices = tree.query(coords1, k=k)
    
    # 准备结果数据
    results = []
    
    # 遍历第一个shp文件的每个点
    for i, (idx, row) in enumerate(gdf1.iterrows()):
        # 获取当前点的最近k个点在第二个shp中的索引
        nearest_indices = indices[i]
        
        # 获取这些点的CommonName
        common_names = gdf2.iloc[nearest_indices]['CommonName'].tolist()
        
        # 添加到结果中
        results.append({
            'source_index': i,
            'nearest_commonname': common_names,
        })
    
        # 获取距离
        dists = distances[i]
        # for j, (name, dist) in enumerate(zip(common_names, dists)):
        #     results.append({
        #         'source_index': i,
        #         'source_id': idx,
        #         'nearest_rank': j + 1,  # 排名，1表示最近
        #         'nearest_commonname': name,
        #         'distance': dist
        #     })
    
    # 转换为DataFrame
    result_df = pd.DataFrame(results)
    
    # 保存为CSV
    print(f"保存结果到 {output_csv}...")
    result_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"完成！共处理了 {len(gdf1)} 个点，保存了 {len(result_df)} 条记录")
    
    return result_df

# 使用示例
if __name__ == "__main__":
    # 替换为您的文件路径

    shp1_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data_32633\CoS_GSV_30m_points.shp'  # 替换为你的SHP文件路径
    shp2_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_streettree_data.shp'  # 替换为你的SHP文件路径

    output_csv = r"E:\work\sv_pangpang\out\nearest_points_commonname.csv"
    
    # 执行函数
    result = find_nearest_points_with_commonname(shp1_path, shp2_path, output_csv)
    
    # 显示前几行结果
    print("\n结果预览:")
    print(result.head())
import geopandas as gpd
from shapely.geometry import Point
import os
import pandas as pd

# 定义输入SHP文件路径列表
shp_paths = [
    r'e:\work\sv_juanjuanmao\澳门特别行政区\澳门特别行政区_15m_.shp',
    r'e:\work\sv_shushu\20250423\points.shp',
    r'e:\work\sv_shushu\20250423\澳门特别行政区_矢量路网\点.shp'
]

# 创建空的GeoDataFrame用于存储所有点
merged_points = gpd.GeoDataFrame()

# 遍历所有SHP文件
for shp_path in shp_paths:
    try:
        # 读取SHP文件
        gdf = gpd.read_file(shp_path)
        
        # 只保留点几何类型 (Point, MultiPoint)
        point_gdf = gdf[gdf.geometry.type.isin(['Point', 'MultiPoint'])].copy()
        
        # 如果有多点(MultiPoint)几何，将其拆分为单个点
        if 'MultiPoint' in point_gdf.geometry.type.unique():
            # 拆分MultiPoint为单个Point
            exploded_points = point_gdf.explode(index_parts=True)
            point_gdf = exploded_points[exploded_points.geometry.type == 'Point']
        
        # 如果点数据不为空，则添加到合并的数据集中
        if not point_gdf.empty:
            # 确保所有数据使用相同的坐标系(以第一个文件的CRS为准)
            if merged_points.empty:
                crs = point_gdf.crs
                merged_points = gpd.GeoDataFrame(columns=point_gdf.columns, crs=crs)
            
            # 转换到目标CRS
            point_gdf = point_gdf.to_crs(merged_points.crs)
            
            # 添加来源文件信息
            point_gdf['source_file'] = os.path.basename(shp_path)
            
            # 合并数据
            merged_points = gpd.GeoDataFrame(
                pd.concat([merged_points, point_gdf], ignore_index=True),
                crs=merged_points.crs
            )
            
    except Exception as e:
        print(f"处理文件 {shp_path} 时出错: {str(e)}")
        continue

# 检查是否有合并后的点数据
if merged_points.empty:
    print("没有找到任何点数据!")
else:
    # 定义输出路径
    output_shp =r'E:\work\sv_shushu\20250423\all_points.shp'
    
    # 保存合并后的点数据为新的Shapefile
    merged_points.to_file(output_shp, encoding='utf-8')
    print(f"成功合并 {len(merged_points)} 个点，已保存至: {output_shp}")
    
    # 打印统计信息
    print("\n合并后的点数据统计:")
    print(f"总点数: {len(merged_points)}")
    print("各来源文件点数:")
    print(merged_points['source_file'].value_counts())
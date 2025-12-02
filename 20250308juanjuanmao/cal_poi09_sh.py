import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

def calculate_point_statistics():
    # 读取北京.csv点数据
    excel_path = r'e:\work\sv_kaixindian\20251124\上海.csv'
    df = pd.read_csv(excel_path)
    
    # 创建GeoDataFrame并转换坐标系
    geometry = [Point(xy) for xy in zip(df['lng'], df['lat'])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=32633)
    
    # 创建缓冲区域（500米半径）
    gdf_points['buffer_500m'] = gdf_points.geometry.buffer(500)
    
    # 读取第二个CSV文件（请替换为实际文件路径）
    second_csv_path = r'f:\大数据\poi_上海\上海市2024\CSV\上海市_商务住宅_anjuke_04.csv'  # 请修改为实际路径
    df_second = pd.read_csv(second_csv_path,encoding='gbk')
    
    # 创建第二个文件的GeoDataFrame
    geometry_second = [Point(xy) for xy in zip(df_second['lon_wgs84'], df_second['lat_wgs84'])]
    gdf_second = gpd.GeoDataFrame(df_second, geometry=geometry_second, crs="EPSG:4326").to_crs(epsg=32633)
    
    # 初始化结果列
    total_households_list = []
    avg_price_list = []
    
    # 对每个北京.csv的点进行计算
    for idx, row in gdf_points.iterrows():
        # 获取当前点的缓冲区域
        buffer_zone = row['buffer_500m']
        
        # 找出落在缓冲区域内的点
        points_in_buffer = gdf_second[gdf_second.geometry.within(buffer_zone)]
        
        # 计算总户数
        if '总户数' in points_in_buffer.columns:
            total_households = points_in_buffer['总户数'].sum()
        else:
            total_households = len(points_in_buffer)  # 如果没有总户数列，使用点数
        
        # 计算挂牌均价平均值
        if '挂牌均价' in points_in_buffer.columns and not points_in_buffer['挂牌均价'].empty:
            avg_price = points_in_buffer['挂牌均价'].mean()
        else:
            avg_price = np.nan
        
        total_households_list.append(total_households)
        avg_price_list.append(avg_price)
    
    # 将计算结果添加到原始DataFrame
    df['总户数'] = total_households_list
    df['平均房价'] = avg_price_list
    
    # 保存结果（可选：保存到新文件）
    output_path = r'e:\work\sv_kaixindian\20251124\上海2024_poi统计结果.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"处理完成！结果已保存到: {output_path}")
    print(f"原始数据行数: {len(df)}")
    print(f"新增列统计:")
    print(f"- 总户数范围: {df['总户数'].min()} ~ {df['总户数'].max()}")
    print(f"- 平均房价范围: {df['平均房价'].min():.2f} ~ {df['平均房价'].max():.2f}")
    
    return df

# 运行函数
if __name__ == "__main__":
    result_df = calculate_point_statistics()
    
    # 显示前几行结果
    print("\n结果预览:")
    print(result_df[['lng', 'lat', '总户数', '平均房价']].head())
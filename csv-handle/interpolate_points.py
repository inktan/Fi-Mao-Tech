import pandas as pd
import numpy as np
from geopy.distance import geodesic

def interpolate_points_between(start_lat, start_lon, end_lat, end_lon, distance_km=0.015):
    """在两经纬度点之间插入等间距的点"""
    start_point = (start_lat, start_lon)
    end_point = (end_lat, end_lon)
    
    # 计算总距离
    total_distance = geodesic(start_point, end_point).kilometers
    
    if total_distance <= distance_km:
        return []  # 如果距离小于等于15英里，不插入点
    
    # 计算需要插入的点数
    num_points = int(total_distance / distance_km) - 1
    
    # 线性插值
    interpolated_points = []
    for i in range(1, num_points + 1):
        fraction = i / (num_points + 1)
        lat = start_lat + (end_lat - start_lat) * fraction
        lon = start_lon + (end_lon - start_lon) * fraction
        interpolated_points.append((lat, lon))
    
    return interpolated_points

def main():
    # 读取数据
    df = pd.read_csv(r'e:\work\sv_shenyang\points.csv')
    
    # 确保有lon和lat列
    if 'lon' not in df.columns or 'lat' not in df.columns:
        raise ValueError("CSV文件必须包含'lon'和'lat'列")
    
    # 15英里转换为公里 (1 mile = 1.60934 km)
    distance_km = 0.015 * 1.60934
    
    new_rows = []
    
    # 遍历每一对相邻的点
    for i in range(len(df) - 1):
        # 添加当前点
        current_row = df.iloc[i].copy()
        new_rows.append(current_row)
        
        # 获取当前点和下一个点的经纬度
        start_lat, start_lon = df.iloc[i]['lat'], df.iloc[i]['lon']
        end_lat, end_lon = df.iloc[i+1]['lat'], df.iloc[i+1]['lon']
        
        # 插入中间点
        interpolated_points = interpolate_points_between(
            start_lat, start_lon, end_lat, end_lon, distance_km
        )
        
        # 添加插入的点
        for lat, lon in interpolated_points:
            new_row = df.iloc[i].copy()
            new_row['lat'] = lat
            new_row['lon'] = lon
            # 可以标记为插入的点（可选）
            new_row['is_interpolated'] = True
            new_rows.append(new_row)
    
    # 添加最后一个点
    new_rows.append(df.iloc[-1].copy())
    
    # 创建新的DataFrame
    new_df = pd.DataFrame(new_rows)
    
    # 保存为新的CSV文件
    new_df.to_csv(r'e:\work\sv_shenyang\points_with_interpolation.csv', index=False)
    print(f"原始数据点: {len(df)} 个")
    print(f"插值后数据点: {len(new_df)} 个")
    print("文件已保存为: points_with_interpolation.csv")

if __name__ == "__main__":
    main()
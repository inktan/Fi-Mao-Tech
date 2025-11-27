import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

# 定义POI类别和路径
poi_categories = {
    '商务住宅': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_商务住宅.shp',
    '生活服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_生活服务.shp',
    '室内设施': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_室内设施.shp',
    '体育休闲服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_体育休闲服务.shp',
    '医疗保健服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_医疗保健服务.shp',
    '政府机构及社会团体': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_政府机构及社会团体.shp',
    '住宿服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_住宿服务.shp',
    '餐饮服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_餐饮服务.shp',
    '道路附属设施': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_道路附属设施.shp',
    '地名地址信息': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_地名地址信息.shp',
    '风景名胜': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_风景名胜.shp',
    '公共设施': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_公共设施.shp',
    '公司企业': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_公司企业.shp',
    '购物服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_购物服务.shp',
    '交通设施服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_交通设施服务.shp',
    '金融保险服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_金融保险服务.shp',
    '科教文化服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_科教文化服务.shp',
    '摩托车服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_摩托车服务.shp',
    '汽车服务': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_汽车服务.shp',
    '汽车维修': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_汽车维修.shp',
    '汽车销售': r'f:\大数据\poi_深圳\深圳市2024\shp\深圳市_汽车销售.shp'
}

# 预先加载所有POI数据到内存
def load_poi_data():
    poi_data = {}
    for category, path in poi_categories.items():
        try:
            print(f"正在加载 {category} 数据...")
            poi_data[category] = gpd.read_file(path, encoding='gb18030').to_crs(epsg=32633)
            print(f"{category} 数据加载完成，共 {len(poi_data[category])} 条记录")
        except Exception as e:
            print(f"加载 {category} 数据时出错: {e}")
            poi_data[category] = None
    return poi_data

# 处理单个点的函数
def process_point(args):
    point, buffer_distance, poi_data = args
    point_geometry = point.geometry
    buffer = point_geometry.buffer(buffer_distance)
    
    result = {}
    for category, poi_gdf in poi_data.items():
        if poi_gdf is not None:
            try:
                count = poi_gdf[poi_gdf.geometry.within(buffer)].shape[0]
                result[f'{category}_count'] = count
            except:
                result[f'{category}_count'] = -1
        else:
            result[f'{category}_count'] = -1
    return result

def main():
    # 读取输入点数据
    excel_path = r'e:\work\sv_kaixindian\20251124\广深.csv'
    df = pd.read_csv(excel_path)
    
    # 创建GeoDataFrame并转换坐标系
    geometry = [Point(xy) for xy in zip(df['lng'], df['lat'])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=32633)
    
    # 预先加载所有POI数据
    poi_data = load_poi_data()
    
    # 准备多进程参数
    buffer_distance = 500  # 500米缓冲区
    points = [row for _, row in gdf_points.iterrows()]
    args_list = [(point, buffer_distance, poi_data) for point in points]
    
    # 使用多进程处理
    print(f"开始处理 {len(points)} 个点，使用 {cpu_count()} 个进程...")
    with Pool(processes=3) as pool:
        results = pool.map(process_point, args_list)
    
    # 将结果合并到原始DataFrame
    for category in poi_categories.keys():
        gdf_points[f'{category}_count'] = [result[f'{category}_count'] for result in results]
    
    # 保存结果
    output_csv = r'e:\work\sv_kaixindian\20250724\上海市2020_500m_poi统计.csv'
    gdf_points.drop(columns=['geometry']).to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"处理完成，结果已保存到: {output_csv}")

if __name__ == '__main__':
    main()
# -*- coding: utf-8 -*-
import json
import requests
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from coordinate_converter import transCoordinateSystem, transBmap
import time

# 全局配置
coordinate_point_category = 1  # 坐标转换类型
resolution_ratio = 4  # 街景图片分辨率 4=4096*2048
max_workers = 50  # 最大线程数
request_timeout = 15  # 请求超时时间(秒)
retry_times = 3  # 失败重试次数

class Panorama:
    """街景数据存储类"""
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

def get_panoid(lng, lat):
    """获取街景ID和元数据"""
    url = f'https://mapsv0.bdimg.com/?qt=qsdata&x={lng}&y={lat}'
    
    for attempt in range(retry_times):
        try:
            response = requests.get(url, timeout=request_timeout)
            response.raise_for_status()
            data = json.loads(response.text)
            
            if data and 'content' in data:
                content = data['content']
                panoid = content['id']
                detail_url = f'https://mapsv0.bdimg.com/?qt=sdata&sid={panoid}&pc=1'
                
                detail_resp = requests.get(detail_url, timeout=request_timeout)
                detail_data = json.loads(detail_resp.text)
                
                if detail_data and 'content' in detail_data:
                    return {
                        'timeLineIds': detail_data["content"][0]['TimeLine'],
                        'heading': detail_data["content"][0]['Heading'],
                        'moveDir': detail_data["content"][0]['MoveDir'],
                        'northDir': detail_data["content"][0]['NorthDir']
                    }
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(1)  # 失败后等待1秒再重试
    
    return None

def coord_convert(lng, lat):
    """坐标系统转换"""
    if coordinate_point_category == 1:
        result = transCoordinateSystem.wgs84_to_gcj02(lng, lat)
        result = transCoordinateSystem.gcj02_to_bd09(result[0], result[1])
        return transBmap.lnglattopoint(result[0], result[1])
    elif coordinate_point_category == 5:
        return transBmap.lnglattopoint(lng, lat)
    elif coordinate_point_category == 6:
        result = transCoordinateSystem.gcj02_to_bd09(lng, lat)
        return transBmap.lnglattopoint(result[0], result[1])

def process_single_point(index, row):
    """处理单个坐标点的线程任务"""
    try:
        lng, lat = float(row['longitude']), float(row['latitude'])
        tar_lng_lat = coord_convert(lng, lat)
        panoid_data = get_panoid(tar_lng_lat[0], tar_lng_lat[1])
        
        if not panoid_data:
            return []
        
        results = []
        for timeline in panoid_data['timeLineIds']:
            timeline_str = timeline['TimeLine']
            year = int(timeline_str[:4])
            month = int(timeline_str[4:6]) if len(timeline_str) >= 6 else 1
            
            # 筛选2015-2017年5-9月的数据（可根据需要修改）
            # if 2015 <= year <= 2017 and 5 <= month <= 9:
            results.append({
                'index': index,
                'longitude': lng,
                'latitude': lat,
                'pano_id': timeline['ID'],
                'year': year,
                'month': month,
                'heading': panoid_data['heading'],
                'north_dir': panoid_data['northDir']
            })
        
        return results
    except Exception as e:
        print(f"Error processing index {index}: {str(e)}")
        return []

def save_results(results, output_file):
    """保存结果到CSV文件"""
    if not results:
        return
    
    df = pd.DataFrame(results)
    
    # 如果文件不存在，写入header；否则追加
    if not os.path.exists(output_file):
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')

def main(csv_path, output_path):
    """主处理函数"""
    # 读取输入数据
    try:
        df = pd.read_csv(csv_path)
        print(f"成功加载数据: {len(df)}条记录")
    except Exception as e:
        print(f"读取CSV文件失败: {str(e)}")
        return
    
    # 准备结果存储
    if os.path.exists(output_path):
        os.remove(output_path)
    
    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        results_buffer = []
        buffer_size = 10000  # 每10000条结果保存一次
        
        # 提交任务
        for index, row in df.iterrows():
            futures.append(executor.submit(process_single_point, index, row))
        
        # 处理结果
        with tqdm(total=len(futures), desc="处理进度") as pbar:
            for future in as_completed(futures):
                try:
                    point_results = future.result()
                    if point_results:
                        results_buffer.extend(point_results)
                        
                        # 缓冲达到指定大小时保存
                        if len(results_buffer) >= buffer_size:
                            save_results(results_buffer, output_path)
                            results_buffer = []
                    
                    pbar.update(1)
                except Exception as e:
                    print(f"处理结果时出错: {str(e)}")
                    pbar.update(1)
        
        # 保存剩余结果
        if results_buffer:
            save_results(results_buffer, output_path)
    
    print(f"处理完成！结果已保存到: {output_path}")

if __name__ == '__main__':
    # 输入输出路径配置
    input_csv = r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial.csv'
    output_csv = input_csv.replace('.csv', '_multithread_results.csv')
    
    # 运行主程序
    start_time = time.time()
    main(input_csv, output_csv)
    print(f"总耗时: {time.time()-start_time:.2f}秒")
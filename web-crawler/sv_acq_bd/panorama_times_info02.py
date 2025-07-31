# -*- coding: utf-8 -*-
import json
import requests
import time
import os
from PIL import Image
import shutil
from coordinate_converter import transCoordinateSystem, transBmap
import csv
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool, cpu_count
import multiprocessing

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

def get_panoid(lng, lat):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    try:
        req = requests.get(url, timeout=10)
        data = json.loads(req.text)
        if (data is not None):
            result = data['content']
            panoid = result['id']
            url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
            r = requests.get(url, stream=True, timeout=10)
            data = json.loads(r.text)
            timeLineIds = data["content"][0]['TimeLine']
            Heading = data["content"][0]['Heading']
            MoveDir = data["content"][0]['MoveDir']
            NorthDir = data["content"][0]['NorthDir']
            return [timeLineIds, Heading, MoveDir, NorthDir]
        else:
            return []
    except Exception as e:
        print(f"Error in get_panoid: {e}")
        return []

def process_row(args):
    index, row, sv_infos_path = args
    lng = row['longitude']
    lat = row['latitude']
    
    try:
        tar_lng_lat = coord_convert(lng, lat)
        panoidInfos = get_panoid(tar_lng_lat[0], tar_lng_lat[1])
        if not panoidInfos:
            return None
            
        timeLineIds = panoidInfos[0]
        heading = panoidInfos[1]
        
        panoramas = []
        for timeLineId in timeLineIds:
            panoramas.append(Panorama(timeLineId, timeLineId['TimeLine'], int(timeLineId['TimeLine'][:4]), int(timeLineId['TimeLine'][4:])))
        
        filtered_panoramas = panoramas
        results = []
        for i in range(len(filtered_panoramas)):
            pano_id = filtered_panoramas[i].pano['ID']
            timeLine = filtered_panoramas[i].pano['TimeLine']
            year = filtered_panoramas[i].year
            month = filtered_panoramas[i].month
            results.append([index, float(row['longitude']), float(row['latitude']), pano_id, year, month])
        
        return results
    except Exception as e:
        print(f'error processing row {index}: {e}')
        return None

def batch_save_results(results_batch, sv_infos_path):
    """批量保存结果到CSV文件"""
    if not results_batch:
        return
        
    # 将所有结果展平
    flat_results = []
    for sublist in results_batch:
        if sublist:  # 确保sublist不是None
            flat_results.extend(sublist)
    
    if not flat_results:
        return
        
    # 使用pandas保存结果
    df_results = pd.DataFrame(flat_results, columns=['index', 'longitude', 'latitude', 'pano_id', 'year', 'month'])
    
    # 如果文件不存在，写入header，否则追加
    if not os.path.exists(sv_infos_path):
        df_results.to_csv(sv_infos_path, index=False)
    else:
        df_results.to_csv(sv_infos_path, mode='a', header=False, index=False)

def main():
    df = pd.read_csv(csv_path)
    print(f"Total rows to process: {df.shape[0]}")
    
    # 准备多进程参数
    num_cores = cpu_count()
    print(f"Using {num_cores} CPU cores")
    
    # 批量处理参数
    batch_size = 10000  # 每10000条结果保存一次
    results_batch = []
    
    # 创建进程池
    with Pool(processes=num_cores) as pool:
        # 准备任务参数
        tasks = [(index, row, None) for index, row in df.iterrows()]  # 不再传递sv_infos_path
        
        # 使用imap_unordered获取结果
        for i, result in enumerate(tqdm(pool.imap_unordered(process_row, tasks), total=len(tasks))):
            if result:
                results_batch.append(result)
                
                # 当积累的结果达到batch_size时，保存一次
                if len(results_batch) >= batch_size:
                    batch_save_results(results_batch, sv_infos_path)
                    results_batch = []  # 清空batch
        
        # 保存剩余的结果
        if results_batch:
            batch_save_results(results_batch, sv_infos_path)

coordinate_point_category = 1
# coordinate_point_category = 5
# coordinate_point_category = 6

def coord_convert(lng1, lat1):
    if coordinate_point_category == 1:
        result = transCoordinateSystem.wgs84_to_gcj02(lng1, lat1)
        result = transCoordinateSystem.gcj02_to_bd09(result[0], result[1])
        return transBmap.lnglattopoint(result[0], result[1])
    elif coordinate_point_category == 5:
        return transBmap.lnglattopoint(lng1, lat1)
    elif coordinate_point_category == 6:
        result = transCoordinateSystem.gcj02_to_bd09(lng1, lat1)
        return transBmap.lnglattopoint(result[0], result[1])

if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial.csv'  # 需要爬取的点
    sv_infos_path = csv_path.replace('.csv', '_infos01.csv')
    
    # 清空或创建结果文件
    if os.path.exists(sv_infos_path):
        os.remove(sv_infos_path)
    
    # 创建带有header的空文件
    pd.DataFrame(columns=['index', 'longitude', 'latitude', 'pano_id', 'year', 'month']).to_csv(sv_infos_path, index=False)
    
    main()
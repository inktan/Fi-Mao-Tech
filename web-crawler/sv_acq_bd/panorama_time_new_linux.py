
# -*- coding:utf-8 -*-
import math
import json
import requests
import os
from PIL import Image
from tqdm import tqdm
import pandas as pd
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
import functools

# 以下是根据百度地图JavaScript API破解得到 百度坐标<->墨卡托坐标 转换算法
array1 = [75, 60, 45, 30, 15, 0]
array3 = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0 ]
array2 = [[-0.0015702102444, 111320.7020616939, 1704480524535203, -10338987376042340, 26112667856603880, -35149669176653700, 26595700718403920, -10725012454188240, 1800819912950474, 82.5],
            [0.0008277824516172526, 111320.7020463578, 647795574.6671607, -4082003173.641316, 10774905663.51142, -15171875531.51559, 12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
            [0.00337398766765, 111320.7020202162, 4481351.045890365, -23393751.19931662, 79682215.47186455, -115964993.2797253, 97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
            [0.00220636496208, 111320.7020209128, 51751.86112841131, 3796837.749470245, 992013.7397791013, -1221952.21711287, 1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
            [-0.0003441963504368392, 111320.7020576856, 278.2353980772752, 2485758.690035394, 6070.750963243378, 54821.18345352118, 9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
            [-0.0003218135878613132, 111320.7020701615, 0.00369383431289, 823725.6402795718, 0.46104986909093, 2351.343141331292, 1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45]
        ]
array4 = [[1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331, 200.9824383106796, -187.2403703815547, 91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
            [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289, 96.32687599759846, -1.85204757529826, -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
            [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616, 59.74293618442277, 7.357984074871, -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
            [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744, 0.65659298677277, -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
            [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901, -0.00023663490511, -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
            [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032, -0.00000353937994, -0.02145144861037, -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5]
        ]

def Convertor(x, y, param):
    T = param[0] + param[1] * abs(x)
    cC = abs(y) / param[9]
    cF = param[2] + param[3] * cC + param[4] * cC * cC + param[5] * cC * cC * cC + param[6] * cC * cC * cC * cC + \
         param[7] * cC * cC * cC * cC * cC + param[8] * cC * cC * cC * cC * cC * cC
    T *= (-1 if x < 0 else 1)
    cF *= (-1 if y < 0 else 1)
    return T, cF

        
# 平面坐标转百度经纬度   
def pointtolnglat(pointx,pointy):
    arr = []
    for i in range(len(array3)):
        if abs(pointy) >= array3[i]:
            arr = array4[i]
            break
    res = Convertor(abs(pointx),abs(pointy), arr)
    return [round(res[0], 6), round(res[1], 6)]


# 百度经纬度转平面坐标
def lnglattopoint(lng,lat):
    arr = []
    lat = 74 if lat > 74 else lat
    lat = -74 if lat < -74 else lat

    for i in range(len(array1)):
        if lat >= array1[i]:
            arr = array2[i]
            break

    if not arr:
        for i in range(len(array1))[::-1]:
            if lat <= -array1[i]:
                arr = array2[i]
                break

    res = Convertor(lng, lat, arr)
    return [res[0], res[1]]

# 平面坐标（pointX, pointY）转瓦片    
def pointtotile(pointx,pointy,zoom=18):
    tilex = int(pointx * 2 ** (zoom - 18) / 256)
    tiley = int(pointy * 2 ** (zoom - 18) / 256)
    return [tilex, tiley]

# 平面坐标（pointX, pointY）转像素（pixelX, pixelY）  
def pointtopixel(pointx,pointy,zoom=18):
    pixelx = int(pointx * 2 ** (zoom - 18) - int(pointx * 2 ** (zoom - 18) / 256) * 256)
    pixely = int(pointy * 2 ** (zoom - 18) - int(pointy * 2 ** (zoom - 18) / 256) * 256)
    return [pixelx, pixely]

# 瓦片及像素瓦片转平面坐标（pointX, pointY）
def tile_pixel_to_point(tilex,tiley,pixelx,pixely,zoom=18):
    pointx = (tilex * 256 + pixelx) / (2 ** (zoom - 18))
    pointy = (tiley * 256 + pixely) / (2 ** (zoom - 18))
    return [pointx, pointy]

# 瓦片及像素瓦片转经纬度坐标
def tile_pixel_to_lnglat(tilex,tiley,pixelx,pixely,zoom=18):
    # pointx = (tilex * 256 + pixelx) / (2 ** (zoom - 18))
    # pointy = (tiley * 256 + pixely) / (2 ** (zoom - 18))
    pointx_pointy = tile_pixel_to_point(tilex,tiley,pixelx,pixely,zoom)
    return pointtolnglat(pointx_pointy[0],pointx_pointy[1])

# 经纬度坐标转瓦片   
def lnglattotile(lng,lat,zoom=18):
    pointx,pointy = lnglattopoint(lng,lat)
    return pointtotile(pointx,pointy,zoom)

# 经纬度坐标转像素（pixelX, pixelY）  
def lnglattopixel(lng,lat,zoom=18):
    pointx,pointy = lnglattopoint(lng,lat)
    return pointtopixel(pointx,pointy,zoom)

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]

def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)

def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

import requests
from PIL import Image
from io import BytesIO
import os

def download_and_merge_streetview(timeLineId, x_count, y_count, save_file_path):
    final_img = Image.new('RGB', (512 * y_count, 512 * x_count), (0, 0, 0))
    
    for x in range(x_count):
        for y in range(y_count):
            # 构造请求URL
            url = (
                'https://mapsv1.bdimg.com/?qt=pdata&sid=' + str(timeLineId) +
                '&pos=' + str(x) + '_' + str(y) +
                '&z=' + str(resolution_ratio) +
                '&udt=20200825&from=PC&auth=GPJbXPMId1MK3NC4B41Mzx7H0%3DNMQDQ%3DuxLEELLENBEtw805wi09v7uvYgP1PcGCgYvjPuVtvYgPMGvgWv%40uVtvYgPPxRYuVtvYgP%40vYZcvWPCuVtvYgP%40ZPcPPuVtvYgPhPPyheuVtvhgMuxVVty1uVtCGYuBtGIiyRWF%3D9Q9K%3DxXw1cv3uVtGccZcuVtPWv3Guxtdw8E62qvyIu9iTHf2PYIUvhgMZSguxzBEHLNRTVtcEWe1GD8zv7u%40ZPuVtc3CuVteuxtf0wd0vyMFFMMFOyAupt66FcErZZWux&seckey=mx8n3s4BT%2BM5jF6vP0bY6%2Bm25GJG9bJAPCy40WbYcVI%3D%2CLObtdXnaK4xy2ePuTyzwbSgjY0lwTkDw27LrZ2b6EqVnuWsCWY8KRbk0pLU3O7nH3Bxrl6QDIDwn3mcxqW8ivuJSq9AWKTb3QWqDwXO1CjnfVgGjLX42xPm511xNwk-n-XPUVVZWEHCymx0r0rAvOnY4vCwIwhNdEUnVTGHwmiRVJeaHB6B6bIKynrJcZMVy'
            )
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                final_img.paste(img, (y * 512, x * 512))  # 粘贴到最终图片
            else:
                print(f"Failed to download image at ({x}, {y}), status code: {response.status_code}")
    
    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
    final_img.save(save_file_path) 
    
#获取街景对应ID
def get_panoid(lng,lat):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = requests.get(url)
    data = json.loads(req.text)
    # print('data')
    # print(data)
    if (data is not None):
         result = data['content']
         # 提取所有历史街景ID
         panoid = result['id']
         url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
         r = requests.get(url,stream=True)
         data = json.loads(r.text)
         timeLineIds = data["content"][0]['TimeLine']
         Heading = data["content"][0]['Heading']
         MoveDir = data["content"][0]['MoveDir']
         NorthDir = data["content"][0]['NorthDir']

         return [timeLineIds,Heading,MoveDir, NorthDir]
    else:
        return []

#经纬度坐标转换
# 坐标点类别 1-5-6

def coord_convert(lng1,lat1):
    if coordinate_point_category == 1:
        result = wgs84_to_gcj02(lng1, lat1)
        result = gcj02_to_bd09(result[0],result[1])
        return lnglattopoint(result[0],result[1])
    elif coordinate_point_category == 5:
        return lnglattopoint(lng1,lat1)
    elif coordinate_point_category == 6:
        result = gcj02_to_bd09(lng1,lat1)
        return lnglattopoint(result[0],result[1])

# 假设这些是你自定义的函数和类，请确保已正确导入
# from your_module import coord_convert, get_panoid, Panorama, download_and_merge_streetview

def process_row(row, folder_out_path):
    """
    单个行数据的处理逻辑，封装成函数以便多进程调用
    """
    # 提取分辨率计算参数
    x_count = int(2 ** (resolution_ratio - 2))
    y_count = int(x_count * 2)
    
    index = row['index']
    # lng = row['lon']
    # lat = row['lat']
    lng = row['longitude']
    lat = row['latitude']

    try:
        # 坐标转换与获取 ID
        tar_lng_lat = coord_convert(lng, lat)
        panoidInfos = get_panoid(tar_lng_lat[0], tar_lng_lat[1])
        
        if not panoidInfos or len(panoidInfos[0]) == 0:
            return f"Index {index}: No panorama found."

        timeLineIds = panoidInfos[0]
        heading = panoidInfos[1]

        # 转换并筛选（这里直接取最新的一个，你可以根据需要改回循环）
        p = timeLineIds[0] 
        year = int(p['TimeLine'][:4])
        month = int(p['TimeLine'][4:])
        pano_id = p['ID']

        # 路径处理
        save_dir = os.path.join(folder_out_path, 'sv_pan01')
        os.makedirs(save_dir, exist_ok=True)
        
        save_file_path = os.path.join(save_dir, f"{index}_{lng}_{lat}_{heading}_{year}_{month}.jpg")

        if os.path.exists(save_file_path):
            return f"Index {index}: Already exists."

        # 执行下载
        download_and_merge_streetview(pano_id, x_count, y_count, save_file_path)
        return f"Index {index}: Downloaded."

    except Exception as e:
        return f"Index {index}: Error {e}"

def main(csv_path, folder_out_path, start_idx=10000, end_idx=13500, num_processes=5):
    # 1. 创建输出目录
    if not os.path.exists(folder_out_path):
        os.makedirs(folder_out_path)

    # 2. 读取 CSV 并根据 index 列筛选数据
    df = pd.read_csv(csv_path)
    print(df.shape, "起始索引:", start_idx, "结束索引:", end_idx)
    # 筛选指定范围的行
    mask = (df['index'] > start_idx) & (df['index'] <= end_idx)
    target_df = df[mask].copy()
    
    print(f"Total rows to process: {len(target_df)}")

    # for _, row in target_df.iterrows():
    #     process_row(row, resolution_ratio, folder_out_path)

    # 3. 使用多进程池
    # partial 用于固定不需要变动的参数 (resolution_ratio, folder_out_path)
    func = functools.partial(process_row, 
                             folder_out_path=folder_out_path)

    # 将 dataframe 转换为字典列表供多进程消费
    rows = [row for _, row in target_df.iterrows()]

    with Pool(processes=num_processes) as pool:
        # 使用 imap_unordered 配合 tqdm 显示进度条
        results = list(tqdm(pool.imap_unordered(func, rows), total=len(rows), desc="Downloading"))

    # 打印简要总结
    print("\nProcessing Complete.")

coordinate_point_category = 1
# coordinate_point_category = 5
# coordinate_point_category = 6
# 分辨率 "3 - 2048*1096   4 - 4096*2048"
resolution_ratio = 4

if __name__ == '__main__':
    CSV_PATH = r'/home/ubuntu/SV_acq/泉州市_50m_Spatial.csv'
    CSV_PATH = r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\泉州市\泉州市_50m_Spatial.csv'
    FOLDER_OUT_PATH = r'/home/ubuntu/SV_acq/sv_pan'
    
    # 在这里设置你想提取的范围和进程数
    start_idx=0
    end_idx=12000
    FOLDER_OUT_PATH = f'/home/ubuntu/SV_acq/sv_pan_{start_idx}_{end_idx}'
    num_processes=20
    main(CSV_PATH, FOLDER_OUT_PATH, start_idx=start_idx, end_idx=end_idx, num_processes=num_processes)

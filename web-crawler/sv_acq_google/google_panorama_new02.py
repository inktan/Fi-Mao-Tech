import csv
from tqdm import tqdm
import re
import requests
from requests.models import Response
import time
from PIL import Image
from dataclasses import dataclass
from typing import Generator, Tuple
from datetime import datetime
import itertools
from io import BytesIO
import threading  # 替换 signal 的核心模块
import pandas as pd
import os
import glob  # 新增：模糊匹配所需模块

# 设置代理环境变量（按需启用）
# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"
# os.environ["all_proxy"] = "socks5://127.0.0.1:7890"

# 定义超时异常类（保持不变）
class TimeoutException(Exception):
    pass

# -------------------------- 关键修改：Windows 兼容的超时装饰器 --------------------------
def timeout(seconds):
    """
    超时装饰器：用线程定时器实现函数超时控制（支持 Windows）
    :param seconds: 超时时间（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 定义超时触发函数
            def timeout_handler():
                raise TimeoutException(f"函数执行超时（超过 {seconds} 秒）")
            
            # 启动定时器：seconds 秒后触发超时
            timer = threading.Timer(seconds, timeout_handler)
            try:
                timer.start()  # 启动定时器
                result = func(*args, **kwargs)  # 执行目标函数
                return result
            finally:
                timer.cancel()  # 无论是否超时，都取消定时器（避免资源泄漏）
        return wrapper
    return decorator

# -------------------------- 原有数据类/工具函数（保持不变） --------------------------
@dataclass
class TileInfo:
    x: int
    y: int
    fileurl: str

@dataclass
class Tile:
    x: int
    y: int
    image: Image.Image


def get_width_and_height_from_zoom(zoom: int) -> Tuple[int, int]:
    return 2**zoom, 2 ** (zoom - 1)

def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    return (
        f'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}'
    )

def fetch_panorama_tile(tile_info: TileInfo) -> Image.Image:
    while True:
        try:
            response = requests.get(tile_info.fileurl, stream=True)
            break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)
    return Image.open(BytesIO(response.content))

def iter_tile_info(pano_id: str, zoom: int) -> Generator[TileInfo, None, None]:
    width, height = get_width_and_height_from_zoom(zoom)
    for x, y in itertools.product(range(width), range(height)):
        yield TileInfo(
            x=x,
            y=y,
            fileurl=make_download_url(pano_id=pano_id, zoom=zoom, x=x, y=y),
        )

def make_search_url(lat: float, lon: float) -> str:
    url = (
        "https://maps.googleapis.com/maps/api/js/"
        "GeoPhotoService.SingleImageSearch"
        "?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10"
        "!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4"
        "!1e8!1e6!5m1!1e2!6m1!1e2"
        "&callback=_xdc_._v2mub5"
    )
    return url.format(lat, lon)

def search_request(lat: float, lon: float) -> Response:
    url = make_search_url(lat, lon)
    while True:
        try:
            response = requests.get(url)
            break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)
    return response

def panoids_from_response(text, closest=False, disp=False, proxies=None):
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "pitch": float(p[3]),
        "heading": float(p[4]),
        "fov01": float(p[5]),
        "fov02": float(p[6]),
        } for p in pans]
    
    # 去重
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    # 提取日期
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # 剔除索引，保留年、月
    
    if len(dates) > 0:
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]
        
        if pans:
            # 最新日期对应第一个全景
            if dates:
                year, month = dates.pop(-1)
                pans[0].update({'year': year, "month": month})
            # 剩余日期倒序对应后续全景
            dates.reverse()
            for i, (year, month) in enumerate(dates):
                if i < len(pans) - 1:
                    pans[-1 - i].update({'year': year, "month": month})

    # 按日期降序排序（最新在前）
    def sort_key(x):
        if 'year' in x:
            return (-x['year'], -x['month'])
        else:
            return (float('inf'), float('inf'))  # 无日期的排最后
    pans.sort(key=sort_key)

    return pans[:len(dates)] if closest else pans

def iter_tiles(pano_id: str, zoom: int) -> Generator[Tile, None, None]:
    for info in iter_tile_info(pano_id, zoom):
        image = fetch_panorama_tile(info)
        yield Tile(x=info.x, y=info.y, image=image)

def get_panorama(pano_id: str, zoom: int = 1) -> Image.Image:
    tile_width = 512
    tile_height = 512
    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))
    
    for tile in iter_tiles(pano_id=pano_id, zoom=zoom):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile  # 释放内存
    return panorama

# -------------------------- 主函数（修改超时逻辑 + 补全 zoom 参数） --------------------------
def main(csv_path, output_, zoom):  # 补全 zoom 参数（原代码漏传）
    df = pd.read_csv(csv_path)
    print(f"CSV 数据总行数：{df.shape[0]}")
    
    # 确保 'index' 列存在（避免 KeyError）
    if 'index' not in df.columns:
        print("警告：CSV 中未找到 'index' 列，将自动添加行索引作为 'index'")
        df['index'] = df.index
    
    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        index = row['index']
        
        # 跳过不在 [start01+1, end] 范围内的行
        if index <= start01 or index > end:
            continue
        
        print(f"当前处理索引：{index}（总进度：{_+1}/{df.shape[0]}）")
        try:
            # 1. 请求全景数据
            resp = search_request(float(row['latitude']), float(row['longitude']))
            
            # 2. 超时解析全景 ID（使用 Windows 兼容的装饰器）
            @timeout(5)  # 5秒超时（可调整）
            def parse_panoids():
                return panoids_from_response(resp.text)
            
            try:
                panoids = parse_panoids()  # 执行带超时的解析
            except TimeoutException:
                print(f"解析超时（index: {index}），尝试用截断文本重试")
                # 超时后用前 30000 字符重试（避免文本过长导致解析卡住）
                @timeout(3)  # 重试时缩短超时时间
                def parse_truncated_panoids():
                    return panoids_from_response(resp.text[:30000])
                panoids = parse_truncated_panoids()
            
            if not panoids:
                print(f"index: {index} 未找到全景数据，跳过")
                continue
        
        except Exception as e:
            print(f"index: {index} 请求/解析失败：{str(e)}，跳过")
            continue
        
        # 3. 下载符合条件的全景图（2022年及以后）
        for pano in panoids:
            try:
                # 提取年/月（无数据时设为 0）
                year = int(pano.get('year', 0))
                month = int(pano.get('month', 0))
                
                # 过滤 2022 年之前的全景
                if year < 2022:
                    continue
                
                # 1. 构建模糊匹配规则（忽略 heading 部分）
                fixed_prefix = f"{int(index)}_{int(row['osm_id'])}_{row['longitude']}_{row['latitude']}_"
                fixed_suffix = f"_{year}_{month}.jpg"
                pattern = os.path.join(output_, f"{fixed_prefix}*{fixed_suffix}")
                
                # 2. 查找是否存在匹配的文件
                existing_files = glob.glob(pattern, recursive=False)
                if existing_files:
                    print(f"已存在同基础信息文件：{existing_files[0]}，跳过当前 heading={pano['heading']} 的下载")
                    continue
                
                # 3. 构建完整保存路径（无重复时才生成）
                img_save_path = os.path.join(output_, f"{fixed_prefix}{pano['heading']}{fixed_suffix}")
                
                # 4. 下载并保存（原逻辑不变）
                image = get_panorama(pano['panoid'], zoom)
                image.save(img_save_path)
                print(f"下载完成：{img_save_path}")
                break
            
            except Exception as e:
                print(f"index: {index} 下载全景失败：{str(e)}，继续尝试下一个全景")
                continue

# -------------------------- 执行配置（保持不变，注意路径格式） --------------------------
if __name__ == "__main__":
    # 输入 CSV 路径（Windows 路径用 r 前缀避免转义）
    points_csv = r'f:\work\work_fimo\svi_taiwan\台湾省_15m_Spatial.csv'
    
    # 全景分辨率：1(512*1024) → 5(4096*8192)，数值越大越清晰（但下载越慢）
    zoom = 3
    
    # 处理范围（index 列的区间）
    start = 710000
    start01 = 710000  # 跳过 index ≤ start01 的行
    end = 720000      # 跳过 index > end 的行
    
    # 输出文件夹（用 os.path.join 适配 Windows 路径）
    output_ = os.path.join(r'E:\svi_panorama', f'sv_pano_{start}_{end}')
    
    # 创建输出文件夹（不存在则创建）
    if not os.path.exists(output_):
        os.makedirs(output_)
        print(f"已创建输出文件夹：{output_}")
    
    # 执行主函数（补传 zoom 参数，原代码漏传导致报错）
    main(points_csv, output_, zoom)
import csv
from tqdm import tqdm
import requests
import re
import requests
from requests.models import Response
import time
import pandas as pd
from PIL import Image
from dataclasses import dataclass
from typing import Generator, Tuple
from datetime import datetime
import itertools
from io import BytesIO
from coord_convert.transform import gcj2wgs

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
    """
    Returns the width and height of a panorama at a given zoom level, depends on the
    zoom level.
    """
    return 2**zoom, 2 ** (zoom - 1)

def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    """
    Returns the URL to download a tile.
    """
    # return (
    #     "https://cbk0.google.com/cbk"
    #     f"?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    # )
    # url = f"https://cbk0.google.com/cbk?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    # url = f'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2'

    return (
        f'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}'
    )

def fetch_panorama_tile(tile_info: TileInfo) -> Image.Image:
    """
    Tries to download a tile, returns a PIL Image.
    """
    while True:
        try:
            response = requests.get(tile_info.fileurl, stream=True)
            break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

    return Image.open(BytesIO(response.content))


def iter_tile_info(pano_id: str, zoom: int) -> Generator[TileInfo, None, None]:
    """
    Generate a list of a panorama's tiles and their position.
    """
    width, height = get_width_and_height_from_zoom(zoom)
    for x, y in itertools.product(range(width), range(height)):
        yield TileInfo(
            x=x,
            y=y,
            fileurl=make_download_url(pano_id=pano_id, zoom=zoom, x=x, y=y),
        )
def make_search_url(lat: float, lon: float) -> str:
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = (
        "https://maps.googleapis.com/maps/api/js/"
        "GeoPhotoService.SingleImageSearch"
        "?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10"
        "!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4"
        "!1e8!1e6!5m1!1e2!6m1!1e2"
        "&callback=callbackfunc"
    )
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
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """

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
    """
    Gets panoids from response (gotting asynchronously)
    """

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    # print("Parsing response...")
    # print('length of text:',len(text))
    # print(text[0:200])
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]', text)
    # pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    # print('length of pans:',len(pans))
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "pitch": float(p[3]),
        "heading": float(p[4]),
        "fov01": float(p[5]),
        "fov02": float(p[6]),
        } for p in pans]  # Convert to floats

    # Remove duplicate panoramas
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
    def func(x):
        if 'year' in x:
            # 返回一个元组，year 取负值（实现降序），month 取负值（实现降序）
            return (-x['year'], -x['month'])
        else:
            # 没有 'year' 键的元素排在最后
            return (float('inf'), float('inf'))

    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def iter_tiles(pano_id: str, zoom: int) -> Generator[Tile, None, None]:
    for info in iter_tile_info(pano_id, zoom):
        image = fetch_panorama_tile(info)
        yield Tile(x=info.x, y=info.y, image=image)
def get_panorama(pano_id: str, zoom: int = 1) -> Image.Image:
    """
    Downloads a streetview panorama.
    """

    tile_width = 512
    tile_height = 512

    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))

    for tile in iter_tiles(pano_id=pano_id, zoom=zoom):
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    return panorama

def main(output_):

    _coords = [
        [33.24442144304853,-111.615594],

]
    # 转换为 WGS-84 坐标系
    # _coords = [gcj2wgs(lon,lat) for lat, lon in _coords]
    count = len(_coords)
    for index, row in tqdm(enumerate(_coords)):
        # if index <= -10:
        #     continue
        # if index >750000000:
        #     continue
        print(count, index)
        try:
            resp = search_request(float(row[0]), float(row[1]))
            panoids = panoids_from_response(resp.text)
            # print(panoids)
        except Exception as e:
            # print(e)
            continue
        if len(panoids)==0:
            continue
        for pano in panoids:
            try :
                year = int(pano['year'])
                month = int(pano['month'])
            except Exception as e :
                year = 0
                month = 0
            try :
                img_save_path = output_+f"/{int(index)}_{row[1]}_{row[0]}_{pano['heading']}_{year}_{month}.jpg"
                if os.path.exists(img_save_path):
                  break
                image = get_panorama(pano['panoid'],zoom)
                image.save(img_save_path)
                print("下载完成==>",img_save_path)
                break
            except Exception as e :
                print(f'error:{e}')
                continue
            
                img_save_path = output_+f"/{int(row('index'))}_{int(row['osm_id'])}_{row['longitude']}_{row['latitude']}_{int(pano['heading'])}_{year}_{month}.jpg"

import os

# 输入街景保存文件夹
# 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
# 全景分辨率设置 1-512*1024; 2-7++*1536; 3-1024*3072; 4-2048*4096; 5-4096*8192
zoom = 3
output_ = r'C:\Users\wang.tan.GOA\Pictures\金门/sv_pan_zoom'+str(zoom)

if os.path.exists(output_) == False:
    os.makedirs(output_)
# main(points_csv,output_,zoom)
main(output_)

# -*- coding: utf-8 -*-

import csv
import time
import json
import re
from typing import List, Optional

import requests
from pydantic import BaseModel
from requests.models import Response
import time
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  
import itertools
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Generator, Tuple

import requests
from PIL import Image


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
    # if zoom == 2:
    #     return 3,2
    # elif zoom == 3:
    #     return 6,3

def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    """
    Returns the URL to download a tile.
    """
    # return (
    #     "https://cbk0.google.com/cbk"
    #     f"?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    # )
    # return (
    #     f'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2'
    # )

    return (
        f'https://lh5.googleusercontent.com/p/{pano_id}=x{x}-y{y}-z{zoom}-k-no'
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

def extract_panoramas(text):
    """
    Given a valid response from the panoids endpoint, return a list of all the
    panoids.
    """
    pano_info = {"panoid":'',
                "year": 0,
                "month": 0,} 

    pattern = r"(\[\d+,\d+,\d+,\d+\])"
    match = re.search(pattern, text)
    if match:
        array_str = match.group(1)
        numbers_str = array_str[1:-1].split(',')
        numbers = [int(num) for num in numbers_str]
        pano_info['year'] = numbers[0]
        pano_info['month'] = numbers[1]


    pattern = r'\[\[\[\"([^\"]+)\"'
    match = re.search(pattern, text)
    if match:
        pano_info['panoid'] =  match.group(1)

    return pano_info

def make_search_url(lat: float, lon: float) -> str:
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = (
        "https://www.google.com/maps/rpc/photo/listentityphotos"
        "?authuser=0&hl=zh-CN&pb=!1e3!5m46!2m2!1i203!2i100!3m2!2i4!5b1!7m33!1m3!1e1!2b0"
        "!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3"
        "!1e9!2b1!3e2!2b1!8m2!1m1!1e2!9b0!11m1!4b1!6m3!1s3R5hZ6z9JOXl2roPgu2koQQ"
        "!7e81!15i11021!9m2!2d{0:}!3d{1:}!10d25"
    )

    # return url.format(lat, lon)
    return url.format(lon,lat)

class Panorama:
    def __init__(self, pano,heading, year_month, year, month):
        self.pano = pano
        self.heading = heading
        self.year_month = year_month
        self.year = year
        self.month = month

def GSVpanoMetadataCollector(input_csv,output_,zoom):
  
    df = pd.read_csv(input_csv)  
    all_points_count = df.shape[0]
    for index, row in tqdm(df.iterrows()):
        print(index,all_points_count)
        
        if index <= 6612:
            continue
        # if index >16000:
        #     continue
        
        id = row[0]
        lon = row[2]
        lat = row[1]
        # pano_id = row[3]
        
        time.sleep(0.05)
        try :
            resp = search_request(lat, lon)
            pano_info = extract_panoramas(resp.text)
            # print(pano_info)

            if pano_info['panoid'] == '':
                continue
            img_save_path = output_+f"/{int(id)}_{lon}_{lat}_{pano_info['year']}_{pano_info['month']}.png"
            if os.path.exists(img_save_path):
                continue
            # print(img_save_path)

            image = get_panorama(pano_info['panoid'],zoom)
            image.save(img_save_path)
                
            # break
                
        except Exception as e :
            print(f'error:{e}')
            continue
                
# ------------Main Function -------------------
# googlemap中点状区域的街景获取
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_yantu\points.csv'
    # 输入街景保存文件夹
        
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    # 全景分辨率设置 1-512*1024; 2-7++*1536; 3-1024*3072; 4-2048*4096; 5-4096*8192
    zoom = 3
    output_ =r'e:\work\sv_yantu\sv_pan_zoom'+str(zoom)

    if os.path.exists(output_) == False:
        os.makedirs(output_)    

    GSVpanoMetadataCollector(input_csv,output_,zoom)



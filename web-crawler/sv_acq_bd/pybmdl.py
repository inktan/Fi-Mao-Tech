import math
from coord_convert import transform

import os
import pandas as pd
from coordinate_converter import transCoordinateSystem, transBmap

import concurrent.futures
import math
import os
import random
import time
import urllib.request
from math import cos, sin

from PIL import Image
from tqdm import tqdm
import logging
import os
import sys
from typing import Literal
import pyproj
from geopy.distance import distance  # type: ignore

def latlon2px(zoom: int, lat: float, lon: float) -> tuple[int, int]:
    """Converts latitude and longitude to pixel coordinates.

    Arguments:
        zoom (int): Zoom level.
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        tuple: Tuple of pixel coordinates.
    """
    pointx,pointy = transBmap.lnglattopoint(lon,lat)
    x = int(pointx * 2 ** (zoom - 18))
    y = int(pointy * 2 ** (zoom - 18))

    return x, y

def latlon2xy(zoom: int, lat: float, lon: float) -> tuple[int, int, int, int]:
    """Converts latitude and longitude to tile coordinates.

    Arguments:
        zoom (int): Zoom level.
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        tuple: Tuple of tile coordinates.
    """
    x, y = latlon2px(zoom, lat, lon)

    remain_x = int(x % 256)
    remain_y = int(y % 256)

    x = int(x / 256)
    y = int(y / 256)

    return x, y, remain_x, remain_y

def calc(lat: float, lon: float, rotation: int, size: int) -> tuple[list[float], list[float]]:
    """Return the boundary of the image as a list of longitudes and latitudes.

    Arguments:
        lat (float): Latitude of the center of the image.
        lon (float): Longitude of the center of the image.
        rotation (int): Rotation of the image.
        size (int): Size of the image.

    Returns:
        tuple: Tuple of lists of longitudes and latitudes.
    """
    toprightlon, toprightlat, _ = pyproj.Geod(ellps="WGS84").fwd(lon, lat, 90 + rotation, size)
    bottomrightlon, bottomrightlat, _ = pyproj.Geod(ellps="WGS84").fwd(
        toprightlon, toprightlat, 180 + rotation, size
    )
    bottomleftlon, bottomleftlat, _ = pyproj.Geod(ellps="WGS84").fwd(
        bottomrightlon, bottomrightlat, 270 + rotation, size
    )

    lons = [lon, toprightlon, bottomrightlon, bottomleftlon]
    lats = [lat, toprightlat, bottomrightlat, bottomleftlat]

    return lats, lons

def top_left_from_center(
    center_lat: float, center_lon_float, size: int, rotation: int
) -> tuple[float, float]:
    """Calculate the top left corner of the image from the center coordinates.

    Arguments:
        center_lat (float): Latitude of the center of the image.
        center_lon_float (float): Longitude of the center of the image.
        size (int): Size of the image.
        rotation (int): Rotation of the image.

    Returns:
        tuple: Tuple of latitude and longitude of the top left corner.
    """
    step_distance = size // 2
    top = distance(meters=step_distance).destination((center_lat, center_lon_float), 0 + rotation)
    top_coordinates = (top.latitude, top.longitude)
    top_left = distance(meters=step_distance).destination(top_coordinates, -90 + rotation)
    return top_left.latitude, top_left.longitude

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 "
    "(KHTML, like Gecko) Version/5.0.5 Safari/533.21.1"
)
HEADERS = {"User-Agent": USER_AGENT}

SAT_URL = "https://maponline3.bdimg.com/starpic/?qt=satepc&u=x=%d;y=%d;z=%d;v=009;type=sate"
ROAD_URL = "https://maponline2.bdimg.com/tile/?qt=vtile&x=%d&y=%d&z=%d&styles=sl&showtext=0"

# https://maponline3.bdimg.com/starpic/?qt=satepc&u=x=104455;y=27476;z=19;v=009;type=sate&fm=46&app=webearth2&v=009&udt=20250529

TILES_DIRECTORY = os.path.join('E:', "temp", "tiles")
os.makedirs(TILES_DIRECTORY, exist_ok=True)

Image.MAX_IMAGE_PIXELS = None

def download_tile(
    x: int,
    y: int,
    zoom: int,
    pbar: tqdm,
) -> None:
    """Download an individual tile for a given x, y, and zoom level.

    Args:
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.
        zoom (int): Zoom level of the tile.
        pbar (tqdm): Progress bar object.
    """
    url = SAT_URL % (x, y, zoom)
    # print(url)
    tile_name = f"{zoom}_{x}_{y}_bs.png"

    tile_path = os.path.join(TILES_DIRECTORY, tile_name)

    if not os.path.exists(tile_path):
        try:
            req = urllib.request.Request(url, data=None, headers=HEADERS)
            response = urllib.request.urlopen(req)  # pylint: disable=R1732
            data = response.read()
        except Exception as e:
            raise RuntimeError(f"Error downloading {tile_path}: {e}")  # pylint: disable=W0707

        if data.startswith(b"<html>"):
            raise RuntimeError(f"Error downloading {tile_path}: Forbidden")

        with open(tile_path, "wb") as f:
            f.write(data)

        time.sleep(random.random())

    pbar.update(1)

# pylint: disable=R0913, R0917, R0914
def download_tiles(
    lat_start: float,
    lat_stop: float,
    lon_start: float,
    lon_stop: float,
    zoom: int,
    show_progress: bool = True,
) -> None:
    """Download tiles for a given boundary.

    Arguments:
        lat_start (float): Latitude of the top-left corner.
        lat_stop (float): Latitude of the bottom-right corner.
        lon_start (float): Longitude of the top-left corner.
        lon_stop (float): Longitude of the bottom-right corner.
        zoom (int): Zoom level.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.
    """
    # 获取瓦片编号
 
    start_x, start_y, _, _ = latlon2xy(zoom, lat_start, lon_start)
    stop_x, stop_y, _, _ = latlon2xy(zoom, lat_stop, lon_stop)

    number_of_tiles = (stop_y - start_y + 1) * (stop_x - start_x + 1)


    with tqdm(
        total=number_of_tiles, desc="Downloading tiles", unit="tiles", disable=show_progress
    ) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for x in range(start_x, stop_x + 1):
                for y in range(start_y, stop_y + 1):
                    executor.submit(download_tile, x, y, zoom, pbar)

    # with tqdm(
    #     total=number_of_tiles, desc="Downloading tiles", unit="tiles", disable=not show_progress
    # ) as pbar:
    #     for x in range(start_x, stop_x + 1):
    #         for y in range(start_y, stop_y + 1):
                # download_tile(x, y, zoom)
                # download_tile(x,y,zoom,pbar)

# pylint: disable=R0914, R0917, R0913
def merge_tiles(
    lat_start: float,
    lat_stop: float,
    lon_start: float,
    lon_stop: float,
    rotation: int,
    output: str,
    zoom: int,
    show_progress: bool = True,
):
    """Merge downloaded tiles into a single image.

    Arguments:
        lat_start (float): Latitude of the top-left corner.
        lat_stop (float): Latitude of the bottom-right corner.
        lon_start (float): Longitude of the top-left corner.
        lon_stop (float): Longitude of the bottom-right corner.
        rotation (int): Rotation of the image.
        output (str): Output path.
        zoom (int): Zoom level.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.
    """
    tile_type, ext = "bs", "png"

    x_start, y_start, remain_x_start, remain_y_start = latlon2xy(zoom, lat_start, lon_start)
    x_stop, y_stop, remain_x_stop, remain_y_stop = latlon2xy(zoom, lat_stop, lon_stop)

    w = (x_stop + 1 - x_start) * 256
    h = (y_stop + 1 - y_start) * 256

    result = Image.new("RGB", (w, h))

    number_of_tiles = (y_stop - y_start + 1) * (x_stop - x_start + 1)

    with tqdm(
        total=number_of_tiles, desc="Merging tiles", unit="tiles", disable=show_progress
    ) as pbar:
        for x in range(x_start, x_stop + 1):
            for y in range(y_start, y_stop + 1):
                tile_name = f"{zoom}_{x}_{y}_{tile_type}.{ext}"
                tile_path = os.path.join(TILES_DIRECTORY, tile_name)

                if not os.path.exists(tile_path):
                    continue

                x_paste = (x - x_start) * 256
                y_paste = (y_stop - y) * 256

                try:
                    image = Image.open(tile_path)
                except Exception as e:  # pylint: disable=W0718
                    try:
                        os.remove(tile_path)
                    except Exception:  # pylint: disable=W0718
                        pass
                    continue

                result.paste(image, (x_paste, y_paste))
                try:
                    os.remove(tile_path)
                except Exception:  # pylint: disable=W0718
                    pass
                continue

                pbar.update(1)

    cropped = result.crop(
        (remain_x_start, remain_y_start, w - (256 - remain_x_stop), h - (256 - remain_y_stop))
    )
    rotated = cropped.rotate(rotation, expand=False)
    new_width = 1 * cos(math.radians(abs(rotation))) + 1 * sin(math.radians(abs(rotation)))

    ratio = 1 / new_width

    box = (
        int((rotated.width - ratio * rotated.width) / 2),
        int((rotated.height - ratio * rotated.height) / 2),
        int(rotated.width - (rotated.width - ratio * rotated.width) / 2),
        int(rotated.height - (rotated.height - ratio * rotated.height) / 2),
    )

    cropped2 = rotated.crop(box)
    cropped2 = cropped2.resize(
        (int(min(cropped2.width, cropped2.height)), int(min(cropped2.width, cropped2.height)))
    )

    os.makedirs(os.path.dirname(output), exist_ok=True)
    cropped2.save(output)
    # result.save(output)

def save_image(
    lat: float,
    lon: float,
    size: int,
    output_path: str,
    rotation: int = 0,
    zoom: int = 18,
    from_center: bool = True,
    show_progress: bool = True,
) -> str:
    """Save an image from a given coordinates, size, and rotation.
    By default function expects that the input coordinates are the top-left corner of the image.
    If you need to provide the center of the image, set from_center to True.

    Arguments:
        lat (float): Latitude of the top-left corner.
        lon (float): Longitude of the top-left corner.
        size (int): Size of the image.
        output_path {str}: Output path.
        rotation (int, optional): Rotation of the image. Defaults to 0.
        zoom (int, optional): Zoom level. Defaults to 18.
        from_center (bool, optional): If set to True, function expects that the input coordinates
            are the center of the image. Defaults to False.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.

    Returns:
        str: Output path.
    """
    if from_center:
        # 基于中心点经纬度，获取左上角经纬度
        lat, lon = top_left_from_center(lat, lon, size, rotation)

    # 获取需要下载卫星图的四个角点的经纬度数据
    lats, lons = calc(lat, lon, rotation, size)

    download_tiles(
        min(lats),max(lats), min(lons), max(lons), zoom,show_progress
    )

    merge_tiles(
        min(lats),
        max(lats),
        min(lons),
        max(lons),
        rotation,
        output_path,
        zoom,
        show_progress=show_progress,
    )
    return output_path

if __name__ == '__main__':

    # zoom = 15 # 256*256的瓦片尺寸为1760*1760m     每个像素点为6.88m
    # zoom = 16 # 256*256的瓦片尺寸为880*880m       每个像素点为3.44m
    # zoom = 17 # 256*256的瓦片尺寸为440*440m       每个像素点为1.72m
    # zoom = 18 # 256*256的瓦片尺寸为220*220m       每个像素点为0.86m
    zoom = 19 # 256*256的瓦片尺寸为110*110m         每个像素点为0.43m
    # zoom = 20 # 无卫星图

    rotation = 0
    # size = 200
    size = 5000
    from_center = True
    show_progress = True
    
    number_of_tiles = 1
    # for zoom in [22,,,20,18,16]:
    for zoom in [19]:
        # 杭州天目里
        lon = 120.0946157506
        lat = 30.2688266736

        lon = 118.05929726762608
        lat = 24.455599238321398
        # 从google map量去的坐标为gcj-2，需要转为wgs84
        coords = [
        (lon,lat),
        ]
        # 将 GCJ-02 坐标转换为 WGS84 坐标
        wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]
        # wgs84转为bd09
        lon,lat = transform.wgs2bd(lon,lat)

        # lon=wgs_coords[0][0]
        # lat=wgs_coords[0][1]

        output_path = f"E:\\temp\\sate_img\\{coords[0][0]}_{coords[0][1]}_{size}m_{zoom}_satellite_image.jpg"
        save_image(lat,lon,size,output_path,rotation,zoom,from_center,show_progress)

    # 上海外滩
    lon = 121.5034659206
    lat = 31.2462386675    

    # for zoom in [15,16,17,18,19,20]:
    #     tile_index = transBmap.lnglattotile(lon,lat,zoom)
    #     x = tile_index[0]
    #     y = tile_index[1]

    #     with tqdm(total=number_of_tiles, desc="Merging tiles", unit="tiles", disable=not show_progress) as pbar:
    #         download_tile(x,y,zoom,pbar)






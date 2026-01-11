"""This module contains functions to download and merge tiles from Google Maps."""

import concurrent.futures
import math
import os
from math import cos, sin

import requests
from PIL import Image
from requests import Session
from tqdm import tqdm

from pygmdl.config import HEADERS, SAT_URL, TILES_DIRECTORY, Logger
from pygmdl.converter import calc, top_left_from_center
from pygmdl.gmapper import latlon2xy

Image.MAX_IMAGE_PIXELS = None
cpu_count = os.cpu_count()
MAX_WORKERS = min(cpu_count * 4, 64) if cpu_count else 4


# pylint: disable=R0913, R0917, R1710
def download_tile(
    x: int,
    y: int,
    zoom: int,
    logger: Logger,
    pbar: tqdm,
    session: Session | None = None,
    tiles_dir: str = TILES_DIRECTORY,
    retries: int = 5,
) -> None:
    """Download an individual tile for a given x, y, and zoom level.

    Args:
        x (int): X coordinate of the tile.
        y (int): Y coordinate of the tile.
        zoom (int): Zoom level of the tile.
        logger (Logger): Logger object.
        pbar (tqdm): Progress bar object.
        session (Session, optional): Requests session object. Defaults to None.
        tiles_dir (str, optional): Directory to save downloaded tiles. Defaults to TILES_DIRECTORY.
        retries (int, optional): Number of retries for downloading the tile. Defaults to 5.
    """
    url = SAT_URL % (x, y, zoom)
    tile_name = f"{zoom}_{x}_{y}_s.png"

    tile_path = os.path.join(tiles_dir, tile_name)

    if not os.path.exists(tile_path):
        try:
            if session is None:
                session = requests.Session()

            response = session.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.content
        except Exception as e:
            if retries > 0:
                logger.warning(
                    f"Can not download tile {tile_name}. Error: {repr(e)}. {retries} retries left."
                )
                return download_tile(
                    x, y, zoom, logger, pbar, session, tiles_dir=tiles_dir, retries=retries - 1
                )
            logger.error(f"Error downloading {tile_path}: {e}")
            raise RuntimeError(f"Error downloading {tile_path}") from e

        if data.startswith(b"<html>"):
            logger.error(f"Error downloading {tile_path}: Forbidden")
            raise RuntimeError(f"Error downloading {tile_path}: Forbidden")

        with open(tile_path, "wb") as f:
            f.write(data)

    pbar.update(1)


# pylint: disable=R0913, R0917, R0914
def download_tiles(
    lat_start: float,
    lat_stop: float,
    lon_start: float,
    lon_stop: float,
    zoom: int,
    logger: Logger,
    show_progress: bool = True,
    tiles_dir: str = TILES_DIRECTORY,
) -> None:
    """Download tiles for a given boundary.

    Arguments:
        lat_start (float): Latitude of the top-left corner.
        lat_stop (float): Latitude of the bottom-right corner.
        lon_start (float): Longitude of the top-left corner.
        lon_stop (float): Longitude of the bottom-right corner.
        zoom (int): Zoom level.
        logger (Logger): Logger object.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.
        tiles_dir (str, optional): Directory to save downloaded tiles. Defaults to TILES_DIRECTORY.
    """
    start_x, start_y, _, _ = latlon2xy(zoom, lat_start, lon_start)
    stop_x, stop_y, _, _ = latlon2xy(zoom, lat_stop, lon_stop)
    number_of_tiles = (stop_y - start_y + 1) * (stop_x - start_x + 1)

    logger.debug("Starting to download %s tiles...", number_of_tiles)

    with tqdm(
        total=number_of_tiles, desc="Downloading tiles", unit="tiles", disable=not show_progress
    ) as pbar:
        with requests.Session() as session:
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for x in range(start_x, stop_x + 1):
                    for y in range(start_y, stop_y + 1):
                        executor.submit(
                            download_tile, x, y, zoom, logger, pbar, session, tiles_dir=tiles_dir
                        )


# pylint: disable=R0914, R0917, R0913
def merge_tiles(
    lat_start: float,
    lat_stop: float,
    lon_start: float,
    lon_stop: float,
    rotation: int,
    output: str,
    zoom: int,
    logger: Logger,
    show_progress: bool = True,
    tiles_dir: str = TILES_DIRECTORY,
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
        logger (Logger): Logger object.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.
        tiles_dir (str, optional): Directory to save downloaded tiles. Defaults to TILES_DIRECTORY.
    """
    tile_type, ext = "s", "png"

    x_start, y_start, remain_x_start, remain_y_start = latlon2xy(zoom, lat_start, lon_start)
    x_stop, y_stop, remain_x_stop, remain_y_stop = latlon2xy(zoom, lat_stop, lon_stop)

    w = (x_stop + 1 - x_start) * 256
    h = (y_stop + 1 - y_start) * 256

    result = Image.new("RGB", (w, h))

    number_of_tiles = (y_stop - y_start + 1) * (x_stop - x_start + 1)

    with tqdm(
        total=number_of_tiles, desc="Merging tiles", unit="tiles", disable=not show_progress
    ) as pbar:
        for x in range(x_start, x_stop + 1):
            for y in range(y_start, y_stop + 1):
                tile_name = f"{zoom}_{x}_{y}_{tile_type}.{ext}"
                tile_path = os.path.join(tiles_dir, tile_name)

                if not os.path.exists(tile_path):
                    logger.warning(f"Tile {tile_path} not found, skipping...")
                    continue

                x_paste = (x - x_start) * 256
                y_paste = h - (y_stop + 1 - y) * 256

                try:
                    image = Image.open(tile_path)
                except Exception as e:  # pylint: disable=W0718
                    logger.error(f"Error opening {tile_path}: {e}")
                    try:
                        os.remove(tile_path)
                    except Exception:  # pylint: disable=W0718
                        pass
                    continue

                result.paste(image, (x_paste, y_paste))

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

    logger.debug("Shape of the image: %s", cropped2.size)

    cropped2.save(output)
    logger.debug("Saved image as %s", output)


def save_image(
    lat: float,
    lon: float,
    size: int,
    output_path: str,
    rotation: int = 0,
    zoom: int = 18,
    from_center: bool = False,
    logger: Logger | None = None,
    show_progress: bool = True,
    tiles_dir: str = TILES_DIRECTORY,
) -> str:
    """Save an image from a given coordinates, size, and rotation.
    By default function expects that the input coordinates are the top-left corner of the image.
    If you need to provide the center of the image, set from_center to True.
    Rotation value is in degrees, minimum value is -90 and maximum value is 90. If the angle
    does not fit into this range, an error will be raised.

    Arguments:
        lat (float): Latitude of the top-left corner.
        lon (float): Longitude of the top-left corner.
        size (int): Size of the image.
        output_path {str}: Output path.
        rotation (int, optional): Rotation of the image. Defaults to 0.
        zoom (int, optional): Zoom level. Defaults to 18.
        from_center (bool, optional): If set to True, function expects that the input coordinates
            are the center of the image. Defaults to False.
        logger (Logger, optional): Logger object.
        show_progress (bool, optional): If set to True, progress bars will be shown. Defaults
            to True.
        tiles_dir (str, optional): Directory to save downloaded tiles. Defaults to TILES_DIRECTORY.

    Raises:
        ValueError: If rotation is not between -90 and 90 degrees.

    Returns:
        str: Output path.
    """
    if not -90 <= rotation <= 90:
        raise ValueError(
            "Satellite image download failed: the rotation must be between -90 and 90 degrees, "
            f"got {rotation} degrees."
        )

    if logger is None:
        logger = Logger()

    if from_center:
        lat, lon = top_left_from_center(lat, lon, size, rotation)

    lats, lons = calc(lat, lon, rotation, size)
    logger.debug("Boundary coordinates: %s %s", lats, lons)

    os.makedirs(tiles_dir, exist_ok=True)

    download_tiles(
        max(lats),
        min(lats),
        min(lons),
        max(lons),
        zoom,
        logger,
        show_progress=show_progress,
        tiles_dir=tiles_dir,
    )
    logger.debug("Satellite tiles downloaded, starting to merge...")

    merge_tiles(
        max(lats),
        min(lats),
        min(lons),
        max(lons),
        rotation,
        output_path,
        zoom,
        logger,
        show_progress=show_progress,
        tiles_dir=tiles_dir,
    )
    logger.debug("Image merged successfully to %s", output_path)
    return output_path

import os
import pandas as pd
from tqdm import tqdm
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('satellite_image_download.log'),
        logging.StreamHandler()
    ]
)

def download_satellite_images(csv_file, output_base_dir, zoom_levels, sizes, img_format='.jpg'):
    """
    批量下载卫星图像
    
    参数:
    csv_file: CSV文件路径，包含lon和lat列
    output_base_dir: 输出目录
    zoom_levels: 缩放级别列表
    sizes: 尺寸列表（单位：米）
    img_format: 图像格式
    """
    
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_file)
        required_columns = ['lon', 'lat']
        
        # 检查必要的列
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV文件必须包含'{col}'列")
        
        logging.info(f"成功读取CSV文件，共{len(df)}行数据")
        
    except Exception as e:
        logging.error(f"读取CSV文件失败: {e}")
        return
    
    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)
    
    # 处理进度统计
    total_tasks = len(df) * len(zoom_levels) * len(sizes)
    processed = 0
    successful = 0
    failed = 0
    
    # 处理每个坐标点
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="处理坐标点"):
        lon = row['lon']
        lat = row['lat']
        
        # 为每个坐标创建子目录
        # coord_dir = os.path.join(output_base_dir, f"coord_{idx+1}_{lon:.6f}_{lat:.6f}")
        coord_dir = os.path.join(output_base_dir)
        os.makedirs(coord_dir, exist_ok=True)
        
        # 对每个缩放级别和尺寸组合
        for zoom in zoom_levels:
            for size in sizes:
                processed += 1
                
                # 生成输出文件名
                output_filename = f"_{idx+1}_{lon:.6f}_{lat:.6f}_{size}m_zoom{zoom}{img_format}"
                output_path = os.path.join(coord_dir, output_filename)
                
                # 检查文件是否已存在
                if os.path.exists(output_path):
                    logging.info(f"文件已存在，跳过: {output_path}")
                    successful += 1
                    continue
                
                try:
                    # 下载卫星图像
                    logging.info(f"正在下载: 坐标({lon:.6f}, {lat:.6f}), zoom={zoom}, size={size}m")
                    
                    save_image(lat, lon, size, output_path, 0, zoom, True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        successful += 1
                        logging.info(f"下载成功: {output_path}")
                    else:
                        failed += 1
                        logging.warning(f"下载的文件可能为空: {output_path}")
                        
                except Exception as e:
                    failed += 1
                    logging.error(f"下载失败 - 坐标({lon:.6f}, {lat:.6f}), zoom={zoom}, size={size}m: {e}")
        
def main():
    # 配置文件路径
    csv_file = "coordinates.csv"  # CSV文件路径，包含lon和lat列
    # 输出目录
    output_base_dir = "E:\\temp\\sate_img_batch"
    
    # zoom = 15 # 256*256的瓦片尺寸为1760*1760m     每个像素点为6.88m
    # zoom = 16 # 256*256的瓦片尺寸为880*880m       每个像素点为3.44m
    # zoom = 17 # 256*256的瓦片尺寸为440*440m       每个像素点为1.72m
    # zoom = 18 # 256*256的瓦片尺寸为220*220m       每个像素点为0.86m
    # zoom = 19 # 256*256的瓦片尺寸为110*110m         每个像素点为0.43m
    # zoom = 20 # 无卫星图

    # 下载参数配置
    zoom_levels = [19]  # 可以同时设置多个缩放级别
    sizes = [1000]  # 可以同时设置多个尺寸
    
    # 图像格式
    img_format = '.png'  # 或 '.jpg'
    
    # 开始批量下载
    download_satellite_images(csv_file, output_base_dir, zoom_levels, sizes, img_format)

if __name__ == '__main__':
    main()

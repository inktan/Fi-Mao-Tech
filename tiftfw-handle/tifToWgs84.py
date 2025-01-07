tif_path = r'f:\立方数据\2000-2023年全国1km分辨率的逐年PM2.5栅格数据\全国范围的数据\tif格式的数据\数据\2023.tif'

import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
from tqdm import tqdm

# 打开 TIFF 文件
with rasterio.open(tif_path) as src:
    # 获取栅格的变换信息
    transform = src.transform
    # 获取栅格的宽度和高度
    width = src.width
    height = src.height

    # 获取nodata值，如果没有定义则为None
    nodata = src.nodata
    # 读取第一个波段的数据
    band_data = src.read(1)
    
    # 如果有nodata值，将nodata值替换为numpy的NaN
    if nodata is not None:
        band_data = band_data.astype('float')
        band_data[band_data == nodata] = 0

    # 创建一个转换器，将栅格坐标转换为 WGS84
    dst_crs = 'EPSG:4326'
    transformer = Transformer.from_crs(src.crs, dst_crs, always_xy=True)

    # 存储所有点的列表
    points = []
    gdp_values = []

    # 遍历每个栅格点
    for row in tqdm(range(height)):
        for col in range(width):
            # 计算栅格点的坐标
            x, y = rasterio.transform.xy(transform, row, col)
            # 转换为 WGS84 坐标
            lon, lat = transformer.transform(x, y)
            # 将点添加到列表中
            gdp_value = band_data[row, col]

            if lon<120.452072634024 or lon>122.672925778185:
                continue
            if lat<30.4104083185987 or lat>32.1352190219701:
                continue
            print(lon, lat,gdp_value)
            gdp_values.append(gdp_value)
            points.append(Point(lon, lat))

    # 创建 GeoDataFrame
    gdf = gpd.GeoDataFrame({'geometry':points, 'gdp_value':gdp_values}, crs=dst_crs)

    # 保存为 Shapefile
    gdf.to_file(tif_path.replace('.tif','_.shp'))

    # 创建 DataFrame 并保存为 CSV
    df = pd.DataFrame({'gdp_value': gdp_values,
                        'longitude': [point.x for point in points],
                    'latitude': [point.y for point in points]})

    df.to_csv(tif_path.replace('.tif','_.csv'), index=False)



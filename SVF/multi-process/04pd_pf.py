import matplotlib.pyplot as plt
from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta
import pytz
import pandas as pd
import math
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split, polygonize, unary_union
from tqdm import tqdm
import geopandas as gpd
from shapely.affinity import scale
import os, csv
import warnings
from multiprocessing import Pool, cpu_count
from functools import partial

warnings.filterwarnings("ignore")  # 忽略所有警告

def read_shp_ss(shp_path):
    gdf_ss = gpd.read_file(shp_path)
    center = gdf_ss.geometry.centroid.union_all().centroid
    center_coords = (center.x, center.y)  # 获取中心点的坐标
    gdf_ss['geometry'] = gdf_ss.geometry.translate(-center_coords[0], -center_coords[1])
    bounds = gdf_ss.total_bounds
    original_width = bounds[2] - bounds[0]  # maxx - minx
    original_height = bounds[3] - bounds[1]  # maxy - miny
    max_dimension = max(original_width, original_height)
    scale_factor = 180 / max_dimension # 极坐标系的长短为-90 90，因此这里总长度为180
    gdf_ss['geometry'] = gdf_ss.geometry.scale(scale_factor, scale_factor, origin=(0,0))
    if 'value' not in gdf_ss.columns:
        raise ValueError("SHP文件中不存在 'value' 字段")
    gdf_ss = gdf_ss[gdf_ss['value'] != 0]
    gdf_ss.set_crs("EPSG:4326", inplace=True)
    return gdf_ss

def cal_pd(gdf_ss,longitude,latitude,year,month,tar_timezone = 'Europe/London'):
    origin = Point(0, 0)
    length = 100
    angles = np.arange(0, 360, 45)  # [0, 45, 90, 135, 180, 225, 270, 315]
    radii = [30, 60, 90]
    gdf_edge = gpd.GeoDataFrame(columns=["type", "geometry"], crs="EPSG:4326")
    for angle in angles:
        radians = np.deg2rad(angle)
        end_x = origin.x + length * np.cos(radians)
        end_y = origin.y + length * np.sin(radians)
        end_point = Point(end_x, end_y)
        line = LineString([origin, end_point])
        gdf_edge.loc[len(gdf_edge)] = {"type": f"line_{angle}", "geometry": line}
    for radius in radii:
        angles_circle = np.linspace(0, 2 * np.pi, 100)  # 将圆分为 100 个点
        circle_points = [Point(origin.x + radius * np.cos(angle), origin.y + radius * np.sin(angle)) for angle in angles_circle]
        circle_boundary = LineString(circle_points)
        gdf_edge.loc[len(gdf_edge)] = {"type": f"circle_r{radius}", "geometry": circle_boundary}
    gdf_edge.set_crs("EPSG:4326", inplace=True)
    timezone = pytz.timezone(tar_timezone)
    date = datetime(year,month, 1, tzinfo=timezone)
    data = []
    for hour in range(24):  # 0 到 23 小时
        for minute in range(0, 60, 6):  # 每 15 分钟计算一次
            current_time = date + timedelta(hours=hour, minutes=minute)
            altitude = get_altitude(latitude, longitude, current_time)
            azimuth = get_azimuth(latitude, longitude, current_time)
            data.append([hour, minute, altitude, azimuth])
    df_solar = pd.DataFrame(data, columns=['Hour', 'Minute', 'Altitude', 'Azimuth'])
    df_solar = df_solar[df_solar['Altitude']>0]
    df_solar.reset_index(drop=True, inplace=True)
    df_solar['Altitude_r'] = df_solar['Altitude'].apply(math.radians)
    df_solar['Azimuth_r'] = df_solar['Azimuth'].apply(math.radians)
    def convert_xy(df):
        altitude = df['Altitude']
        azimuth = df['Azimuth']
        if azimuth < 90:
            azimuth = 90- azimuth
            vx = np.cos((azimuth/360)*2*np.pi)*(90-altitude)
            vy = np.sin((azimuth/360)*2*np.pi)*(90-altitude)
        elif 90 <= azimuth < 180:
            azimuth = azimuth-90
            vx = np.cos((azimuth/360)*2*np.pi)*(90-altitude)
            vy = -np.sin((azimuth/360)*2*np.pi)*(90-altitude)
        elif 180 <= azimuth < 270:
            azimuth = azimuth-180
            vx = -np.sin((azimuth/360)*2*np.pi)*(90-altitude)
            vy = -np.cos((azimuth/360)*2*np.pi)*(90-altitude)
        else:
            azimuth = azimuth-270
            vx = -np.cos((azimuth/360)*2*np.pi)*(90-altitude)
            vy = np.sin((azimuth/360)*2*np.pi)*(90-altitude)
        return vx, vy
    df_solar['xy'] = df_solar[['Altitude','Azimuth']].apply(convert_xy,axis=1)
    df_solar['cos_altitude_r']= df_solar['Altitude_r'].apply(lambda x:np.cos(x))
    df_solar['x'] = df_solar['xy'].apply(lambda xy: xy[0])  # 提取 x 坐标
    df_solar['y'] = df_solar['xy'].apply(lambda xy: xy[1])  # 提取 y 坐标
    dst_crs = 'EPSG:4326'
    gdf_solar = gpd.GeoDataFrame(df_solar, geometry=gpd.points_from_xy(df_solar.x, df_solar.y), crs=dst_crs)
    gdf_solar.set_crs("EPSG:4326", inplace=True)
    gdf_solar_in_ss = gpd.sjoin(gdf_solar, gdf_ss, predicate='within')
    PD = sum(gdf_solar_in_ss['cos_altitude_r'])/ sum(df_solar['cos_altitude_r'])
    return PD

def cal_pf(gdf_ss):
    gdf_ss['value'] = 1
    gdf_ss = gdf_ss.dissolve(by='value')

    gdf_ss.set_crs("EPSG:4326", inplace=True)
    origin = Point(0, 0)
    lstx = [i * 90/8 for i in range(1, 9)]  # [11.25, 22.5, ..., 90.0]
    center = Point(0, 0)  # 圆心坐标 (0, 0)
    gdf_edge = gpd.GeoDataFrame(columns=["type", "geometry"], crs="EPSG:4326")
    circles = []
    for radius in lstx:
        circle = center.buffer(radius)
        exterior_coords = list(circle.exterior.coords)
        circle_boundary = LineString(exterior_coords)
        gdf_edge.loc[len(gdf_edge)] = {"type": f"circle_r{radius}", "geometry": circle_boundary}
    angle_interval = 360/16.0
    angles = [angle_interval*i for i in range(0, 16)]  # [11.25, 22.5, ..., 90.0]
    length = 95
    for angle in angles:
        radians = np.deg2rad(angle)
        end_x = origin.x + length * np.cos(radians)
        end_y = origin.y + length * np.sin(radians)
        end_point = Point(end_x, end_y)
        line = LineString([origin, end_point])
        gdf_edge.loc[len(gdf_edge)] = {"type": f"line_{angle}", "geometry": line}
    combined_geoms = unary_union(gdf_edge.geometry)
    polygons = list(polygonize(combined_geoms))
    gdf_polygons = gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")
    gdf_polygons["area"] = gdf_polygons.to_crs("EPSG:32650").geometry.area  # 计算面积
    gdf_polygons["id"] = range(len(gdf_polygons))      # 添加ID
    dfy= gpd.overlay(gdf_ss,gdf_polygons,how='identity')
    projected_crs = "EPSG:4326"  # 请根据实际位置调整
    dfy = dfy.to_crs(projected_crs)
    dfy["area2"] = dfy.to_crs("EPSG:32650").geometry.area  # 计算面积

    dfy['inner_zenith']= dfy['geometry'].apply(lambda x:90 - Point(0,0).distance(x))
    dfy['outer_zenith']= dfy['geometry'].apply(lambda x:90 - Point(0,0).hausdorff_distance(x))
    dfy['centroid_zenith'] = dfy['geometry'].apply(lambda x:90 - Point(0,0).distance(x.centroid))
    dfy = dfy[dfy['inner_zenith'] >= 0]
    dfy = dfy[dfy['outer_zenith'] >= 0]
    dfy = dfy[dfy['centroid_zenith'] >= 0]

    def get_pf(x):
        gaz = x['area2'] / x['area']
        theta2 = (x['outer_zenith']/360) * 2 * np.pi
        theta1 = (x['inner_zenith']/360) * 2 * np.pi
        thetaz = (x['centroid_zenith']/360) * 2 * np.pi
        cos_theta2_1 = np.cos(theta2) - np.cos(theta1)
        cos_thetaz = np.cos(thetaz)
        return gaz*cos_theta2_1*cos_thetaz

    dfy['vl']= dfy.apply(get_pf,axis=1)

    pf = np.nansum(dfy['vl'])/16
    return pf

def process_shp_file(shp_path, output_csv):
    try:
        infos = os.path.basename(shp_path).split('_')
        longitude = float(infos[1])
        latitude = float(infos[2])
        year = int(infos[-1].split('.')[0][0:4])
        month = int(infos[-1].split('.')[0][-2:])
        
        gdf_ss = read_shp_ss(shp_path)
        PD = cal_pd(gdf_ss, longitude, latitude, year, month)
        PF = cal_pf(gdf_ss)
        
        return {'shp_path': shp_path, 'pd': PD, 'pf': PF}
    except Exception as e:
        print(f"Error processing {shp_path}: {str(e)}")
        return None

def main():
    image_types = ('.shp')
    shp_paths = []
    
    for root, dirs, files in os.walk(r'D:\Ai\sv\fisheye_shp'):
        for file in files:
            if file.endswith(".shp"):
                file_path = os.path.join(root, file)
                shp_paths.append(file_path)
    
    image_ss_csv = r'D:\Ai\sv\sv_points_ori_pd_pf.csv'
    
    # Create empty DataFrame to store results
    results_df = pd.DataFrame(columns=['shp_path', 'pd', 'pf'])
    
    # Use multiprocessing
    num_processes = cpu_count()
    with Pool(processes=num_processes) as pool:
        # Use partial to pass the output_csv parameter
        process_func = partial(process_shp_file, output_csv=image_ss_csv)
        
        # Use tqdm to show progress
        results = list(tqdm(pool.imap(process_func, shp_paths), total=len(shp_paths)))
    
    # Filter out None results (failed processes)
    valid_results = [r for r in results if r is not None]
    
    # Convert to DataFrame
    if valid_results:
        results_df = pd.DataFrame(valid_results)
        
        # Save to CSV
        results_df.to_csv(image_ss_csv, index=False)
        print(f"Results saved to {image_ss_csv}")
    else:
        print("No valid results to save.")

if __name__ == '__main__':
    main()
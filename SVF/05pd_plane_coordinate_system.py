import matplotlib.pyplot as plt
from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta
import pytz
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

from shapely.geometry import Polygon, LineString, Point
from tqdm import tqdm
import os
import geopandas as gpd
from shapely.affinity import scale

# 创建绘图对象
fig, ax = plt.subplots(figsize=(12, 10))

# 1 读取天空的轮廓SHP文件
shp_path = r"e:\work\sv_j_ran\20241227\pan2fish\fish_shp\121.434537_31.1965683_202002.shp"
gdf_ss = gpd.read_file(shp_path)

# 计算几何中心
center = gdf_ss.geometry.centroid.union_all().centroid
# print(center)
center_coords = (center.x, center.y)  # 获取中心点的坐标

# 平移所有几何对象，使原点位于几何中心
gdf_ss['geometry'] = gdf_ss.geometry.translate(-center_coords[0], -center_coords[1])

# 获取边界框 (minx, miny, maxx, maxy)
bounds = gdf_ss.total_bounds

# 计算原始宽度和高度
original_width = bounds[2] - bounds[0]  # maxx - minx
original_height = bounds[3] - bounds[1]  # maxy - miny

# 计算缩放比例（以宽度或高度中的较大值为基准）
max_dimension = max(original_width, original_height)
scale_factor = 180 / max_dimension # 极坐标系的长短为-90 90，因此这里总长度为180

# 对几何对象进行缩放
# gdf_ss['geometry'] = gdf_ss.geometry.scale(scale_factor, scale_factor, origin='center')
gdf_ss['geometry'] = gdf_ss.geometry.scale(scale_factor, scale_factor, origin=(0,0))

# 检查是否存在 'value' 字段
if 'value' not in gdf_ss.columns:
    raise ValueError("SHP文件中不存在 'value' 字段")

# 找到 value 不为 0 的几何对象
gdf_ss = gdf_ss[gdf_ss['value'] != 0]

gdf_ss.set_crs("EPSG:4326", inplace=True)
# 绘制第一个 SHP 文件，设置为红色
# gdf_ss.plot(ax=ax, color='red', label='Layer 1')
# print(gdf_ss.crs)

# gdf_ss.plot()
# plt.show()

# 定义原点
origin = Point(0, 0)
# 定义线段长度
length = 100
# 定义角度列表（每45°一根线段）
angles = np.arange(0, 360, 45)  # [0, 45, 90, 135, 180, 225, 270, 315]
# 定义圆圈半径
radii = [30, 60, 90]
# 创建一个空的 GeoDataFrame
gdf_edge = gpd.GeoDataFrame(columns=["type", "geometry"], crs="EPSG:4326")
# 2 生成线段并添加到 GeoDataFrame
for angle in angles:
    # 将角度转换为弧度
    radians = np.deg2rad(angle)
    # 计算终点坐标
    end_x = origin.x + length * np.cos(radians)
    end_y = origin.y + length * np.sin(radians)
    end_point = Point(end_x, end_y)
    # 创建 LineString
    line = LineString([origin, end_point])
    # 添加到 GeoDataFrame
    gdf_edge.loc[len(gdf_edge)] = {"type": f"line_{angle}", "geometry": line}
# 3 生成圆圈并添加到 GeoDataFrame
for radius in radii:
    # 生成圆的边界点
    angles_circle = np.linspace(0, 2 * np.pi, 100)  # 将圆分为 100 个点
    circle_points = [Point(origin.x + radius * np.cos(angle), origin.y + radius * np.sin(angle)) for angle in angles_circle]
    # 将点连接成 LineString
    circle_boundary = LineString(circle_points)
    # 添加到 GeoDataFrame
    gdf_edge.loc[len(gdf_edge)] = {"type": f"circle_r{radius}", "geometry": circle_boundary}

# 合并两个 GeoDataFrame
# gdf_ss_edge = gpd.GeoDataFrame(pd.concat([gdf_ss, gdf_edge], ignore_index=True), crs=gdf_ss.crs)

# 绘制第二个 SHP 文件，设置为绿色
# gdf_edge.plot(ax=ax, color='green', label='Layer 2')
gdf_edge.set_crs("EPSG:4326", inplace=True)

# print(gdf_edge.crs)

# print(merged_gdf.head())
# merged_gdf.plot(edgecolor='red',lw=0.5)
# plt.show()

# 4 将太阳辐射从极坐标系转为平面坐标系
# 给定的经纬度
latitude = 52.776188701508325  # 纬度
longitude = -1.238319474       # 经度
# 设置时区（英国伦敦时区，UTC+0）
timezone = pytz.timezone('Europe/London')
# 定义日期（例如：2023年10月1日）
date = datetime(2023, 10, 1, tzinfo=timezone)
# 创建一个空的 DataFrame，用于存储结果
data = []
# 遍历一天中的每个小时和分钟
for hour in range(24):  # 0 到 23 小时
    for minute in range(0, 60, 6):  # 每 15 分钟计算一次
        # 构造当前时间
        current_time = date + timedelta(hours=hour, minutes=minute)
        # 计算太阳高度角和方位角
        altitude = get_altitude(latitude, longitude, current_time)
        azimuth = get_azimuth(latitude, longitude, current_time)
        # 将结果添加到列表中
        data.append([hour, minute, altitude, azimuth])
# 将列表转换为 DataFrame
df_solar = pd.DataFrame(data, columns=['Hour', 'Minute', 'Altitude', 'Azimuth'])
# 输出 DataFrame
df_solar = df_solar[df_solar['Altitude']>0]
df_solar.reset_index(drop=True, inplace=True)
# 将Altitude和Azimuth列转换为弧度
df_solar['Altitude_r'] = df_solar['Altitude'].apply(math.radians)
df_solar['Azimuth_r'] = df_solar['Azimuth'].apply(math.radians)

# print(df_solar.head())

# 定义函数：将 Azimuth 转换为标准数学极坐标角度
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

# 应用转换函数
df_solar['xy'] = df_solar[['Altitude','Azimuth']].apply(convert_xy,axis=1)
df_solar['cos_altitude_r']= df_solar['Altitude_r'].apply(lambda x:np.cos(x))

# 解析 xy 列
df_solar['x'] = df_solar['xy'].apply(lambda xy: xy[0])  # 提取 x 坐标
df_solar['y'] = df_solar['xy'].apply(lambda xy: xy[1])  # 提取 y 坐标
# 创建点几何
dst_crs = 'EPSG:4326'
gdf_solar = gpd.GeoDataFrame(df_solar, geometry=gpd.points_from_xy(df_solar.x, df_solar.y), crs=dst_crs)
gdf_solar.set_crs("EPSG:4326", inplace=True)

# 绘制第三个 SHP 文件，设置为蓝色
# gdf_solar.plot(ax=ax, color='blue',lw=0.5, label='Layer 3')
# print(gdf_solar.crs)

# 空间连接：找到落在面内的点
gdf_solar_in_ss = gpd.sjoin(gdf_solar, gdf_ss, predicate='within')

# 绘制第三个 SHP 文件，设置为蓝色
# gdf_solar_in_ss.plot(ax=ax, color='blue',lw=0.5, label='Layer 3')
# print(gdf_solar_in_ss.shape)

# print(gdf_solar_in_ss)

# 太阳直射比例的结果 PD
pd = sum(gdf_solar_in_ss['cos_altitude_r'])/ sum(df_solar['cos_altitude_r'])
print(pd)

# 添加图例
# ax.legend()
# 设置标题
# ax.set_title("Three SHP Files with Different Colors")
# 设置纵横比为相等
# ax.set_aspect('equal')
# 显示图形
# plt.show()
import matplotlib.pyplot as plt
from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta
import pytz
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split, polygonize, unary_union
from shapely.geometry import Polygon, LineString, Point
from tqdm import tqdm
import os
import geopandas as gpd
from shapely.affinity import scale

# 创建绘图对象
fig, ax = plt.subplots(figsize=(12, 10))

# 读取与处理shp问价

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
# 赋值为1，为了将所有sky几何进行合并，便于后面进行分割
gdf_ss['value'] = 1
gdf_ss = gdf_ss.dissolve(by='value')

gdf_ss.set_crs("EPSG:4326", inplace=True)
# 绘制第一个 SHP 文件，设置为红色
# gdf_ss.plot(ax=ax, color='black', label='Layer 1')
# print(gdf_ss.crs)

# gdf_ss.plot(ax=ax, edgecolor='red', label='Layer 1')
# plt.show()
# print(gdf_ss)
# raise('123')

# 创建极坐标线，用于构造天空图

# 定义原点
origin = Point(0, 0)

# 1. 绘制 8 个同心圆
# 半径列表
lstx = [i * 90/8 for i in range(1, 9)]  # [11.25, 22.5, ..., 90.0]
center = Point(0, 0)  # 圆心坐标 (0, 0)

# 创建一个空的 GeoDataFrame
gdf_edge = gpd.GeoDataFrame(columns=["type", "geometry"], crs="EPSG:4326")
# 生成8个同心圆的外边界 LineString
circles = []
for radius in lstx:
    # 创建圆（通过缓冲实现）
    circle = center.buffer(radius)
    # 获取外边界坐标并转为 LineString
    exterior_coords = list(circle.exterior.coords)
    # 将点连接成 LineString
    circle_boundary = LineString(exterior_coords)
    # 添加到 GeoDataFrame
    gdf_edge.loc[len(gdf_edge)] = {"type": f"circle_r{radius}", "geometry": circle_boundary}

# 2. 绘制 16 根旋转线段
angle_interval = 360/16.0
angles = [angle_interval*i for i in range(0, 16)]  # [11.25, 22.5, ..., 90.0]
# 定义线段长度
length = 95

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

# gdf_edge.plot(ax=ax, edgecolor='red', label='Layer 1')
# plt.show()
# print(gdf_edge)
# print(gdf_edge.shape)
# raise('123')

# 3 基于线与圆生成闭合多边形
# 合并所有圆和线为一个几何集合
combined_geoms = unary_union(gdf_edge.geometry)
polygons = list(polygonize(combined_geoms))
gdf_polygons = gpd.GeoDataFrame(geometry=polygons, crs="EPSG:4326")

# 添加属性（可选）
gdf_polygons["area"] = gdf_polygons.geometry.area  # 计算面积
gdf_polygons["id"] = range(len(gdf_polygons))      # 添加ID

# gdf_polygons.plot(ax=ax, edgecolor='red', label='Layer 1')
# gdf_ss.plot(ax=ax, color='black', label='Layer 1')

# print(gdf_polygons)
# print(gdf_polygons.shape)
# 分割天空

dfy= gpd.overlay(gdf_ss,gdf_polygons,how='identity')
projected_crs = "EPSG:4326"  # 请根据实际位置调整
dfy = dfy.to_crs(projected_crs)

dfy.plot(ax=ax, edgecolor='red', label='Layer 1')
dfy["area2"] = dfy.geometry.area  # 计算面积

# 计算三个天顶角
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

# print(dfy)
# print(dfy.shape)

print(np.nansum(dfy['vl'])/16)

# 太阳辐射比例的结果 PF
# 添加图例
# ax.legend()
# 设置标题
# ax.set_title("Three SHP Files with Different Colors")
# 设置纵横比为相等
# ax.set_aspect('equal')
# 显示图形
# plt.show()
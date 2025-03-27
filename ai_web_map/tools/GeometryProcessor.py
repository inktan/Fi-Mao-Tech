# -*- coding: utf-8 -*-
"""
几何运算处理器 - 负责所有与几何相关的操作
Created on 2024.9.30
@author: 非猫科技
"""

from shapely.geometry import LineString, Point
from shapely.ops import transform
import pyproj
from functools import partial
import geopandas as gpd
import dask_geopandas as dgpd

class GeometryProcessor:
    def __init__(self, gcj02_to_wgs84=False):
        """
        初始化几何处理器
        
        参数:
            gcj02_to_wgs84 (bool): 是否将GCJ-02坐标转换为WGS-84
        """
        self.gcj02_to_wgs84 = gcj02_to_wgs84
        self._init_projections()
    
    def _init_projections(self):
        """初始化坐标投影转换"""
        # GCJ-02到WGS-84的近似转换
        self.gcj02_to_wgs84_transformer = partial(
            transform,
            partial(pyproj.transform,
                   pyproj.Proj(init='epsg:3857'),  # GCJ-02近似投影
                   pyproj.Proj(init='epsg:4326'))   # WGS-84
        )
        
        # 用于精确距离计算的投影
        self.distance_transformer = partial(
            pyproj.transform,
            pyproj.Proj(init='epsg:4326'),
            pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84')
        )
    
    def parse_polyline(self, polyline_str):
        """解析polyline字符串为坐标列表"""
        return [list(map(float, point.split(','))) 
                for point in polyline_str.split(';')]
    
    def convert_coords(self, lng, lat):
        """坐标转换"""
        point = Point(lng, lat)
        return self.gcj02_to_wgs84_transformer(point).coords[0]
    
    def create_linestring(self, coords):
        """从坐标列表创建LineString"""
        return LineString(coords)
    
    def load_point_data(self, shp_path, use_dask=False, n_partitions=None):
        """
        加载点数据
        
        参数:
            shp_path (str): Shapefile路径
            use_dask (bool): 是否使用Dask处理大数据
            n_partitions (int): Dask分区数
        """
        if use_dask:
            # 使用Dask-GeoPandas加载
            self.point_gdf = dgpd.read_file(
                shp_path, 
                npartitions=n_partitions or 4,
                chunksize=500000
            )
            self.point_gdf = self.point_gdf.spatial_shuffle()
        else:
            # 使用普通GeoPandas加载
            self.point_gdf = gpd.read_file(shp_path)
        
        # 统一转换为WGS84
        if self.point_gdf.crs and self.point_gdf.crs.to_epsg() != 4326:
            self.point_gdf = self.point_gdf.to_crs(epsg=4326)
        
        return self.point_gdf
    
    def find_nearby_points(self, line_geometries, buffer_distance=50, use_dask=False):
        """
        查找线附近的点
        
        参数:
            line_geometries (list): LineString几何列表
            buffer_distance (int): 缓冲距离(米)
            use_dask (bool): 是否使用Dask
        """
        if not hasattr(self, 'point_gdf'):
            raise ValueError("请先加载点数据")
        
        # 合并所有线
        merged_line = line_geometries[0]
        for line in line_geometries[1:]:
            merged_line = merged_line.union(line)
        
        # 创建缓冲区
        projected_line = transform(self.distance_transformer, merged_line)
        buffered = projected_line.buffer(buffer_distance)
        buffered_wgs84 = transform(partial(pyproj.transform,
                                        pyproj.Proj(proj='aeqd'),
                                        pyproj.Proj(init='epsg:4326')), 
                                buffered)
        
        # 空间查询
        if use_dask and isinstance(self.point_gdf, dgpd.GeoDataFrame):
            mask = self.point_gdf.geometry.within(buffered_wgs84)
            return self.point_gdf[mask].compute()
        else:
            return self.point_gdf[self.point_gdf.geometry.within(buffered_wgs84)]

if __name__ == "__main__":
    print('-')
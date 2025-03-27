# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

import geopandas as gpd
import pandas as pd
from typing import List, Dict, Optional

class NavigationPath:
    def __init__(self, path_data, geometry_processor):
        """
        单条导航路径类
        
        参数:
            path_data (dict): 单条路径的原始数据
            geometry_processor (GeometryProcessor): 几何处理器实例
        """
        self.raw_data = path_data
        self.geo_processor = geometry_processor
        
        # 基础属性
        self.distance = path_data.get('distance')  # 总距离(米)
        self.duration = path_data.get('duration')  # 预计时间(秒)
        self.strategy = path_data.get('strategy')  # 路径策略
        self.tolls = path_data.get('tolls', 0)  # 收费金额(元)
        self.toll_distance = path_data.get('toll_distance', 0)  # 收费路段长度(米)
        self.restriction = path_data.get('restriction')  # 限行信息
        self.traffic_lights = path_data.get('traffic_lights', 0)  # 红绿灯数量
        
        # 路径步骤
        self.steps = self._process_steps(path_data.get('steps', []))
        
        # 空间分析结果
        self.nearby_points = None
        self.mysql_results = None
        self.enriched_points = None
    
    def _process_steps(self, steps_data) -> List[Dict]:
        """处理路径步骤数据"""
        processed_steps = []
        for step in steps_data:
            # 解析polyline
            polyline = self.geo_processor.parse_polyline(step.get('polyline', ''))
            
            if self.geo_processor.gcj02_to_wgs84:
                polyline = [self.geo_processor.convert_coords(lng, lat) for lng, lat in polyline]
            
            # 创建LineString
            linestring = self.geo_processor.create_linestring(polyline)
            
            processed_steps.append({
                'instruction': step.get('instruction'),
                'road': step.get('road'),
                'distance': step.get('distance'),
                'duration': step.get('duration'),
                'geometry': linestring,
                'tolls': step.get('tolls', 0),
                'toll_distance': step.get('toll_distance', 0),
                'traffic_lights': step.get('traffic_lights', 0)
            })
        return processed_steps
    
    def find_nearby_points(self, point_gdf, buffer_distance=50) -> gpd.GeoDataFrame:
        """查找路径附近的所有点"""
        line_geometries = [step['geometry'] for step in self.steps]
        
        if not line_geometries:
            return None
        
        # 使用几何处理器查找附近点
        self.nearby_points = self.geo_processor.find_nearby_points(
            line_geometries, 
            buffer_distance,
            use_dask=isinstance(point_gdf, dgpd.GeoDataFrame)
        )
        return self.nearby_points
    
    def query_mysql_by_ids(self, mysql_config: Dict, id_column: str = 'id') -> Optional[pd.DataFrame]:
        """基于ID查询MySQL数据"""
        if self.nearby_points is None or len(self.nearby_points) == 0:
            print("没有可查询的附近点数据")
            return None
        
        ids = self.nearby_points[id_column].unique().tolist()
        if not ids:
            print("没有找到有效的ID列")
            return None
        
        try:
            engine = create_engine(
                f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@"
                f"{mysql_config['host']}:{mysql_config.get('port', 3306)}/"
                f"{mysql_config['database']}"
            )
            
            query = f"SELECT * FROM {mysql_config.get('table')} WHERE {id_column} IN ({','.join(map(str, ids))})"
            self.mysql_results = pd.read_sql(query, engine)
            
            # 合并数据
            self._merge_mysql_results(id_column)
            
            return self.mysql_results
        
        except Exception as e:
            print(f"MySQL查询失败: {str(e)}")
            return None
    
    def _merge_mysql_results(self, id_column: str):
        """合并MySQL结果与点数据"""
        if not hasattr(self, 'mysql_results') or self.mysql_results.empty:
            return
        
        self.enriched_points = pd.merge(
            self.nearby_points,
            self.mysql_results,
            on=id_column,
            how='left'
        )
        
        # 保持GeoDataFrame类型
        self.enriched_points = gpd.GeoDataFrame(
            self.enriched_points, 
            geometry='geometry',
            crs=self.nearby_points.crs
        )
    
    def get_geodataframe(self) -> gpd.GeoDataFrame:
        """将路径数据转换为GeoDataFrame"""
        features = []
        for step_idx, step in enumerate(self.steps):
            features.append({
                'step_id': step_idx,
                'instruction': step['instruction'],
                'road': step['road'],
                'distance': step['distance'],
                'duration': step['duration'],
                'tolls': step['tolls'],
                'toll_distance': step['toll_distance'],
                'traffic_lights': step['traffic_lights'],
                'geometry': step['geometry']
            })
        
        return gpd.GeoDataFrame(features, crs='EPSG:4326')

if __name__ == "__main__":
    print('-')
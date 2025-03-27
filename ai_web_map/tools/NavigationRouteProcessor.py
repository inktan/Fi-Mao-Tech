# -*- coding: utf-8 -*-
"""
导航路线处理器 - 负责业务逻辑和数据处理
Created on 2024.9.30
@author: 非猫科技
"""

class NavigationRouteProcessor:
    def __init__(self, route_data, gcj02_to_wgs84=True, config_path='config.ini'):
        """
        完全封装的导航路线处理器
        
        参数:
            route_data (dict): 高德地图返回的路线数据
            gcj02_to_wgs84 (bool): 是否转换坐标系
            config_path (str): 配置文件路径
        """
        from .geometry_processor import GeometryProcessor  # 假设有单独模块
        
        # 初始化几何处理器
        self.geo_processor = GeometryProcessor(gcj02_to_wgs84=gcj02_to_wgs84)
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 处理路线数据
        self.original_data = route_data
        self.paths = self._init_paths()
        
        # 内部状态
        self._point_gdf = None
        self._mysql_engine = None
    
    def _load_config(self, config_path):
        """加载配置文件"""
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        return {
            'mysql': {
                'host': config.get('MYSQL', 'host'),
                'port': config.getint('MYSQL', 'port', fallback=3306),
                'user': config.get('MYSQL', 'user'),
                'password': config.get('MYSQL', 'password'),
                'database': config.get('MYSQL', 'database'),
                'table': config.get('MYSQL', 'table', fallback='points')
            },
            'shp_path': config.get('DATA', 'point_shp_path')
        }
    
    def _init_paths(self):
        """初始化所有路径"""
        return [
            NavigationPath(path, self.geo_processor)
            for path in self.original_data.get('route', {}).get('paths', [])
        ]
    
    def _get_mysql_engine(self):
        """获取MySQL引擎(懒加载)"""
        if self._mysql_engine is None:
            from sqlalchemy import create_engine
            mysql_cfg = self.config['mysql']
            self._mysql_engine = create_engine(
                f"mysql+pymysql://{mysql_cfg['user']}:{mysql_cfg['password']}@"
                f"{mysql_cfg['host']}:{mysql_cfg['port']}/{mysql_cfg['database']}"
            )
        return self._mysql_engine
    
    def _load_point_data(self, use_dask=False):
        """加载点数据(懒加载)"""
        if self._point_gdf is None:
            shp_path = self.config['shp_path']
            self._point_gdf = self.geo_processor.load_point_data(
                shp_path, use_dask=use_dask
            )
        return self._point_gdf
    
    def process_all(self, buffer_distance=50, id_column='id'):
        """
        一键处理所有流程
        1. 加载点数据
        2. 查找附近点
        3. 查询MySQL数据
        4. 合并结果
        """
        # 加载点数据(自动判断是否使用Dask)
        point_gdf = self._load_point_data(
            use_dask=len(self.paths) > 3  # 如果路径多则使用Dask
        )
        
        # 处理每条路径
        results = {}
        for idx, path in enumerate(self.paths):
            # 查找附近点
            nearby = path.find_nearby_points(point_gdf, buffer_distance)
            
            # 查询MySQL
            if nearby is not None and not nearby.empty:
                mysql_data = pd.read_sql(
                    f"SELECT * FROM {self.config['mysql']['table']} "
                    f"WHERE {id_column} IN ({','.join(map(str, nearby[id_column].unique()))})",
                    con=self._get_mysql_engine()
                )
                
                # 合并数据
                if not mysql_data.empty:
                    enriched = pd.merge(
                        nearby,
                        mysql_data,
                        on=id_column,
                        how='left'
                    )
                    path.enriched_points = gpd.GeoDataFrame(
                        enriched, 
                        geometry='geometry',
                        crs=nearby.crs
                    )
                    results[idx] = path.enriched_points
        
        return results
    
    def save_all_results(self, output_dir, driver='ESRI Shapefile'):
        """
        保存所有路径的增强结果
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        for idx, path in enumerate(self.paths):
            if path.enriched_points is not None:
                output_path = os.path.join(output_dir, f'path_{idx}.shp')
                path.enriched_points.to_file(output_path, driver=driver)
                saved_files.append(output_path)
        
        return saved_files
    
    def get_summary(self):
        """获取所有路径的统计摘要"""
        summary = []
        for path in self.paths:
            path_data = {
                'distance': path.distance,
                'duration': path.duration,
                'tolls': path.tolls,
                'strategy': path.strategy,
                'has_nearby': path.nearby_points is not None,
                'has_enriched': path.enriched_points is not None
            }
            if path.enriched_points is not None:
                path_data['feature_count'] = len(path.enriched_points)
            summary.append(path_data)
        
        return pd.DataFrame(summary)

# if __name__ == '__main__':
    # 初始化处理器(自动加载配置)
    # processor = NavigationRouteProcessor(
    #     route_data=amap_route_data,
    #     gcj02_to_wgs84=True,
    #     config_path='config.ini'
    # )

    # 一键处理所有流程
    # processor.process_all(buffer_distance=50)

    # 保存结果
    # saved_files = processor.save_all_results('output')

    # 获取统计信息
    # summary = processor.get_summary()
    # print(summary)

if __name__ == "__main__":
    print('-')
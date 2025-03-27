# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

import geopandas as gpd
import pandas as pd
from typing import List, Dict, Optional
import NavigationRouteProcessor, NavigationPath, load_config, GeometryProcessor
from transformers import pipeline
import numpy as np

class MultiModalRoutePlanner:
    def __init__(self, config_path='config.ini'):
        """
        多模式出行路径规划器
        
        参数:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.route_processors = {
            0: self._plan_driving_route,   # 驾车
            1: self._plan_walking_route,   # 步行
            2: self._plan_cycling_route,   # 骑行
            3: self._plan_transit_route    # 公共交通
        }
        # 初始化NLP模型 (按需加载)
        self.classifier = None
        if self.use_nlp:
            try:
                self.classifier = pipeline("text-classification")
            except Exception as e:
                print(f"无法加载NLP模型: {str(e)}")
                self.use_nlp = False
        
        # 关键词库配置
        self.preference_keywords = {
            'greenest': ['绿化', '绿视率', '公园', '风景', '景观', '美丽', '漂亮', 'beautiful', 'scenic'],
            'fastest': ['最快', '时间短', '赶时间', '尽快', '速度', '少花时间', 'urgent', 'fast', 'quick'],
            'safest': ['安全', '危险', '事故', '安心', '保险', '可靠', 'safe', 'security']
        }

    def analyze_user_preference(self, messages: List[Dict]) -> str:
        """
        综合NLP和关键词分析用户偏好
        
        参数:
            messages: 聊天消息列表
            
        返回:
            str: 推荐策略 ('balanced', 'fastest', 'greenest', 'safest')
        """
        if not messages:
            return 'balanced'
        
        # 合并用户消息内容
        content = " ".join([msg['content'] for msg in messages if msg['role'] == 'user']).lower()
        
        # 1. 使用NLP情感分析 (如果可用)
        nlp_result = None
        if self.use_nlp and self.classifier:
            try:
                nlp_result = self.classifier(content[:512])[0]  # 截断长文本
            except Exception as e:
                print(f"NLP分析失败: {str(e)}")
        
        # 2. 关键词匹配
        keyword_scores = {k: 0 for k in self.preference_keywords}
        for criteria, keywords in self.preference_keywords.items():
            keyword_scores[criteria] = sum(keyword in content for keyword in keywords)
        
        # 3. 综合决策
        max_score = max(keyword_scores.values())
        if max_score > 0:
            # 有关键词匹配时优先使用
            return max(keyword_scores, key=keyword_scores.get)
        elif nlp_result:
            # 无关键词时使用NLP结果
            if nlp_result['label'] == 'POSITIVE' and any(w in content for w in ['美', '漂亮']):
                return 'greenest'
            elif 'urgent' in content or nlp_result['label'] == 'NEGATIVE':
                return 'fastest'
        
        # 默认平衡策略
        return 'balanced'           

    def _load_config(self, config_path):
        """加载配置文件"""
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        return {
            'amap_key': config.get('AMAP', 'api_key'),
            'baidu_key': config.get('BAIDU_MAP', 'api_key'),
            'mysql': {
                'host': config.get('MYSQL', 'host'),
                'port': config.getint('MYSQL', 'port', fallback=3306),
                'user': config.get('MYSQL', 'user'),
                'password': config.get('MYSQL', 'password'),
                'database': config.get('MYSQL', 'database'),
                'table': config.get('MYSQL', 'table', fallback='points')
            },
            'shp_path': config.get('DATA', 'point_shp_path', fallback='points.shp')
        }
    
    def plan_optimal_route(self, locations: List, transport_type: int, messages: List[Dict] = None, **kwargs):
        """
        规划最优路径
        
        参数:
            locations: 经纬度坐标列表 [[lng,lat],...]
            transport_type: 出行方式(0-驾车,1-步行,2-骑行,3-公交)
            **kwargs: 各出行方式的特定参数
        
        返回:
            dict: 包含最优路径信息和评分
        """
        if transport_type not in self.route_processors:
            raise ValueError(f"不支持的出行方式: {transport_type}")
        
        # 获取基础路径数据
        route_data = self.route_processors[transport_type](locations, **kwargs)
        
        # 处理路径数据
        processor = NavigationRouteProcessor(route_data)
        processor.process_all()
        
        # 评估路径
        evaluator = PathEvaluator()
        evaluator.add_paths([path.enriched_points for path in processor.paths])
        
        # 根据出行方式调整权重
        weights = self._get_weights_for_transport(transport_type)
        results = evaluator.evaluate_paths(custom_weights=weights)
        
        # 返回最优路径
        if messages:
            criteria = self.analyze_user_preference(messages)
            print(f"根据用户偏好选择策略: {criteria}")
        else:
            criteria = 'balanced'

        best_idx = evaluator.get_optimal_path(criteria)
        return {
            'route_data': processor.paths[best_idx],
            'evaluation': results.iloc[0].to_dict(),
            'all_options': results.to_dict('records')
        }
    
    def _get_weights_for_transport(self, transport_type: int) -> Dict:
        """根据不同出行方式获取权重配置"""
        # 基础权重配置
        weights = {
            'visual': {
                'w_G': 0.2, 'w_S': 0.1, 'w_V': 0.1,
                'w_B': 0.1, 'w_SW': 0.05, 'w_RW': 0.05
            },
            'perception': {
                'w_We': 0.05, 'w_Be': 0.1, 'w_Bo': -0.05,
                'w_Sa': 0.1, 'w_De': -0.05, 'w_Li': 0.05
            },
            'time_cost': {'w_Ti': 0.1}
        }
        
        # 根据不同出行方式调整权重
        if transport_type == 0:  # 驾车
            weights['visual']['w_V'] = 0.15  # 更关注车流量
            weights['time_cost']['w_Ti'] = 0.2  # 更重视时间
        elif transport_type == 1:  # 步行
            weights['visual']['w_G'] = 0.3  # 更关注绿化
            weights['perception']['w_Be'] = 0.15  # 更重视美观
            weights['time_cost']['w_Ti'] = 0.05  # 时间不重要
        elif transport_type == 2:  # 骑行
            weights['visual']['w_G'] = 0.25
            weights['perception']['w_Sa'] = 0.15  # 更重视安全
        elif transport_type == 3:  # 公交
            weights['visual']['w_B'] = 0.15  # 更关注建筑(站点)
            weights['time_cost']['w_Ti'] = 0.15
        
        return weights
    
    def _plan_driving_route(self, locations: List, **kwargs):
        """规划驾车路线"""
        from .api_utils import get_amap_driving_route, get_baidu_driving_route
        
        origin = locations[0]
        destination = locations[-1]
        waypoints = locations[1:-1] if len(locations) > 2 else None
        
        # 获取高德和百度双方案
        gd_route = get_amap_driving_route(
            origin, destination, waypoints, 
            self.config['amap_key'],
            strategy=kwargs.get('strategy', 11)  # 默认多策略
        )
        
        bd_route = get_baidu_driving_route(
            origin, destination, waypoints,
            self.config['baidu_key'],
            tactics=kwargs.get('tactics', 11)  # 默认最少时间
        )
        
        # 合并结果
        combined = {
            'route': {
                'paths': gd_route['route']['paths'] + bd_route['result']['routes']
            }
        }
        return combined
    
    def _plan_walking_route(self, locations: List, **kwargs):
        """规划步行路线"""
        from .api_utils import get_amap_walking_route
        
        origin = locations[0]
        destination = locations[-1]
        waypoints = locations[1:-1] if len(locations) > 2 else None
        
        return get_amap_walking_route(
            origin, destination, waypoints,
            self.config['amap_key']
        )
    
    def _plan_cycling_route(self, locations: List, **kwargs):
        """规划骑行路线"""
        from .api_utils import get_amap_cycling_route
        
        origin = locations[0]
        destination = locations[-1]
        waypoints = locations[1:-1] if len(locations) > 2 else None
        
        return get_amap_cycling_route(
            origin, destination, waypoints,
            self.config['amap_key']
        )
    
    def _plan_transit_route(self, locations: List, **kwargs):
        """规划公交路线"""
        from .api_utils import get_amap_transit_route
        
        origin = locations[0]
        destination = locations[-1]
        
        return get_amap_transit_route(
            origin, destination,
            self.config['amap_key'],
            city=kwargs.get('city', '全国')
        )

if __name__ == "__main__":
    print('-')
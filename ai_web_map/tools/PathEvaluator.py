# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

import geopandas as gpd
import pandas as pd
import numpy as np
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

class PathEvaluator:
    def __init__(self):
        """
        初始化路径评价分析器
        
        属性:
            weight_categories: 权重类别及对应的关键词
            weight_factors: 各权重因子的默认权重值
        """
        # 定义视觉要素权重类别
        self.weight_categories = {
            '绿视率权重 (w_G)': ['tree', 'palm', 'grass'],
            '天空度权重 (w_S)': ['sky'],
            '车辆视率权重 (w_V)': ['car, auto; automobile; machine; molorar','bus; autobus; coach; charabanc; double-decker; itney; motorbus; motorcoach; omnibus; passenger vehicle','van','minibike; motorbike','bicycle; bike; wheel; cycle'],
            '建筑视率权重 (w_B)': ['building', 'edifice'],
            '人行道视率权重 (w_SW)': ['sidewalk', 'pavement'],
            '车行道视率权重 (w_RW)': ['road', 'route']
        }
        
        # 定义环境感知权重类别
        self.perception_categories = {
            '富裕权重 (w_We)': ['wealthy'],
            '美丽权重 (w_Be)': ['beautiful'],
            '无聊权重 (w_Bo)': ['boring'],
            '安全权重 (w_Sa)': ['safety'],
            '压抑权重 (w_De)': ['depressing'],
            '活泼权重 (w_Li)': ['lively']
        }
        
        # 设置默认权重因子 (总和为1)
        self.weight_factors = {
            'visual': {  # 视觉要素权重 (总和0.6)
                'w_G': 0.2,  # 绿视率
                'w_S': 0.1,  # 天空度
                'w_V': 0.1,  # 车辆视率
                'w_B': 0.1,  # 建筑视率
                'w_SW': 0.05,  # 人行道
                'w_RW': 0.05   # 车行道
            },
            'perception': {  # 环境感知权重 (总和0.3)
                'w_We': 0.05,  # 富裕
                'w_Be': 0.1,   # 美丽
                'w_Bo': -0.05, # 无聊(负向)
                'w_Sa': 0.1,   # 安全
                'w_De': -0.05, # 压抑(负向)
                'w_Li': 0.05   # 活泼
            },
            'time_cost': {  # 时间成本权重 (0.1)
                'w_Ti': 0.1
            }
        }
        # 加载历史文化街区的多边形数据
        self.historical_areas = gpd.read_file(polygon_geojson_path)
        self.historical_areas = self.historical_areas.to_crs("EPSG:4326")  # 确保坐标系一致
        
        # 结构化数据 验证权重总和为1
        self._validate_weights()

        # 非结构化文本评价 AI评价配置
        self.openai_api_key = openai_api_key
        self.ai_weight = 0.5  # AI评分在总分中的权重(可调整)
        
        # 缓存AI评分结果
        self.ai_score_cache = {}
    
    def _validate_weights(self):
        """验证权重总和是否为1"""
        total = 0
        for category in self.weight_factors.values():
            total += sum(category.values())
        
        if not np.isclose(total, 1.0, atol=0.001):
            raise ValueError(f"权重总和应为1.0，当前为{total:.3f}")
    
    def add_paths(self, paths: List[gpd.GeoDataFrame]):
        """
        添加待分析的路径数据
        参数:
            paths: NavigationPath.enriched_points 列表
        """
        self.paths = paths
        self._preprocess_data()
    
    def _preprocess_data(self):
        """预处理数据，提取各权重要素"""
        for i, path in enumerate(self.paths):
            # 确保有必要的列
            if not all(col in path.columns for col in ['name', 'id']):
                raise ValueError("路径数据必须包含'name'和'id'列")
            
            # 添加视觉要素计数
            for category, keywords in self.weight_categories.items():
                path[category] = path['id'].apply(
                    lambda x: self._count_keywords(x, keywords)
                )
            
            # 添加环境感知评分
            for category, keywords in self.perception_categories.items():
                path[category] = path['id'].apply(
                    lambda x: self._count_keywords(x, keywords)
                )
    
    def _count_keywords(self, text: str, keywords: List[str]) -> float:
        """
        计算文本中关键词出现的频率
        参数:
            text: 待分析的文本
            keywords: 关键词列表
        返回:
            匹配到的关键词数量 (归一化到0-1)
        """
        if pd.isna(text):
            return 0.0
        
        text = text.lower()
        count = sum(keyword.lower() in text for keyword in keywords)
        return min(count / 10, 1.0)  # 上限为1.0

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_ai_evaluation(self, text: str) -> float:
        """
        方式-01
        使用OpenAI评估文本描述
        返回标准化评分(0-1)
        方式-02
        文本可以选择前置到数据库中
        """
        if not text or not self.openai_api_key:
            return 0.5  # 默认中性评分
            
        if text in self.ai_score_cache:
            return self.ai_score_cache[text]
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": """你是一个专业的路径评估AI。请根据以下驾车路线描述，从以下维度进行评分(0-1)：
                    1. 驾驶安全性
                    2. 路线舒适度
                    3. 沿途景观质量
                    4. 交通流畅度
                    返回一个综合评分，直接输出0到1之间的数字，不要任何解释。"""
                }, {
                    "role": "user",
                    "content": text
                }],
                temperature=0.2,
                max_tokens=10
            )
            
            score = float(response.choices[0].message.content.strip())
            score = max(0, min(1, score))  # 确保在0-1范围内
            self.ai_score_cache[text] = score
            return score
            
        except Exception as e:
            print(f"AI评估失败: {str(e)}")
            return 0.5  # 出错时返回中性评分

    def evaluate_paths(self, custom_weights: Dict = None, use_ai: bool = True) -> pd.DataFrame:
        """
        评估所有路径并返回评分结果(集成AI文本分析)
        
        参数:
            custom_weights: 自定义权重因子
            use_ai: 是否使用AI文本分析
        返回:
            包含各路径评分的DataFrame
        """
        if not hasattr(self, 'paths'):
            raise ValueError("请先使用add_paths()添加路径数据")
        
        # 使用自定义权重或默认权重
        weights = custom_weights if custom_weights else self.weight_factors
        self._validate_custom_weights(weights)
        
        results = []
        for i, path in enumerate(self.paths):
            # 计算视觉要素得分
            visual_score = 0
            for factor, weight in weights['visual'].items():
                col_name = next(k for k in self.weight_categories if factor in k)
                visual_score += path[col_name].mean() * weight
            
            # 计算环境感知得分
            perception_score = 0
            for factor, weight in weights['perception'].items():
                col_name = next(k for k in self.perception_categories if factor in k)
                perception_score += path[col_name].mean() * weight
            
            # 计算时间成本得分 (假设路径有duration属性)
            time_score = 0
            if 'duration' in path.attrs: 
                norm_duration = 1 - (path.attrs['duration'] / (path.attrs['duration'].max() + 1e-6))
                time_score = norm_duration * weights['time_cost']['w_Ti']
            
            # 综合得分
            total_score = visual_score + perception_score + time_score
            
            # AI文本评分 (如果可用)
            ai_score = 0
            if use_ai and 'ai_text' in path.columns:
                # 计算所有点的平均AI评分
                ai_scores = []
                for text in path['ai_text'].dropna():
                    ai_scores.append(self._get_ai_evaluation(text))
                
                ai_score = np.mean(ai_scores) if ai_scores else 0.5
            else:
                ai_score = 0.5  # 默认中性评分
            
            # 综合得分 (结构化数据得分占70%，AI评分占30%)
            structured_score = visual_score + perception_score + time_score
            total_score = (structured_score * (1 - self.ai_weight)) + (ai_score * self.ai_weight)
            
            # 检查路径是否与任何历史文化街区多边形相交
            collision = False
            for _, area in self.historical_areas.iterrows():
                if path['geometry'].intersects(area['geometry']):
                    collision = True
                    break
            
            # 如果碰撞，总分 *1.1
            if collision:
                total_score *= 1.1

            results.append({
                'path_id': i,
                'visual_score': visual_score,
                'perception_score': perception_score,
                'time_score': time_score,
                'ai_score': ai_score,
                'total_score': total_score,
                'distance': path.attrs.get('distance', 0),
                'duration': path.attrs.get('duration', 0),
                'structured_score': structured_score  # 仅结构化数据得分
            })
        
        result_df = pd.DataFrame(results).sort_values('total_score', ascending=False)
        
        # 添加评分解释
        if use_ai and 'ai_text' in path.columns:
            result_df['score_type'] = result_df.apply(
                lambda x: "AI增强评分" if x['ai_score'] != 0.5 else "基础评分", 
                axis=1
            )
        
        return result_df
    
    def _validate_custom_weights(self, weights: Dict):
        """验证自定义权重是否有效"""
        required_categories = ['visual', 'perception', 'time_cost']
        if not all(cat in weights for cat in required_categories):
            raise ValueError(f"自定义权重必须包含{required_categories}")
        
        total = 0
        for category in weights.values():
            total += sum(category.values())
        
        if not np.isclose(total, 1.0, atol=0.001):
            raise ValueError(f"自定义权重总和应为1.0，当前为{total:.3f}")
    
    def get_optimal_path(self, criteria: str = 'balanced') -> int:
        """
        根据指定标准获取最优路径
        参数:
            criteria: 选择标准 ('balanced', 'fastest', 'greenest', 'safest')
        返回:
            最优路径的索引
        """
        if not hasattr(self, 'paths'):
            raise ValueError("请先使用evaluate_paths()评估路径")
        
        df = self.evaluate_paths()
        
        if criteria == 'balanced':
            return df.iloc[0]['path_id']
        elif criteria == 'fastest':
            return df.sort_values('duration').iloc[0]['path_id']
        elif criteria == 'greenest':
            return df.sort_values('visual_score', ascending=False).iloc[0]['path_id']
        elif criteria == 'safest':
            return df.sort_values('perception_score', ascending=False).iloc[0]['path_id']
        else:
            raise ValueError(f"未知的选择标准: {criteria}")


    def explain_score(self, path_id: int) -> str:
        """
        获取路径评分的详细解释
        """
        if not hasattr(self, 'paths'):
            raise ValueError("请先评估路径")
        
        path = self.paths[path_id]
        explanation = []
        
        # 结构化数据解释
        explanation.append("=== 结构化数据评分 ===")
        explanation.append(f"绿视率贡献: {path['绿视率权重 (w_G)'].mean():.2f} * {self.weight_factors['visual']['w_G']} = "
                          f"{path['绿视率权重 (w_G)'].mean() * self.weight_factors['visual']['w_G']:.3f}")
        # ... [添加其他要素解释] ...
        
        # AI解释
        if 'ai_text' in path.columns:
            sample_text = path['ai_text'].dropna().iloc[0] if not path['ai_text'].dropna().empty else ""
            explanation.append("\n=== AI文本分析 ===")
            explanation.append(f"采样文本: {sample_text[:100]}...")
            explanation.append(f"AI评分权重: {self.ai_weight}")
        
        return "\n".join(explanation)

if __name__ == "__main__":
    print('-')
# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

# 必须在所有其他导入之前执行！
from gevent import monkey
monkey.patch_all()  # 优先打补丁

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
from gevent import pywsgi
import re
import json
import requests
from urllib.parse import urlencode
from flask import Response
import json
from coord_convert.transform import gcj2bd
from tools import MultiModalRoutePlanner
import configparser
import requests
from typing import List, Dict, Optional
from flask import Flask, request, jsonify, Response
import requests
from gevent.pywsgi import WSGIServer
from concurrent.futures import ThreadPoolExecutor
import threading
import json
from functools import wraps
import threading
from flask import copy_current_request_context

# 创建线程池执行器
_executor = ThreadPoolExecutor(max_workers=50)

app = Flask(__name__)
CORS(app)

# 使用连接池优化HTTP请求
SESSION = requests.Session()
SESSION.mount('https://', requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100))

class MapConfig:
    def __init__(self, config_path='config.ini'):
        """
        初始化地图配置读取器
        
        参数:
            config_path (str): 配置文件路径
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
    
    def get_amap_config(self) -> Dict:
        """获取高德地图配置"""
        return {
            'api_key': self.config.get('AMAP', 'api_key'),
            'base_url': self.config.get('AMAP', 'base_url'),
            'route_endpoint': self.config.get('AMAP', 'driving_endpoint'),
            'default_city': self.config.get('AMAP', 'default_city', fallback='')
        }
    
    def get_baidu_map_config(self) -> Dict:
        """获取百度地图配置"""
        return {
            'api_key': self.config.get('BAIDU_MAP', 'api_key'),
            'base_url': self.config.get('BAIDU_MAP', 'base_url'),
            'route_endpoint': self.config.get('BAIDU_MAP', 'route_endpoint'),
            'coord_type': self.config.get('BAIDU_MAP', 'coord_type', fallback='bd09ll')
        }

def get_amap_driving_route(
    origin: List[float],
    destination: List[float],
    waypoints: Optional[List[List[float]]] = None,
    strategy: int = 11,
    config_path: str = 'config.ini'
) -> Dict:
    """
    获取高德地图驾车路线规划(从配置文件读取配置)
    
    参数:
        origin: 起点经纬度 [lng, lat] (GCJ-02坐标系)
        destination: 终点经纬度 [lng, lat] (GCJ-02坐标系)
        waypoints: 途经点列表 [[lng1,lat1], [lng2,lat2], ...]
        strategy: 路线策略(0-速度优先 1-费用优先 2-距离优先 3-不走高速 4-多策略 11-多策略返回)
        config_path: 配置文件路径
        
    返回:
        dict: 包含路线信息的字典
        
    异常:
        ValueError: 当API返回错误时
        Exception: 当请求失败时
    """
    # 读取配置
    map_config = MapConfig(config_path)
    amap_config = map_config.get_amap_config()
    
    # 构造途经点字符串
    waypoints_str = ""
    if waypoints:
        waypoints_str = "|".join([f"{lng},{lat}" for lng, lat in waypoints])
    
    # 构造请求参数
    params = {
        'origin': f"{origin[0]},{origin[1]}",
        'destination': f"{destination[0]},{destination[1]}",
        'waypoints': waypoints_str,
        'key': amap_config['api_key'],
        'strategy': str(strategy),
        'extensions': 'all'  # 返回全部路线信息
    }
    
    # 发送请求
    url = f"{amap_config['base_url']}{amap_config['route_endpoint']}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != '1':
            raise ValueError(f"高德API错误: {data.get('info', '未知错误')}")
        
        return data
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"请求高德API失败: {str(e)}")

def get_baidu_driving_route(
    origin: List[float],
    destination: List[float],
    waypoints: Optional[List[List[float]]] = None,
    tactics: int = 11,
    config_path: str = 'config.ini'
) -> Dict:
    """
    获取百度地图驾车路线规划(从配置文件读取配置)
    
    参数:
        origin: 起点经纬度 [lng, lat] (BD09坐标系)
        destination: 终点经纬度 [lng, lat] (BD09坐标系)
        waypoints: 途经点列表 [[lng1,lat1], [lng2,lat2], ...]
        tactics: 路线策略(11-最少时间, 12-最短距离, 13-避开高速)
        config_path: 配置文件路径
        
    返回:
        dict: 包含路线信息的字典
        
    异常:
        ValueError: 当API返回错误时
        Exception: 当请求失败时
    """
    # 读取配置
    map_config = MapConfig(config_path)
    baidu_config = map_config.get_baidu_map_config()
    
    # 百度API需要将途经点包含在起点和终点中
    all_points = [origin]
    if waypoints:
        all_points.extend(waypoints)
    all_points.append(destination)
    
    # 构造请求参数
    params = {
        'origin': f"{origin[1]},{origin[0]}",  # 百度使用"纬度,经度"格式
        'destination': f"{destination[1]},{destination[0]}",
        'waypoints': ";".join([f"{point[1]},{point[0]}" for point in all_points[1:-1]]),
        'ak': baidu_config['api_key'],
        'tactics': str(tactics),
        'coord_type': baidu_config['coord_type'],
        'ret_coordtype': baidu_config['coord_type'],
        'output': 'json'
    }
    
    # 发送请求
    url = f"{baidu_config['base_url']}{baidu_config['route_endpoint']}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 0:
            raise ValueError(f"百度API错误: {data.get('message', '未知错误')}")
        
        return data
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"请求百度API失败: {str(e)}")


def get_location_coordinates(address, city='苏州', api_key=None):
    """
    使用高德地图API将地点名称转换为经纬度坐标
    参数:
        address (str): 要查询的地点名称
        city (str): 城市限制，默认为'苏州'
        api_key (str): 高德地图API密钥
    返回:
        dict: 包含地点信息的字典，格式为:
              {
                  'address': 原始地址,
                  'formatted_address': 标准化地址,
                  'location': 经纬度坐标('经度,纬度'),
                  'longitude': 经度,
                  'latitude': 纬度,
                  'level': 地址匹配的精确度级别
              }
              或 None(如果查询失败)
    异常:
        会抛出requests.exceptions.RequestException或自定义异常
    """
    
    if not api_key:
        raise ValueError("高德地图API密钥不能为空")
    
    # 构造请求参数
    params = {
        'address': address,
        'city': city,
        'key': api_key,
        'output': 'JSON'  # 默认就是JSON，显式声明更清晰
    }
    
    # 构造请求URL
    base_url = 'https://restapi.amap.com/v3/geocode/geo'
    query_string = urlencode(params)
    url = f"{base_url}?{query_string}"
    
    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP错误
        
        data = response.json()
        
        # 检查API返回状态
        if data.get('status') != '1':
            error_msg = data.get('info', '未知错误')
            raise ValueError(f"高德API错误: {error_msg}")
        
        # 提取地理编码结果
        geocodes = data.get('geocodes', [])
        if not geocodes:
            return None
        
        # 取第一个结果(最匹配的)
        first_result = geocodes[0]
        
        # 解析经纬度
        location = first_result.get('location', '')
        if location:
            longitude, latitude = location.split(',')
        else:
            longitude, latitude = None, None
        
        # 构造返回字典
        result = {
            'address': address,
            'formatted_address': first_result.get('formatted_address', ''),
            'location': location,
            'longitude': float(longitude) if longitude else None,
            'latitude': float(latitude) if latitude else None,
            'level': first_result.get('level', ''),
            'city': first_result.get('city', ''),
            'district': first_result.get('district', '')
        }
        
        return result
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"请求高德API失败: {str(e)}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"处理高德API响应时出错: {str(e)}")

def extract_travel_info(content):
    """
    从文本内容中提取旅行信息并处理
    
    参数:
        content (str): 包含JSON代码块的文本内容
        
    返回:
        dict: 包含处理后的路径名称和交通类型的字典，格式为:
              {
                  'pathPointerNames': list,  # 处理后的地点名称列表
                  'transportationType': int   # 交通类型代码
              }
              
    处理规则:
        1. 使用正则表达式提取JSON代码块
        2. 处理TravelLocations:
           - 如果地点不包含"苏州"，则添加"苏州市"前缀
           - 移除所有空白字符
           - 去重并过滤长度小于3的地点
        3. 处理TravelMethod:
           - 包含"铁"或"公交" -> 交通类型3(公共交通)
           - 包含"骑"或"自行" -> 交通类型2(骑行)
           - 包含"步" -> 交通类型1(步行)
           - 其他 -> 交通类型0(默认)
    """
    
    # 定义正则表达式匹配JSON代码块
    json_regex = r'```json([\s\S]*?)```'
    match = re.search(json_regex, content)
    
    if not match:
        raise ValueError("未找到JSON代码块")
    
    try:
        # 解析JSON对象
        json_str = match.group(1).strip()
        json_object = json.loads(json_str)
        
        # 初始化结果字典
        result = {
            'pathPointerNames': [],
            'transportationType': 0
        }
        
        # 处理TravelLocations
        if 'TravelLocations' in json_object:
            temp_path_pointer_names = []
            
            for item in json_object['TravelLocations']:
                # 确保项目是字符串
                if not isinstance(item, str):
                    continue
                
                # 添加苏州前缀
                processed_item = item
                if "苏州" not in processed_item:
                    processed_item = f"苏州市{processed_item}"
                
                # 移除空白字符
                processed_item = re.sub(r'\s+', '', processed_item)
                
                temp_path_pointer_names.append(processed_item)
            
            # 去重并过滤长度>=3的地点
            result['pathPointerNames'] = list(
                {item for item in temp_path_pointer_names if len(item) >= 3}
            )
        
        # 处理TravelMethod
        if 'TravelMethod' in json_object and isinstance(json_object['TravelMethod'], str):
            travel_method = json_object['TravelMethod']
            
            if any(t in travel_method for t in ["铁", "公交"]):
                result['transportationType'] = 3
            elif any(t in travel_method for t in ["骑", "自行"]):
                result['transportationType'] = 2
            elif "步" in travel_method:
                result['transportationType'] = 1
            else:
                result['transportationType'] = 0
        
        return result
    
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise ValueError(f"处理JSON对象时出错: {str(e)}")

# OpenAI代理配置
OPENAI_API_URL = "https://c-z0-api-01.hash070.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o"  # 使用的模型
HEADERS = {
    "Content-Type": "application/json",
    # 如果需要认证，添加你的API密钥
    # "Authorization": "Bearer your-api-key"
}

def generate_statement_prefix():
    """生成用于提取信息的指令前缀"""
    return """按照语义，提取下面对话中，用户的身份，用户的出行方式，用户的最后计划行程中经过的地名、景点、街道名,
最后以 JSON 格式输出以下信息：用户身份、用户出行方式、旅途地点。
格式如下：{'UserIdentity': '儿童', 'TravelMethod': '地铁', 'TravelLocations': ['留园','平江府','拙政园']}\n"""

def prepare_messages(conversation):
    """
    准备发送给OpenAI的消息
    参数:
        conversation: 前端发送的对话记录列表
    返回:
        list: 添加了前缀的完整消息列表
    """
    prefix = generate_statement_prefix()
    # 确保对话记录是字典列表格式
    if not isinstance(conversation, list) or not all(isinstance(item, dict) for item in conversation):
        raise ValueError("对话记录必须是字典组成的列表")
    
    # 在第一条用户消息前添加前缀
    if len(conversation) > 0 and conversation[0].get('role') == 'user':
        conversation[0]['content'] = prefix + conversation[0].get('content', '')
    
    return conversation


# 线程本地存储用于保存请求数据
_request_data = threading.local()

def stream_with_context(f):
    """保持请求上下文的流式生成器装饰器（增强版）"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if hasattr(request, '_preserved_context'):
            return f(*args, **kwargs)
        
        # 保存请求上下文和额外数据
        _request_data.ctx = copy_current_request_context(lambda: None)
        _request_data.extra_data = kwargs.pop('extra_data', None)
        
        try:
            return f(*args, **kwargs)
        finally:
            # 清理线程本地数据
            del _request_data.ctx
            if hasattr(_request_data, 'extra_data'):
                del _request_data.extra_data
    return wrapper

@stream_with_context
def generate_with_extra_data(response):
    """
    生成流式响应并在结束后附加提取的旅行信息
    参数:
        response: requests的流式响应对象
    生成器:
        1. 流式传输原始数据
        2. 收集所有内容片段
        3. 结束后提取旅行信息作为额外数据
    """
    # 用于收集所有内容片段
    full_content = ""
    try:    
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith('data:'):
                    data = decoded_chunk[5:].strip()
                    if data != '[DONE]':
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content_chunk = delta['content']
                                    full_content += content_chunk  # 收集内容
                                    yield f"data: {json.dumps(delta, ensure_ascii=False)}\n\n"
                        except json.JSONDecodeError:
                            continue
        
        # 发送流式传输结束标志
        yield "data: [DONE]\n\n"
        
        # 从完整内容中提取旅行信息
        try:
            travel_info = extract_travel_info(full_content)
            # 从api获取路线信息，与mysql交互，进行指标对比，求出最有路线
            # 转换地点为经纬度
            if 'pathPointerNames' in travel_info and travel_info['pathPointerNames']:
                location_coordinates = []
                
                for location in travel_info['pathPointerNames']:
                    try:
                        # 获取地点坐标
                        coord = get_location_coordinates(location, api_key=AMAP_API_KEY)
                        if coord:
                            location_coordinates.append([coord['longitude'],coord['latitude']])
                    except Exception as e:
                        print(f"转换地点 {location} 失败: {str(e)}")
                        # location_coordinates.append({
                        #     'name': location,
                        #     'error': str(e)
                        # })
                
                travel_info['locationCoordinates'] = location_coordinates
                # gcj02 批量转换为 BD-09
                bd_coordinates = [gcj2bd(lng, lat) for lng, lat in location_coordinates]

                # 初始化规划器
                planner = MultiModalRoutePlanner(config_path='config.ini')

                plan_optimal_route = planner.plan_optimal_route(
                    locations=locations,
                    transport_type=travel_info['transportationType'], 
                    strategy=11,  # 高德多策略
                    messages=prepared_messages
                 )

                extra_data['best_path'] = plan_optimal_route
                
                # 基于分析ai提供的旅行点位，以及出行方式，对旅行路径进行择优判断
                # if travel_info['transportationType'] == 3: # 公共交通
                #     print('-')
                # elif travel_info['transportationType'] == 2: # 骑行
                #     print('-')
                # elif travel_info['transportationType'] == 1: # 步行
                #     print('-')
                # elif travel_info['transportationType'] == 0: # 驾车
                    # print('-')
                    # try:
                        # 第一个点为起点，最后一个点为终点，中间为途经点
                        # origin = location_coordinates[0]
                        # destination = location_coordinates[-1]
                        # waypoints = location_coordinates[1:-1] if len(location_coordinates) > 2 else None
                        # gd
                        # route_data_gd = get_amap_driving_route(origin, destination, waypoints, AMAP_API_KEY)
                        # 初始化处理器(自动加载配置)
                        # processor_gd = NavigationRouteProcessor(
                        #     route_data=route_data_gd,
                        # )
                        # 一键处理所有流程
                        # processor_gd.process_all()

                        # bd
                        # route_data_bd = get_baidu_driving_route(origin, destination, waypoints, AMAP_API_KEY)
                        # route_bd = NavigationRouteProcessor(route_data_bd)
                        # processor_bd = NavigationRouteProcessor(
                        #     route_data=route_data_gd,
                        # )
                        # processor_bd.process_all()
                        # processor_bd.paths

                        # 创建路径评价器
                        # evaluator = PathEvaluator()

                        # 添加所有路径 (合并高德和百度的路径)
                        # all_paths = processor_gd.paths + processor_bd.paths
                        # evaluator.add_paths([path.enriched_points for path in all_paths])

                        # 评估路径
                        # results = evaluator.evaluate_paths(use_ai=True)
                        # print(results)

                        # 获取最优路径 (综合评分最高)

                        # criteria: 选择标准 ('balanced', 'fastest', 'greenest', 'safest')
                        # criteria = analyze_user_preference(messages)
                        # best_path_idx = evaluator.get_optimal_path(criteria)
                        # extra_data['best_path'] = all_paths[best_path_idx]

                        # 这里可以自定义权重示例
                        # custom_weights = {
                        #     'visual': {'w_G': 0.3, 'w_S': 0.1, 'w_V': 0.05, 'w_B': 0.05, 'w_SW': 0.05, 'w_RW': 0.05},
                        #     'perception': {'w_We': 0.05, 'w_Be': 0.15, 'w_Bo': -0.05, 'w_Sa': 0.1, 'w_De': -0.05, 'w_Li': 0.05},
                        #     'time_cost': {'w_Ti': 0.1}
                        # }
                        # custom_results = evaluator.evaluate_paths(custom_weights)

                        # print("\n使用自定义权重的评分:")
                        # print(custom_results)

                    # except Exception as e:
                    #     print(e)

        except Exception as e:
            extra_data = {
                'error': f"Failed to extract travel info: {str(e)}",
                'raw_content': full_content[:200] + "..."  # 只返回部分内容用于调试
            }
        
        # 发送额外数据
        if extra_data:
            yield f"data: {json.dumps({'extra': extra_data}, ensure_ascii=False)}\n\n"
            
    except GeneratorExit:
        # 客户端断开连接时清理资源
        response.close()
        app.logger.info("客户端提前断开连接")
    except Exception as e:
        app.logger.error(f"流生成错误: {str(e)}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    finally:
        # 确保释放资源
        if 'response' in locals():
            response.close()

prepared_messages = ''
@app.route('/api/chat', methods=['POST'])
def chat_completion():
    """处理聊天请求，流式返回OpenAI的响应"""
    try:
        # 获取前端发送的数据
        data = request.get_json()
        
        # 验证数据
        if not data or 'messages' not in data:
            return jsonify({"error": "缺少messages参数"}), 400
        
        messages = data['messages']
        
        # 准备消息（添加前缀）
        prepared_messages = prepare_messages(messages)
        
        # 构造OpenAI请求数据
        # payload = {
        #     "model": OPENAI_MODEL,
        #     "messages": prepared_messages,
        #     "stream": True,  # 启用流式响应
        #     "temperature": 0.7  # 可调整的参数
        # }
        
        # 发送请求到OpenAI代理
        # response = requests.post(
        #     OPENAI_API_URL,
        #     headers=HEADERS,
        #     json=payload,
        #     stream=True  # 保持流式连接
        # )
        
        # 检查响应状态
        # if response.status_code != 200:
        #     error_msg = response.json().get('error', {}).get('message', 'Unknown error')
        #     return jsonify({"error": f"OpenAI API错误: {error_msg}"}), response.status_code
        
        # 将耗时的准备操作放到线程中执行
        future = _executor.submit(process_chat_request, prepared_messages)
        # 使用修改后的生成器
        return Response(future.result(), mimetype='text/event-stream',headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

def process_chat_request(messages):
    """线程中处理聊天请求"""
    try:
        prepared = prepare_messages(messages)
        payload = {
            "model": OPENAI_MODEL,
            "messages": prepared,
            "stream": True,
            "temperature": 0.7
        }
        
        # 使用连接池发送请求
        with SESSION.post(OPENAI_API_URL, headers=HEADERS, json=payload, stream=True) as resp:
            resp.raise_for_status()
            return generate_with_extra_data(resp)
            
    except requests.exceptions.RequestException as e:
        app.logger.error(f"OpenAI请求失败: {str(e)}")
        yield "event: error\ndata: " + json.dumps({"error": str(e)}) + "\n\n"
    except Exception as e:
        app.logger.error(f"处理失败: {str(e)}")
        yield "event: error\ndata: " + json.dumps({"error": str(e)}) + "\n\n"
# if __name__ == '__main__':
    # 使用gevent WSGI服务器
    # server = pywsgi.WSGIServer(('0.0.0.0', 6666), app)
    # print("服务器启动，监听端口 6666...")
    # server.serve_forever()
if __name__ == '__main__':
    # 生产环境使用gevent WSGI服务器
    server = WSGIServer(('0.0.0.0', 6666), app)
    
    # 设置合理的超时和并发参数
    server.max_accept = 1000
    server.backlog = 500
    server.timeout = 300  # 5分钟超时
    
    print("服务器启动 ai web map，监听端口 6666...")
    print(server)
    server.serve_forever()
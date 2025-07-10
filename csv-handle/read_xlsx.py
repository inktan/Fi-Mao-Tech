import pandas as pd
import json
from coord_convert.transform import gcj2wgs  # 确保已安装coord_convert库

def excel_to_json(excel_path, json_path):
    # 读取Excel文件
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    # 检查必要列是否存在
    required_cols = [df.columns[0], '地点', '地址', '评论或介绍']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Excel文件中缺少必要的列: {missing_cols}")
    
    # 重命名第一列为lon_lat
    df = df.rename(columns={df.columns[0]: 'lon_lat'})
    
    # 填充空值为空字符串
    df = df.fillna('')
    
    # 初始化结果列表
    result = []
    current_place = None
    
    # 遍历DataFrame的每一行
    for _, row in df.iterrows():
        # 如果地点不为空，表示新地点开始
        if row['lon_lat'].strip():
            # 保存上一个地点数据
            if current_place:
                result.append(current_place)
            
            # 处理坐标数据
            try:
                # 分割字符串并过滤空值
                coord_str = str(row['lon_lat']).strip()
                parts = [p.strip() for p in coord_str.split(',') if p.strip()]
                # 确保至少有两个有效数值
                if len(parts) >= 2:
                    # 尝试转换为float
                    lon_gcj = float(parts[0])
                    lat_gcj = float(parts[1])
                   
                    # 坐标转换 (GCJ-02 -> WGS-84)
                    lon_wgs, lat_wgs = gcj2wgs(lon_gcj, lat_gcj)
                else:
                    print(f"坐标格式无效 (地点: {row['地点']}, 坐标: {coord_str}): 需要两个数值")
                    coord_str = None
                    lon_gcj, lat_gcj = None, None
                    lon_wgs, lat_wgs = None, None
          
            except Exception as e:
                print(f"坐标转换错误 (地点: {row['地点']}, 坐标: {row['lon_lat']}): {str(e)}")
                lon_wgs, lat_wgs = None, None

            # 创建新地点数据
            if coord_str is not None:
                # 确保坐标字符串格式正确
                coord_str ={
                    'original': coord_str,
                    'gcj02': {'lon': lon_gcj, 'lat': lat_gcj} if lon_gcj is not None else None,
                    'wgs84': {'lon': lon_wgs, 'lat': lat_wgs} if lon_wgs is not None else None
                }
            else:
                coord_str = None    
                
            current_place = {
                'lon_lat': coord_str,

                '地点': row['地点'].strip(),
                '地址': row['地址'].strip(),
                '评论或介绍': [row['评论或介绍'].strip()] if row['评论或介绍'].strip() else []
            }
        else:
            # 如果当前地点存在且评论不为空，添加到评论列表
            if current_place and row['评论或介绍'].strip():
                current_place['评论或介绍'].append(row['评论或介绍'].strip())
    
    # 添加最后一个地点
    if current_place:
        result.append(current_place)
    
    # 保存为JSON文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    return result

# 使用示例
excel_path = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(1).xlsx'  # 替换为你的Excel文件路径
json_path = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(1).json'  # 输出的JSON文件路径

try:
    json_data = excel_to_json(excel_path, json_path)
    print(f"转换成功！共处理 {len(json_data)} 个地点数据")
    print(f"JSON数据已保存到: {json_path}")
except Exception as e:
    print("转换失败:", str(e))
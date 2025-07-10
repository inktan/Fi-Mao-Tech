import json

def remove_duplicate_locations(input_file, output_file):
    """
    处理JSON文件中地点重复的元素，保留每个地点的第一个出现的元素
    
    参数:
        input_file (str): 输入的JSON文件路径
        output_file (str): 输出的JSON文件路径
    """
    # 1. 读取JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. 创建一个字典来跟踪已出现的地点
    seen_locations = {}
    unique_data = []
    duplicate_count = 0
    
    # 3. 遍历数据，检查重复地点
    for item in data:
        if '地点' in item:
            location = item['地点']
            if location not in seen_locations:
                # 如果是新地点，添加到结果中并记录
                seen_locations[location] = True
                unique_data.append(item)
            else:
                duplicate_count += 1
        else:
            # 如果没有地点字段，保留该项
            unique_data.append(item)
    
    # 4. 保存去重后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    
    print(f"处理完成！原始数据 {len(data)} 条，去重后 {len(unique_data)} 条")
    print(f"共移除 {duplicate_count} 条重复地点的数据")
    
    return unique_data

# 使用示例
input_json = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(2).json'  # 输入的JSON文件路径
output_json = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(3).json'  # 输出的JSON文件路径

unique_results = remove_duplicate_locations(input_json, output_json)
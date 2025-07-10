import json
from collections import defaultdict

def process_duplicate_no(json_file_path):
    # 1. 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. 按"no"字段分类数据
    no_dict = defaultdict(list)
    for item in data:
        if 'no' in item:
            no_value = item['地点']
            no_dict[no_value].append(item)
    
    # 3. 找出重复的"no"值
    duplicates = {no: items for no, items in no_dict.items() if len(items) > 1}
    
    print(f"发现 {len(duplicates)} 个重复的'no'值")
    print("重复统计结果（按出现次数降序排列）：")
    for no, count in duplicates.items():
        print(f"'{no}': {len(count)}次")

# 使用示例
input_json = r'e:\work\sv_xiufenganning\文本分析\wuhan(3)(2).json'  # 输入的JSON文件路径

processed_data = process_duplicate_no(input_json)
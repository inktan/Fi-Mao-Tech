import os
import pandas as pd
import re

def process_folders_and_csv(folder_path, csv_file_path, output_csv_path):
    """
    处理文件夹和CSV文件，生成匹配结果
    
    参数:
    folder_path: 要扫描的文件夹路径
    csv_file_path: 输入的CSV文件路径
    output_csv_path: 输出的CSV文件路径
    """
    
    # 读取CSV文件
    print("正在读取CSV文件...")
    try:
        csv_data = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(csv_data)} 行数据")
        print("CSV文件列名:", csv_data.columns.tolist())
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 检查CSV文件中是否有需要的列
    required_columns = ['source_index', 'nearest_commonname']
    if not all(col in csv_data.columns for col in required_columns):
        print(f"CSV文件中缺少必要的列，需要的列: {required_columns}")
        print(f"实际列: {csv_data.columns.tolist()}")
        return
    
    # 获取指定文件夹下的所有文件夹
    print(f"正在扫描文件夹: {folder_path}")
    folder_info = []
    
    if not os.path.exists(folder_path):
        print(f"文件夹路径不存在: {folder_path}")
        return
    
    # 遍历文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            # 使用下划线分割文件夹名
            parts = item.split('_')
            if len(parts) >= 2:
                # 获取第二个部分（索引为1）
                second_part = parts[1]
                
                # 尝试将第二个部分转换为整数（如果是数字的话）
                try:
                    folder_index = int(second_part)
                except ValueError:
                    folder_index = second_part  # 如果不是数字，保持原样
                
                folder_info.append({
                    'folder_name': item,
                    'folder_path': item_path,
                    'extracted_part': second_part,
                    'folder_index': folder_index
                })
            else:
                print(f"文件夹名 '{item}' 不包含足够的下划线分隔部分，跳过")
    
    print(f"找到 {len(folder_info)} 个符合条件的文件夹")
    
    # 创建结果列表
    results = []
    
    # 进行匹配
    print("正在进行匹配...")
    for folder in folder_info:
        folder_idx = folder['folder_index']
        
        # 在CSV数据中查找匹配的source_index
        matched_rows = csv_data[csv_data['source_index'] == folder_idx]
        
        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                results.append({
                    'source_index': row['source_index'],
                    'nearest_commonname': row['nearest_commonname'],
                    'folder_name': folder['folder_name'],
                    'folder_path': folder['folder_path']
                })
        else:
            # 如果没有匹配，也可以选择记录或跳过
            print(f"警告: 文件夹索引 {folder_idx} 在CSV文件中没有匹配的source_index")
    
    # 转换为DataFrame
    if results:
        result_df = pd.DataFrame(results)
        
        # 保存为CSV文件
        print(f"保存结果到 {output_csv_path}...")
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"完成！共生成 {len(result_df)} 条匹配记录")
        
        # 显示结果预览
        print("\n结果预览:")
        print(result_df.head())
        
        return result_df
    else:
        print("没有找到任何匹配的记录")
        return None

def process_folders_with_pattern(folder_path, csv_file_path, output_csv_path, pattern=r'_(\w+)_'):
    """
    使用正则表达式模式处理文件夹名
    
    参数:
    folder_path: 要扫描的文件夹路径
    csv_file_path: 输入的CSV文件路径
    output_csv_path: 输出的CSV文件路径
    pattern: 正则表达式模式，用于提取文件夹名中的特定部分
    """
    
    # 读取CSV文件
    print("正在读取CSV文件...")
    try:
        csv_data = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(csv_data)} 行数据")
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 检查CSV文件中是否有需要的列
    required_columns = ['source_index', 'nearest_commonname']
    if not all(col in csv_data.columns for col in required_columns):
        print(f"CSV文件中缺少必要的列，需要的列: {required_columns}")
        return
    
    # 获取指定文件夹下的所有文件夹
    print(f"正在扫描文件夹: {folder_path}")
    folder_info = []
    
    if not os.path.exists(folder_path):
        print(f"文件夹路径不存在: {folder_path}")
        return
    
    # 编译正则表达式
    regex = re.compile(pattern)
    
    # 遍历文件夹
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            # 使用正则表达式匹配
            match = regex.search(item)
            if match:
                extracted_part = match.group(1)
                
                # 尝试转换为整数（如果是数字的话）
                try:
                    folder_index = int(extracted_part)
                except ValueError:
                    folder_index = extracted_part
                
                folder_info.append({
                    'folder_name': item,
                    'folder_path': item_path,
                    'extracted_part': extracted_part,
                    'folder_index': folder_index
                })
            else:
                print(f"文件夹名 '{item}' 不匹配正则表达式模式，跳过")
    
    print(f"找到 {len(folder_info)} 个符合条件的文件夹")
    
    # 创建结果列表
    results = []
    
    # 进行匹配
    print("正在进行匹配...")
    for folder in folder_info:
        folder_idx = folder['folder_index']
        
        # 在CSV数据中查找匹配的source_index
        matched_rows = csv_data[csv_data['source_index'] == folder_idx]
        
        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                results.append({
                    'source_index': row['source_index'],
                    'nearest_commonname': row['nearest_commonname'],
                    'folder_name': folder['folder_name'],
                    'folder_path': folder['folder_path']
                })
    
    # 转换为DataFrame
    if results:
        result_df = pd.DataFrame(results)
        
        # 保存为CSV文件
        print(f"保存结果到 {output_csv_path}...")
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"完成！共生成 {len(result_df)} 条匹配记录")
        
        return result_df
    else:
        print("没有找到任何匹配的记录")
        return None

# 使用示例
if __name__ == "__main__":
    # 替换为您的实际路径
    folder_path = r"E:\work\sv_pangpang\out\sam_tree_out"  # 要扫描的文件夹路径
    csv_file_path = r"e:\work\sv_pangpang\out\nearest_points_commonname.csv"  # CSV文件路径
    output_csv_path = r"e:\work\sv_pangpang\out\sam_tree_nearest_name.csv"  # 输出CSV文件路径
    
    # 方法1：使用下划线分割
    print("=== 方法1: 使用下划线分割 ===")
    result1 = process_folders_and_csv(folder_path, csv_file_path, output_csv_path)
    
    # 方法2：使用正则表达式（如果需要更复杂的模式）
    print("\n=== 方法2: 使用正则表达式 ===")
    # 例如：匹配 pattern_123_something 中的 123
    # result2 = process_folders_with_pattern(folder_path, csv_file_path, 
    #                                      "matched_folders_regex.csv", 
    #                                      pattern=r'_(\d+)_')


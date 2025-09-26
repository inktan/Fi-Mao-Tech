import pandas as pd
import ast
import re

def process_commonname_column(csv_file_path, output_csv_path, column_name='nearest_commonname'):
    """
    处理CSV文件中nearest_commonname列的字符串数据，去除重复元素
    
    参数:
    csv_file_path: 输入的CSV文件路径
    output_csv_path: 输出的CSV文件路径
    column_name: 要处理的列名，默认为'nearest_commonname'
    """
    
    # 读取CSV文件
    print("正在读取CSV文件...")
    try:
        df = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(df)} 行数据")
        print("列名:", df.columns.tolist())
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 检查指定的列是否存在
    if column_name not in df.columns:
        print(f"错误: 列 '{column_name}' 不存在于CSV文件中")
        print(f"可用的列: {df.columns.tolist()}")
        return
    
    # 处理每一行的数据
    print("正在处理数据...")
    
    def process_string_list(cell_value):
        """
        处理单个单元格的字符串列表数据
        """
        if pd.isna(cell_value):
            return []
        
        # 尝试多种方法解析字符串
        try:
            # 方法1: 使用ast.literal_eval安全地评估字符串
            if isinstance(cell_value, str) and cell_value.startswith('[') and cell_value.endswith(']'):
                parsed_list = ast.literal_eval(cell_value)
                if isinstance(parsed_list, list):
                    # 去除重复元素并保持顺序
                    unique_list = []
                    for item in parsed_list:
                        if item not in unique_list:
                            unique_list.append(item)
                    return unique_list
        except (ValueError, SyntaxError):
            pass
        try:
            # 方法2: 使用正则表达式提取引号内的内容
            if isinstance(cell_value, str):
                # 匹配单引号或双引号内的内容
                matches = re.findall(r"['\"]([^'\"]+)['\"]", cell_value)
                if matches:
                    # 去除重复元素并保持顺序
                    unique_list = []
                    for item in matches:
                        if item not in unique_list:
                            unique_list.append(item)
                    return unique_list
        except:
            pass
        
        # 方法3: 如果以上方法都失败，返回原始值
        return cell_value
    
    # 应用处理函数
    df['processed_commonname'] = df[column_name].apply(process_string_list)
    
    # 创建新的DataFrame，只保留处理后的列和其他需要的列
    # 可以选择保留所有原始列，或者只保留需要的列
    result_df = df.copy()
    result_df['unique_commonnames'] = result_df['processed_commonname']
    
    # 删除临时列
    result_df = result_df.drop('processed_commonname', axis=1)
    
    # 保存为新的CSV文件
    print(f"保存结果到 {output_csv_path}...")
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    
    # 显示处理前后的对比
    print("\n处理前后对比示例:")
    for i in range(min(3, len(df))):
        print(f"行 {i}:")
        print(f"  原始: {df[column_name].iloc[i]}")
        print(f"  处理后: {result_df['unique_commonnames'].iloc[i]}")
        print()
    
    print(f"完成！共处理了 {len(df)} 行数据")
    return result_df

def alternative_method(csv_file_path, output_csv_path, column_name='nearest_commonname'):
    """
    另一种处理方法：使用更简单的字符串分割
    """
    
    # 读取CSV文件
    print("使用替代方法读取CSV文件...")
    try:
        df = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(df)} 行数据")
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    def simple_process(cell_value):
        """
        使用简单的字符串处理方法
        """
        if pd.isna(cell_value) or not isinstance(cell_value, str):
            return []
        
        # 去除两端的方括号
        clean_str = cell_value.strip().strip('[]')
        
        # 分割字符串
        items = []
        current_item = ""
        in_quotes = False
        quote_char = None
        
        for char in clean_str:
            if char in ["'", '"']:
                if in_quotes and char == quote_char:
                    # 结束引号
                    items.append(current_item)
                    current_item = ""
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    # 开始引号
                    in_quotes = True
                    quote_char = char
                else:
                    current_item += char
            elif char == ',' and not in_quotes:
                # 分隔符，不在引号内
                if current_item.strip():
                    items.append(current_item.strip())
                current_item = ""
            else:
                current_item += char
        
        # 添加最后一个项目
        if current_item.strip():
            items.append(current_item.strip())
        
        # 去除每个项目两端的空格和可能的引号
        cleaned_items = []
        for item in items:
            item = item.strip()
            if (item.startswith("'") and item.endswith("'")) or \
               (item.startswith('"') and item.endswith('"')):
                item = item[1:-1]
            cleaned_items.append(item)
        
        # 去除重复并保持顺序
        unique_items = []
        for item in cleaned_items:
            if item not in unique_items:
                unique_items.append(item)
        
        return unique_items
    
    # 应用处理函数
    df['unique_commonnames'] = df[column_name].apply(simple_process)
    
    # 保存结果
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"替代方法完成！结果保存到 {output_csv_path}")
    
    return df

# 使用示例
if __name__ == "__main__":
    # 替换为您的实际路径
    output_csv_path = r"e:\work\sv_pangpang\out\sam_tree_nearest_name02.csv"  # 输入的CSV文件路径
    input_csv_path = r"e:\work\sv_pangpang\out\sam_tree_nearest_name.csv"  # 输出的CSV文件路径
    
    # 方法1：主要方法
    print("=== 方法1: 主要处理方法 ===")
    result1 = process_commonname_column(input_csv_path, output_csv_path)
    
    # 如果方法1不成功，尝试方法2
    if result1 is None or len(result1) == 0:
        print("\n=== 方法2: 替代处理方法 ===")
        result2 = alternative_method(input_csv_path, "processed_commonnames_alt.csv")
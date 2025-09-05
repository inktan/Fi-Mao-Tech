import pandas as pd
import re
from chardet import detect

def detect_encoding(file_path):
    """自动检测文件编码"""
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  # 读取前10000字节用于检测
    return detect(rawdata)['encoding']

def keep_chinese(text):
    """只保留汉字（包括扩展汉字和标点）"""
    if pd.isna(text):
        return text
    # 匹配汉字、中文标点和间隔号
    chinese_pattern = re.compile(
        r'[^\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff'
        r'\u3001-\u303f\uff01-\uff60\u2018\u2019\u201c\u201d·]'
    )
    return chinese_pattern.sub('', str(text))

def process_file(input_file, output_file):
    # 1. 检测文件编码
    try:
        encoding = detect_encoding(input_file)
        print(f"检测到文件编码: {encoding}")
        
        # 2. 读取文件
        df = pd.read_csv(input_file, encoding=encoding)
        
        # 3. 检查地点列是否存在
        if '地点' not in df.columns:
            raise ValueError("CSV文件中必须包含'地点'列")
        
        # 4. 备份原始列
        df['原始地点'] = df['地点']
        
        # 5. 清洗数据
        df['地点'] = df['地点'].apply(keep_chinese)
        
        # 6. 保存结果（使用UTF-8带BOM编码）
        df.to_csv(output_file, index=False, encoding='utf_8_sig')
        print(f"处理完成！已保存为: {output_file}")
        
        # 7. 显示处理样例
        print("\n处理样例：")
        for i in range(min(3, len(df))):
            print(f"前: {df['原始地点'].iloc[i]} \t→ 后: {df['地点'].iloc[i]}")
            
        return df
    
    except Exception as e:
        print(f"处理失败: {str(e)}")
        raise

# 使用示例
input_csv = r"e:\work\sv_xiufenganning\20250819\类别情感-逐地点统计.csv"  # 替换为你的输入文件路径

output_csv = input_csv.replace('.csv', '_cleaned.csv')

# 执行处理
try:
    processed_df = process_file(input_csv, output_csv)
except Exception as e:
    print(f"最终错误: {e}")
    print("建议解决方案：")
    print("1. 检查文件是否被其他程序占用")
    print("2. 尝试手动指定编码，如'gbk'或'gb18030'")
    print("3. 检查文件路径是否正确")

    
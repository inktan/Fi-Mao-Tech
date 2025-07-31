import pandas as pd
import json
import chardet

def detect_encoding(file_path, sample_size=1024):
    """自动检测文件编码"""
    with open(file_path, 'rb') as f:
        rawdata = f.read(sample_size)
    return chardet.detect(rawdata)['encoding']

def safe_read_csv(file_path):
    """安全读取CSV文件，自动处理编码问题"""
    # 尝试常见中文编码
    encodings_to_try = ['utf-8', 'gbk', 'utf-8-sig', 'gb18030', 'big5']
    
    # 先尝试自动检测编码
    try:
        detected_encoding = detect_encoding(file_path)
        if detected_encoding:
            encodings_to_try.insert(0, detected_encoding)
    except:
        pass
    
    # 尝试各种编码
    for encoding in encodings_to_try:
        try:
            # 使用更安全的读取方式，只读取前5行
            # df = pd.read_csv(file_path, encoding=encoding, nrows=5)
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"成功使用编码: {encoding}")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"编码 {encoding} 尝试失败: {str(e)}")
            continue
    
    # 如果所有编码都失败，尝试二进制模式读取
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            # 尝试去除可能的BOM头
            for bom in [b'\xef\xbb\xbf', b'\xff\xfe', b'\xfe\xff']:
                if content.startswith(bom):
                    content = content[len(bom):]
                    break
            # 再次尝试检测编码
            detected_encoding = chardet.detect(content)['encoding']
            if detected_encoding:
                df = pd.read_csv(pd.compat.BytesIO(content), encoding=detected_encoding, nrows=5)
                print(f"成功使用检测到的编码: {detected_encoding}")
                return df
    except Exception as e:
        print(f"最终尝试失败: {str(e)}")
    
    raise ValueError("无法确定文件编码，请手动指定正确的编码")

# 使用示例
file_path = r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial_infos.csv'  # 替换为你的实际文件路径

try:
    # 读取文件前5行
    df = safe_read_csv(file_path)

    # 输出结果
    # print("\n文件前5行内容:")
    print(df.head())
    # print(df)
    print(df.columns.to_list())
    print(df.shape)
    # print(df.iloc[:1, :1])  # 

    # for i in range(15):
    #     print(df.iloc[i, 0])
    
    # first_element = df.values[0, 0]
    print(df.values[0, 0])
    # print(df.values[0, 1])
    # print(df.values[1, 0])
    # print(df.values[2, 0])
    # print(df.values[3, 0])
    
    # 尝试美观输出
    # try:
    #     from tabulate import tabulate
    #     print("\n美观格式输出:")
    #     print(tabulate(df.head(), headers='keys', tablefmt='grid', showindex=False))
    # except ImportError:
    #     print("\n(安装tabulate库可以获得更美观的输出格式: pip install tabulate)")
    #     print(df.head())
        
except Exception as e:
    print(f"读取文件失败: {str(e)}")
    print("建议尝试以下方法:")
    print("1. 用文本编辑器(如Notepad++)检查文件实际编码")
    print("2. 尝试其他编码如 'gb18030'、'big5' 或 'latin1'")
    print("3. 检查文件是否损坏或不完整")

    
import pandas as pd
from coord_convert.transform import gcj2wgs

def convert_coordinates(input_file, output_file, lon_col='lon', lat_col='lat', new_lon_col='lon_wgs', new_lat_col='lat_wgs'):
    """
    将CSV文件中的GCJ-02坐标转换为WGS-84坐标
    
    参数:
    input_file (str): 输入CSV文件路径
    output_file (str): 输出CSV文件路径
    lon_col (str): 输入文件中经度列的名称，默认为'lon'
    lat_col (str): 输入文件中纬度列的名称，默认为'lat'
    new_lon_col (str): 输出文件中转换后的经度列的名称，默认为'lon_wgs'
    new_lat_col (str): 输出文件中转换后的纬度列的名称，默认为'lat_wgs'
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(input_file)
        
        # 检查经纬度列是否存在
        if lon_col not in df.columns or lat_col not in df.columns:
            raise ValueError(f"输入文件中找不到指定的列: {lon_col} 或 {lat_col}")
        
        # 应用坐标转换函数
        print("正在进行坐标转换...")
        df[[new_lon_col, new_lat_col]] = df.apply(
            lambda row: pd.Series(gcj2wgs(float(row[lon_col]), float(row[lat_col]))), 
            axis=1
        )
        
        # 保存转换后的DataFrame到新的CSV文件
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"坐标转换完成，结果已保存至: {output_file}")
        print(f"共转换了 {len(df)} 条记录")
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 - {input_file}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 示例使用
    INPUT_FILE = r'e:\work\sv_xiufenganning\文本分析\work\points_gcj02.csv'    # 替换为你的输入文件路径
    OUTPUT_FILE = r'e:\work\sv_xiufenganning\文本分析\work\points_wgs84.csv'  # 替换为你的输出文件路径
    
    convert_coordinates(INPUT_FILE, OUTPUT_FILE)
    
    # 如果你需要自定义列名，可以这样调用:
    # convert_coordinates(
    #     input_file='your_data.csv',
    #     output_file='converted_data.csv',
    #     lon_col='longitude',
    #     lat_col='latitude',
    #     new_lon_col='wgs_longitude',
    #     new_lat_col='wgs_latitude'
    # )    
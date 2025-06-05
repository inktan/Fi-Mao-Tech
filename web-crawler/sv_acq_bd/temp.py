import os
import pandas as pd

def check_file_matches(csv_path, directory_path):
    """
    检查CSV数据与目录中文件的匹配情况
    
    参数:
        csv_path (str): CSV文件路径
        directory_path (str): 要检查的目录路径
        
    返回:
        tuple: (不匹配的行DataFrame, 只匹配一个文件的行DataFrame)
    """
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    
    # 获取目录中所有文件名
    all_files = set(os.listdir(directory_path))
    
    # 创建合并的字符串列
    df['combined'] = df['Id'].astype(str) + '_' + \
                     df['ORIG_FID'].astype(str) + '_' + \
                     df['lon'].astype(str) + '_' + \
                     df['lat'].astype(str)
    
    single_match_rows = []
    
    # 检查每一行
    for index, row in df.iterrows():
        prefix = row['combined']
        # 查找匹配的文件
        matched_files = [f for f in all_files if f.startswith(prefix)]
        
        if len(matched_files) == 1:
            single_match_rows.append(row)
    
    # 转换为DataFrame
    single_match_df = pd.DataFrame(single_match_rows)
    
    return single_match_df

# 使用示例
if __name__ == "__main__":
    csv_path = r'd:\work\sv\points_50m.csv'  # 替换为你的CSV文件路径
    directory_path = r'D:\work\sv\sv_degrees\90°广角1000x500'  # 替换为你的文件目录路径
    
    single_match = check_file_matches(csv_path, directory_path)
    
    print("\n只匹配一个文件的行:")
    print(single_match)
    
    # 可选：将结果保存到文件
    single_match.to_csv(r'd:\work\sv\single_match_files.csv', index=False)



    
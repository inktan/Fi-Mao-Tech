import os
import pandas as pd

def split_csv_into_chunks(csv_file, num_chunks=24):
    """
    将CSV文件按行数大致平均分割成指定份数，并保存到新文件夹
    
    参数:
    csv_file (str): 原始CSV文件路径
    num_chunks (int): 需要分割的份数，默认为24
    """
    
    # 读取原始CSV文件
    df = pd.read_csv(csv_file)
    total_rows = len(df)
    
    # 计算每份的大致行数
    chunk_size = total_rows // num_chunks
    # 如果行数不能整除，最后一份会包含剩余行数
    remainder = total_rows % num_chunks
    
    # 创建目标文件夹
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_dir = f"{base_name}_chunks"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"原始文件总行数: {total_rows}")
    print(f"计划分割成{num_chunks}份，每份大约{chunk_size}行")
    print(f"输出目录: {output_dir}")
    
    # 分割并保存文件
    for i in range(num_chunks):
        start_idx = i * chunk_size
        # 如果是最后一份，包含剩余所有行
        if i == num_chunks - 1:
            end_idx = total_rows  # 包含到最后一行
        else:
            end_idx = start_idx + chunk_size
        
        # 提取数据块
        chunk_df = df.iloc[start_idx:end_idx]
        
        # 生成输出文件名
        output_file = os.path.join(output_dir, f"{base_name}_chunk_{i+1:02d}.csv")
        
        # 保存CSV文件（不包含索引）
        chunk_df.to_csv(output_file, index=False)
        print(f"已保存: {output_file} (行数: {len(chunk_df)})")
    
    print(f"\n分割完成！所有文件已保存到 '{output_dir}' 文件夹")

# 使用示例
if __name__ == "__main__":
    # 替换为你的CSV文件路径
    csv_file_path = "your_large_file.csv"  # 修改为实际文件路径
    
    # 调用函数分割文件
    split_csv_into_chunks(csv_file_path, num_chunks=24)
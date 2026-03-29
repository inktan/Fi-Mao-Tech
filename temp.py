import os
import pandas as pd

def validate_csv_format():
    # 1. 定义要检查的根文件夹路径
    root_folder = r"F:\osm\分城市的道路数据_50m_point_csv"

    # 2. 检查根路径是否存在
    if not os.path.isdir(root_folder):
        print(f"错误：文件夹 '{root_folder}' 不存在或不是一个有效的目录。")
        return

    print(f"正在检查 '{root_folder}' 中的CSV文件格式...")

    # 3. 定义预期的列名
    expected_columns = ['osm_id', 'longitude', 'latitude', 'index']

    # 4. 使用 os.walk 遍历所有子文件夹和文件
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    # 5. 读取CSV文件并检查列名
                    df = pd.read_csv(file_path, nrows=0)  # 只读取列名，提高效率
                    if list(df.columns) != expected_columns:
                        print(f"格式不匹配: {file_path}")
                except Exception as e:
                    # 如果读取文件时出错（例如，文件为空或损坏），也打印路径
                    print(f"无法读取或格式错误: {file_path} (错误: {e})")

# 执行函数
if __name__ == "__main__":
    validate_csv_format()
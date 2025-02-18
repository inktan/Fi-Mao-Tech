import csv
import pandas as pd
import os

def csv_to_xlsx(csv_file_path, xlsx_file_path):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path, encoding='GBK')
    # 将 DataFrame 写入 XLSX 文件
    df.to_excel(xlsx_file_path, index=False)
    print(f"转换完成，结果已保存到 {xlsx_file_path}")

csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_folder_list =[
    r'E:\work\sv_juanjuanmao\指标计算\业态混合度',
    ]
for folder_path in csv_path_folder_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)

for file_path in csv_paths:
    
    # 示例使用
    csv_file_path = file_path
    xlsx_file_path = file_path.replace('.csv', '.xlsx')

    csv_to_xlsx(csv_file_path, xlsx_file_path)

import pandas as pd
import os

def excel_to_csv(excel_file):
    try:
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        for sheet_name in sheet_names:
            df = xls.parse(sheet_name)
            csv_file = f"{os.path.splitext(excel_file)[0]}_{sheet_name}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Sheet '{sheet_name}' 已转换为 CSV 文件: {csv_file}")
        print(f"Excel 文件 '{excel_file}' 转换完成。")
    except FileNotFoundError:
        print(f"错误: Excel 文件 '{excel_file}' 未找到。")
    except Exception as e:
        print(f"发生错误: {e}")
# 示例用法
excel_file = r"e:\work\sv_juanjuanmao\20250308\吸引力数据\8条路线吸引力poi清单0307.xlsx"  # 替换为你的 Excel 文件路径
excel_to_csv(excel_file)






import pandas as pd

# 假设文件名为 'your_file.xlsx'
file_name = r"e:\work\sv_shushu\谷歌\score.xlsx"

# 使用pandas的ExcelFile类来读取xlsx文件
with pd.ExcelFile(file_name) as xls:
    # 遍历所有工作表
    for sheet_name in xls.sheet_names:
        # 读取每个工作表
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # 打印工作表名
        # print(f"工作表：{sheet_name}")
        # 打印每个工作表的前两列的前三行
        # print(df.iloc[:, :2].head(3))
        df = df.iloc[:, :2]
        df.to_csv(f"e:\work\sv_shushu\谷歌\{sheet_name}.csv", index=False)
        print(df.shape)
        print(type(df))
        # print("\n")  # 打印空行以分隔不同工作表的内容

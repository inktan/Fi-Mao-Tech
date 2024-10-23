import pandas as pd

categories = ['beautiful','boring','depressing','lively','safety','wealthy']
for category in categories:

    # 读取CSV文件
    csv_path = f'e:\work\sv_levon\{category}.csv'
    df = pd.read_csv(csv_path)

    column_to_map = category
    data = df[column_to_map]
    min_val = data.min()
    max_val = data.max()

    df[column_to_map] = (data - min_val) / (max_val - min_val) * 100
    df.to_csv(csv_path, index=False)
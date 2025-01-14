import pandas as pd

categories = ['beautiful','boring','depressing','lively','safety','wealthy']

for category in categories:
    # category = 'wealthy'
    # 假设df是你的DataFrame，且有一个名为'id'的列
    df = pd.read_csv(f'E:\work\sv_levon/folder-01\sv_hor_2017_{category}.csv')
    print(df)

    # 替换非数字值为NaN
    df[category] = pd.to_numeric(df[category], errors='coerce')
    # 将id列的数据类型转换为float
    df[category] = df[category].astype(float)
    # 假设id列中的数据是整数，并且最小值是min_id，最大值是max_id
    min_id = df[category].min()
    max_id = df[category].max()

    # 线性映射函数：将数据从原始区间映射到 10-90 的新区间
    def scale_to_range(series, new_min=0, new_max=100):
        old_min = series.min()
        old_max = series.max()
        return new_min + (series - old_min) * (new_max - new_min) / (old_max - old_min)

    # 将 id 列映射到 10-90
    df[category] = scale_to_range(df[category])

    # 保存为新的CSV文件
    output_file = f'E:\work\sv_levon/folder-01\sv_hor_2017_{category}_0.csv'
    df.to_csv(output_file, index=False)

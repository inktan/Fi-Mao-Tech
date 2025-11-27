import pandas as pd

csv_paths = [
    r'f:\大数据\2025年华北地区poi数据\北京市\北京市.csv',
    ]
                
for csv_path in csv_paths:
    # 读取CSV文件

    df = pd.read_csv(csv_path)  # 替换为您的文件路径

    # 查询"大类"列的唯一值
    unique_categories = df['中类'].unique()

    # 输出结果
    print(f"唯一值数量: {len(unique_categories)}")
    print("唯一值内容:")
    for i, category in enumerate(unique_categories, 1):
        print(f"{i}. {category}")

    # 可选：按字母顺序排序输出
    print("\n按字母顺序排序:")
    sorted_categories = sorted(unique_categories)
    for i, category in enumerate(sorted_categories, 1):
        print(f"{i}. {category}")

    # 筛选"中类"为"住宅区"的数据并显示前10行
    filtered_data = df[df['中类'] == '住宅区'].head(10)

    print(f"找到 {len(filtered_data)} 行数据（最多显示10行）")
    print("=" * 50)

    # 显示所有列
    pd.set_option('display.max_columns', None)  # 显示所有列
    print(filtered_data)

    # 或者只显示部分重要列
    print("\n重要列信息:")
    print(filtered_data[['中类', '小类', '名称']])  # 根据需要调整列名
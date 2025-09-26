import pandas as pd

# 简洁版差集查找
def simple_csv_difference(file1, file2):
    """
    简洁版：找出file1中有但file2中没有的记录
    """
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # 使用merge找出差集
    merged = df1.merge(df2, on=['longitude', 'latitude'], how='left', indicator=True)
    difference = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
    
    print(f"文件1记录数: {len(df1)}")
    print(f"文件2记录数: {len(df2)}")
    print(f"差集记录数: {len(difference)}")
    print("\n差集数据预览:")
    print(difference.head())
    
    return difference

# 使用示例
result = simple_csv_difference(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_7.5m_unique.csv', 
                               r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique.csv')
result.to_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_7.5_ifference_15.csv', index=False)




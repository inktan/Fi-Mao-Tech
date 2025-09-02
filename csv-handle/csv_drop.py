import pandas as pd

# 读取两个 CSV 文件
df1 = pd.read_csv(r"f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique.csv")  # 替换为你的文件路径
df2 = pd.read_csv(r"f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_Spatial.csv")  # 替换为你的文件路径

# 合并两个 DataFrame，基于 longitude 和 latitude 列
merged = df1.merge(
    df2,
    on=["longitude", "latitude"],
    how="left",  # 左连接（保留 df1 的所有行）
    indicator=True  # 添加 _merge 列标记来源
)

# 筛选出仅在 df1 中存在的行（不在 df2 中的行）
result = merged[merged["_merge"] == "left_only"].drop(columns="_merge")

# 保存为新的 CSV 文件
result.to_csv(r"f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_Spatial01.csv", index=False)

print("处理完成，结果已保存为 unique_to_file1.csv")




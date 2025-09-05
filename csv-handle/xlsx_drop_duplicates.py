import pandas as pd

# 读取Excel文件
file_path = r"e:\work\sv_xiufenganning\20250815\类别情感05.xlsx"  # 替换为你的文件路径
df = pd.read_excel(file_path)

# 检查是否存在lon和lat列
if not all(col in df.columns for col in ['lon', 'lat']):
    raise ValueError("数据中必须包含lon和lat列")

# 基于lon和lat进行去重（保留第一个出现的记录）
deduplicated_df = df.drop_duplicates(subset=['lon', 'lat'], keep='first')

# 可选：重置索引（不保留原来的行号）
deduplicated_df = deduplicated_df.reset_index(drop=True)

# 保存去重后的数据
output_path =  r"e:\work\sv_xiufenganning\20250815\类别情感06.xlsx" 
deduplicated_df.to_excel(output_path, index=False)

print(f"去重完成！原始数据{len(df)}条，去重后{len(deduplicated_df)}条")
print("前5条去重后的数据：")
print(deduplicated_df.head())
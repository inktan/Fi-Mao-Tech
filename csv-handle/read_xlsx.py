
import re
import pandas as pd
file_path = r"e:\work\sv_xiufenganning\20250815\类别情感06.xlsx"  # 请将此处替换为实际的文件路径
df = pd.read_excel(file_path)

# 定义各感知度分类对应的列
category_columns = {
    "文化感知": ["历史", "艺术/文学", "建筑", "跨文化"],
    "自然感知": ["人工景观", "自然景观", "动物"],
    "娱乐感知": ["活动", "设施/场地", "饮食"],
    "现代化感知度": ["技术", "商业"],
    "人际情感感知度": ["友情", "爱情", "亲子"],
    "科教感知度": ["高校", "知识与成长"]
}

# 检查所有需要的列是否都存在
missing_columns = []
for cols in category_columns.values():
    for col in cols:
        if col not in df.columns:
            missing_columns.append(col)

if missing_columns:
    raise ValueError(f"数据中缺少以下列: {missing_columns}")

# 计算各感知度总和
for category, columns in category_columns.items():
    df[category] = df[columns].sum(axis=1)

print(df.head())

# 保存处理后的数据（可选）
output_path = r"e:\work\sv_xiufenganning\20250815\类别情感07.xlsx" 
df.to_excel(output_path, index=False)

print("数据处理完成！")
print(df.head())  # 显示前几行数据
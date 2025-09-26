import pandas as pd
import numpy as np

# 定义因变量和自变量
dependent_vars = ['建筑', '历史', '异域文化', '景观', '艺术', '娱乐', '饮食', '亲子', '购物', '科技', '高校', '科普与素养']
independent_vars = ['Green', 'Sky', 'River', 'BLR', 'ID', 'PubArt', 'Arch', 'Histor', 'Faccon', 'Block', 'FacCol']

# 构建模拟相关系数矩阵
data = np.zeros((len(independent_vars), len(dependent_vars)))
data[0] = [0.3, 0, 0, 0.8, 0.3, 0.8, 0, 0.5, 0, 0, 0.5, -0.3]
data[1] = [-0.3, 0.3, 0, 0.3, 0, 0.3, 0, 0.3, 0, 0, 0, 0]
data[2] = [0, 0.3, 0, 0.8, 0.5, 0.3, 0, 0.3, 0, 0, 0.3, 0]
data[3] = [-0.3, -0.5, -0.3, -0.5, -0.8, -0.8, 0, 0, 0, 0.5, 0, 0]
data[4] = [-0.5, -0.5, -0.3, -0.8, -0.8, -0.5, 0, 0, 0, 0, 0, 0]
data[5] = [0.3, 0, 0.3, 0.3, 0.8, 0.3, 0.3, 0.5, 0.5, -0.3, 0, 0]
data[6] = [0, -0.5, -0.5, -0.3, -0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0, 0.3]
data[7] = [0.5, 0.8, 0.5, 0.3, 0.5, 0.3, 0, 0.5, 0.3, -0.8, 0.3, 0]
data[8] = [0.5, 0.3, 0.3, 0, 0.8, 0.5, 0.5, 0.3, 0, 0.3, 0.3, 0]
data[9] = [0.5, 0.5, 0.5, 0.3, 0.5, 0.5, 0, 0.3, 0.3, 0, 0, 0]
data[10] = [0.3, 0.5, 0.5, 0, 0.3, 0.8, 0, 0, 0.3, 0, 0, 0]

df = pd.DataFrame(data, index=independent_vars, columns=dependent_vars)

# 计算每个因变量的最佳预测变量和重要性排名
best_predictors = {}
ranking_results = {}

for col in df.columns:
    abs_corrs = df[col].abs()
    sorted_indices = abs_corrs.sort_values(ascending=False).index
    best_predictors[col] = sorted_indices[0]
    ranking_results[col] = list(sorted_indices)

# 输出结果
print("模拟的皮尔逊相关系数矩阵：")
print(df.round(2))

print("\n各因变量的最佳预测变量：")
for dep_var, predictor in best_predictors.items():
    print(f"{dep_var}: {predictor}")

print("\n各因变量的预测变量重要性排名（基于相关系数绝对值）：")
for dep_var, predictors in ranking_results.items():
    print(f"{dep_var}: {predictors}")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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

# 1. 完整热力图 - 所有相关性
plt.figure(figsize=(14, 10))
sns.heatmap(df, annot=True, cmap='RdBu_r', center=0, fmt='.2f', 
            cbar_kws={'label': '相关系数'})
plt.title('皮尔逊相关系数热力图 - 完整视图', fontsize=16, pad=20)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('correlation_heatmap_full.png', dpi=300, bbox_inches='tight')
plt.savefig('correlation_heatmap_full.pdf', bbox_inches='tight')
plt.close()

# 2. 显著相关性热力图 - 只显示绝对值大于0.3的相关性
plt.figure(figsize=(14, 10))
mask = np.abs(df) < 0.3  # 创建掩码，隐藏绝对值小于0.3的值
sns.heatmap(df, annot=True, cmap='RdBu_r', center=0, fmt='.2f', 
            mask=mask, cbar_kws={'label': '相关系数'})
plt.title('皮尔逊相关系数热力图 - 显著相关性 (|r| ≥ 0.3)', fontsize=16, pad=20)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('correlation_heatmap_significant.png', dpi=300, bbox_inches='tight')
plt.savefig('correlation_heatmap_significant.pdf', bbox_inches='tight')
plt.close()

# 3. 各因变量的最佳预测变量条形图
plt.figure(figsize=(16, 8))
best_predictors = {}
best_correlations = {}

for col in df.columns:
    abs_corrs = df[col].abs()
    best_idx = abs_corrs.idxmax()
    best_predictors[col] = best_idx
    best_correlations[col] = df.loc[best_idx, col]

# 创建条形图数据
predictor_names = list(best_predictors.values())
correlation_values = list(best_correlations.values())
dep_vars = list(best_predictors.keys())

colors = ['red' if x < 0 else 'blue' for x in correlation_values]

bars = plt.bar(range(len(dep_vars)), correlation_values, color=colors, alpha=0.7)
plt.xlabel('因变量', fontsize=12)
plt.ylabel('相关系数', fontsize=12)
plt.title('各因变量的最佳预测变量及相关系数', fontsize=16, pad=20)
plt.xticks(range(len(dep_vars)), dep_vars, rotation=45, ha='right')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.grid(axis='y', alpha=0.3)

# 添加数值标签
for i, (bar, val) in enumerate(zip(bars, correlation_values)):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.05),
             f'{val:.2f}\n({predictor_names[i]})', 
             ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

plt.tight_layout()
plt.savefig('best_predictors_bar.png', dpi=300, bbox_inches='tight')
plt.savefig('best_predictors_bar.pdf', bbox_inches='tight')
plt.close()

# 4. 各预测变量的总影响力（绝对相关系数之和）
plt.figure(figsize=(12, 8))
predictor_impact = df.abs().sum(axis=1).sort_values(ascending=False)

bars = plt.bar(range(len(predictor_impact)), predictor_impact.values, 
               alpha=0.7, color='green')
plt.xlabel('预测变量', fontsize=12)
plt.ylabel('总影响力（绝对相关系数之和）', fontsize=12)
plt.title('各预测变量的总影响力排名', fontsize=16, pad=20)
plt.xticks(range(len(predictor_impact)), predictor_impact.index, 
           rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)

# 添加数值标签
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('predictor_impact_ranking.png', dpi=300, bbox_inches='tight')
plt.savefig('predictor_impact_ranking.pdf', bbox_inches='tight')
plt.close()

# 5. 相关性强度分布饼图
plt.figure(figsize=(10, 8))
corr_strength = {
    '强正相关 (r ≥ 0.7)': (df >= 0.7).sum().sum(),
    '中等正相关 (0.3 ≤ r < 0.7)': ((df >= 0.3) & (df < 0.7)).sum().sum(),
    '弱正相关 (0 < r < 0.3)': ((df > 0) & (df < 0.3)).sum().sum(),
    '无相关 (r = 0)': (df == 0).sum().sum(),
    '弱负相关 (-0.3 < r < 0)': ((df < 0) & (df > -0.3)).sum().sum(),
    '中等负相关 (-0.7 < r ≤ -0.3)': ((df <= -0.3) & (df > -0.7)).sum().sum(),
    '强负相关 (r ≤ -0.7)': (df <= -0.7).sum().sum()
}

labels = list(corr_strength.keys())
sizes = list(corr_strength.values())
colors = ['#FF6B6B', '#FFA8A8', '#FFD3D3', '#E0E0E0', '#D3E0FF', '#A8C6FF', '#6B8CFF']

plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.axis('equal')
plt.title('相关性强度分布', fontsize=16, pad=20)
plt.tight_layout()
plt.savefig('correlation_strength_distribution.png', dpi=300, bbox_inches='tight')
plt.savefig('correlation_strength_distribution.pdf', bbox_inches='tight')
plt.close()

# 6. 最强相关性关系图（前10个）
plt.figure(figsize=(12, 8))
all_correlations = []
for i in range(len(independent_vars)):
    for j in range(len(dependent_vars)):
        corr_value = df.iloc[i, j]
        if abs(corr_value) >= 0.3:  # 只显示显著相关性
            all_correlations.append((independent_vars[i], dependent_vars[j], corr_value))

# 按绝对值排序取前10
top_10 = sorted(all_correlations, key=lambda x: abs(x[2]), reverse=True)[:10]

# 准备数据
relationships = [f"{x[0]} - {x[1]}" for x in top_10]
values = [x[2] for x in top_10]
colors = ['red' if x < 0 else 'blue' for x in values]

plt.barh(relationships, values, color=colors, alpha=0.7)
plt.xlabel('相关系数')
plt.title('最强相关性关系排名（前10）', fontsize=16, pad=20)
plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('top_correlations_ranking.png', dpi=300, bbox_inches='tight')
plt.savefig('top_correlations_ranking.pdf', bbox_inches='tight')
plt.close()

print("所有图表已保存为本地文件：")
print("1. correlation_heatmap_full.png/.pdf - 完整热力图")
print("2. correlation_heatmap_significant.png/.pdf - 显著相关性热力图")
print("3. best_predictors_bar.png/.pdf - 最佳预测变量条形图")
print("4. predictor_impact_ranking.png/.pdf - 预测变量影响力排名")
print("5. correlation_strength_distribution.png/.pdf - 相关性强度分布饼图")
print("6. top_correlations_ranking.png/.pdf - 最强相关性关系排名")
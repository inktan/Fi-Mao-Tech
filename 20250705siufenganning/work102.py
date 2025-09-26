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

# 创建图形
fig, axes = plt.subplots(2, 2, figsize=(20, 16))
fig.suptitle('相关性分析结果', fontsize=20, fontweight='bold')

# 1. 热力图 - 所有相关性
ax1 = axes[0, 0]
sns.heatmap(df, annot=True, cmap='RdBu_r', center=0, fmt='.2f', 
            ax=ax1, cbar_kws={'label': '相关系数'})
ax1.set_title('皮尔逊相关系数热力图', fontsize=16, pad=20)
ax1.tick_params(axis='x', rotation=45)
ax1.tick_params(axis='y', rotation=0)

# 2. 热力图 - 只显示绝对值大于0.3的相关性（突出显著相关）
ax2 = axes[0, 1]
mask = np.abs(df) < 0.3  # 创建掩码，隐藏绝对值小于0.3的值
sns.heatmap(df, annot=True, cmap='RdBu_r', center=0, fmt='.2f', 
            mask=mask, ax=ax2, cbar_kws={'label': '相关系数'})
ax2.set_title('显著相关性热力图 (|r| ≥ 0.3)', fontsize=16, pad=20)
ax2.tick_params(axis='x', rotation=45)
ax2.tick_params(axis='y', rotation=0)

# 3. 各因变量的最佳预测变量条形图
ax3 = axes[1, 0]
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

bars = ax3.bar(range(len(dep_vars)), correlation_values, color=colors, alpha=0.7)
ax3.set_xlabel('因变量')
ax3.set_ylabel('相关系数')
ax3.set_title('各因变量的最佳预测变量及相关系数', fontsize=16, pad=20)
ax3.set_xticks(range(len(dep_vars)))
ax3.set_xticklabels(dep_vars, rotation=45, ha='right')
ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)

# 添加数值标签
for i, (bar, val) in enumerate(zip(bars, correlation_values)):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.05),
             f'{val:.2f}\n({predictor_names[i]})', 
             ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

# 4. 各预测变量的总影响力（绝对相关系数之和）
ax4 = axes[1, 1]
predictor_impact = df.abs().sum(axis=1).sort_values(ascending=False)

bars = ax4.bar(range(len(predictor_impact)), predictor_impact.values, alpha=0.7)
ax4.set_xlabel('预测变量')
ax4.set_ylabel('总影响力（绝对相关系数之和）')
ax4.set_title('各预测变量的总影响力排名', fontsize=16, pad=20)
ax4.set_xticks(range(len(predictor_impact)))
ax4.set_xticklabels(predictor_impact.index, rotation=45, ha='right')

# 添加数值标签
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:.2f}', ha='center', va='bottom')

plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.show()

# 输出详细分析结果
print("=" * 60)
print("相关性分析详细结果")
print("=" * 60)

# 计算每个因变量的最佳预测变量和排名
print("\n各因变量的最佳预测变量：")
for dep_var in dependent_vars:
    corrs = df[dep_var]
    abs_corrs = corrs.abs()
    best_predictor = abs_corrs.idxmax()
    best_corr = corrs[best_predictor]
    print(f"{dep_var}: {best_predictor} (r = {best_corr:.2f})")

print("\n" + "=" * 60)
print("最强正相关关系：")
strong_positive = []
for i in range(len(independent_vars)):
    for j in range(len(dependent_vars)):
        if df.iloc[i, j] >= 0.7:
            strong_positive.append((independent_vars[i], dependent_vars[j], df.iloc[i, j]))

for rel in sorted(strong_positive, key=lambda x: x[2], reverse=True):
    print(f"{rel[0]} - {rel[1]}: r = {rel[2]:.2f}")

print("\n最强负相关关系：")
strong_negative = []
for i in range(len(independent_vars)):
    for j in range(len(dependent_vars)):
        if df.iloc[i, j] <= -0.7:
            strong_negative.append((independent_vars[i], dependent_vars[j], df.iloc[i, j]))

for rel in sorted(strong_negative, key=lambda x: x[2]):
    print(f"{rel[0]} - {rel[1]}: r = {rel[2]:.2f}")

# 创建相关性强度统计
corr_strength = {
    '强正相关 (r ≥ 0.7)': (df >= 0.7).sum().sum(),
    '中等正相关 (0.3 ≤ r < 0.7)': ((df >= 0.3) & (df < 0.7)).sum().sum(),
    '弱正相关 (0 < r < 0.3)': ((df > 0) & (df < 0.3)).sum().sum(),
    '无相关 (r = 0)': (df == 0).sum().sum(),
    '弱负相关 (-0.3 < r < 0)': ((df < 0) & (df > -0.3)).sum().sum(),
    '中等负相关 (-0.7 < r ≤ -0.3)': ((df <= -0.3) & (df > -0.7)).sum().sum(),
    '强负相关 (r ≤ -0.7)': (df <= -0.7).sum().sum()
}

print("\n" + "=" * 60)
print("相关性强度统计：")
for strength, count in corr_strength.items():
    print(f"{strength}: {count}个关系")
import pandas as pd
import numpy as np

# 设置随机种子以保证结果可复现
np.random.seed(42)

# 1. 定义维度和因素列表
dimensions = ['Green', 'Sky', 'River', 'BLR', 'ID', 'PubArt', 'Arch', 'Histor', 'Faccon', 'Block', 'FacCol']
factors = ['建筑', '历史', '异域文化', '景观', '艺术', '娱乐', '饮食', '亲子', '购物', '科技', '高校', '科普与素养']

# 2. 根据原始关联强度创建量化矩阵（高正=3, 中正=2, 弱正=1, 无关=0, 弱负=-1, 中负=-2, 高负=-3）
quant_matrix = np.array([
    [1, 0, 0, 3, 1, 3, 0, 2, 0, 0, 2, -1],  # Green
    [-1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],  # Sky
    [0, 1, 0, 3, 2, 1, 0, 1, 0, 0, 1, 0],   # River
    [-1, -2, -1, -2, -3, -3, 0, 0, 0, 2, 0, 0],  # BLR
    [-2, -2, -1, -3, -3, -2, 0, 0, 0, 0, 0, 0],  # ID
    [1, 0, 1, 1, 3, 1, 1, 2, 2, -1, 0, 0],  # PubArt
    [0, -2, -2, -1, -1, 1, 1, 1, 2, 2, 0, 1],  # Arch
    [2, 3, 2, 1, 2, 1, 0, 2, 1, -3, 1, 0],  # Histor
    [2, 1, 1, 0, 3, 2, 2, 1, 0, 1, 1, 0],  # Faccon
    [2, 2, 2, 1, 2, 2, 0, 1, 1, 0, 0, 0],  # Block
    [1, 2, 2, 0, 1, 3, 0, 0, 1, 0, 0, 0]   # FacCol
])

# 3. 生成50组样本数据（在量化值基础上添加±0.3的随机扰动）
n_samples = 50
data = []
for _ in range(n_samples):
    # 为每个维度的每个因素添加随机扰动
    noise = np.random.uniform(-0.3, 0.3, size=quant_matrix.shape)
    sample = quant_matrix + noise
    data.append(sample.flatten())

# 4. 创建DataFrame（列名：维度_因素）
columns = [f'{dim}_{fac}' for dim in dimensions for fac in factors]
df = pd.DataFrame(data, columns=columns)

# 查看前5行数据（展示数据结构）
print("分析数据前5行：")
print(df.head())

import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体为微软雅黑
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 1. 计算相关性矩阵
corr_matrix = df.corr()

# 2. 绘制相关性热力图（展示所有变量间的相关性）
plt.figure(figsize=(20, 16))
# 热力图：cmap用RdBu_r（红=正相关，蓝=负相关），标注相关系数（保留2位小数）
heatmap = sns.heatmap(
    corr_matrix,
    cmap='RdBu_r',
    center=0,
    annot=False,  # 变量过多时关闭标注，避免拥挤（如需标注可设为True）
    fmt='.2f',
    linewidths=0.5,
    cbar_kws={'shrink': 0.8}
)
plt.title('各维度-因素组合的相关性热力图', fontsize=16, pad=20)
plt.xlabel('维度-因素', fontsize=12)
plt.ylabel('维度-因素', fontsize=12)
# 旋转x轴标签以避免重叠
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. 提取关键维度与因素的相关性（以“景观”“艺术”“饮食”为例）
key_factors = ['景观', '艺术', '饮食']
key_data = df[[col for col in df.columns if any(fac in col for fac in key_factors)]]
key_corr = key_data.corr()

# 绘制关键因素的相关性热力图（带标注）
plt.figure(figsize=(12, 10))
sns.heatmap(
    key_corr,
    cmap='RdBu_r',
    center=0,
    annot=True,
    fmt='.2f',
    linewidths=0.5,
    cbar_kws={'shrink': 0.8}
)
plt.title('关键因素（景观、艺术、饮食）相关维度的相关性热力图', fontsize=14, pad=15)
plt.xlabel('维度-关键因素', fontsize=12)
plt.ylabel('维度-关键因素', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('key_factors_correlation.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. 输出关键相关性数据（展示Top10正相关和Top10负相关）
# 筛选非对角线元素（排除自身相关）
corr_vals = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
corr_vals = corr_vals.stack().reset_index()
corr_vals.columns = ['变量1', '变量2', '相关系数']

# 按相关系数排序
positive_corr = corr_vals.sort_values('相关系数', ascending=False).head(10)
negative_corr = corr_vals.sort_values('相关系数').head(10)

print("\nTop10正相关组合：")
print(positive_corr)
print("\nTop10负相关组合：")
print(negative_corr)
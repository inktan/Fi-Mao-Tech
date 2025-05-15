import numpy as np
import pysal as ps
from pysal.model import spreg
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from libpysal.weights import KNN
from spreg import ML_Lag

# 1. 数据加载与预处理
gdf = gpd.read_file(r"e:\work\sv_juanjuanmao\20250308\八条路线\T8_50m_SEG_ssindicators04.shp")

# 2. 只保留显著变量（根据之前结果）
selected_features = ['ashcan', 'poster', 'green', 'sky', 'window', 'chair', 'OpenSocial', 'shop', 'h_value', 'traffic']  # 只保留显著变量
y = gdf['attraction'].values.reshape(-1, 1)  # 确保y是二维数组

# 3. 数据标准化
scaler = MinMaxScaler(feature_range=(0, 1))
X = scaler.fit_transform(gdf[selected_features])
y = scaler.fit_transform(y).flatten()  # 对y也进行标准化

# 4. 改进权重矩阵构建
# 使用KNN并检查连通性
k = 2  # 增加邻居数量以确保连通性
W = KNN.from_dataframe(gdf, k=k)

slm = ML_Lag(y, X, W, name_y='attraction', name_x=selected_features)
print(slm.summary)

# 6. 模型诊断
print("\n模型诊断信息:")
print(f"对数似然值: {slm.logll}")
print(f"AIC值: {slm.aic}")
print(f"空间自回归系数(rho): {slm.rho}")

# OLS回归
ols = spreg.OLS(y, X, name_y='attraction', name_x=selected_features)
print(ols.summary)

# 计算Moran's I检验残差空间自相关
w = W.sparse  # 转换为稀疏矩阵
moran = ps.explore.esda.Moran(ols.u, w)
print("\nMoran's I检验结果:")
print(f"Moran's I值: {moran.I}")
print(f"标准化统计量: {moran.z_rand}")
print(f"P值: {moran.p_rand}")

# 拉格朗日乘数检验
lm_tests = spreg.spDiagnostic(ols, W)
print("\n拉格朗日乘数检验结果:")
print(f"LM-Lag统计量: {lm_tests.lm_lag}")
print(f"LM-Lag P值: {lm_tests.lm_lag_pval}")
print(f"LM-Error统计量: {lm_tests.lm_error}")
print(f"LM-Error P值: {lm_tests.lm_error_pval}")
print(f"稳健LM-Lag统计量: {lm_tests.rlm_lag}")
print(f"稳健LM-Lag P值: {lm_tests.rlm_lag_pval}")
print(f"稳健LM-Error统计量: {lm_tests.rlm_error}")
print(f"稳健LM-Error P值: {lm_tests.rlm_error_pval}")

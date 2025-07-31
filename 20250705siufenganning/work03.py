import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 加载shp文件
gdf = gpd.read_file(r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_04.shp')  # 替换为你的SHP文件路径
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pysal.lib import weights
from esda.moran import Moran
from pysal.explore import esda
from pysal.model import spreg
from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW

# 加载SHP文件
from libpysal.weights import Queen  # 用于空间权重矩阵

# 检查数据
print(gdf.head())
print(gdf.columns)

# 选择要分析的列
columns_to_analyze = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 
                     'ID_Vis', 'PubArt_Vis', 'Arch_Vis', 'FacCol_Vis']

# 确保数据没有缺失值
gdf = gdf.dropna(subset=columns_to_analyze)
# 创建空间权重矩阵 - 这里使用Queen邻接
w = weights.Queen.from_dataframe(gdf)

# 对每一列进行莫兰指数分析
for col in columns_to_analyze:
    # 计算莫兰指数
    moran = Moran(gdf[col], w)
    
    # 打印结果
    print(f"变量: {col}")
    print(f"莫兰指数 I: {moran.I:.4f}")
    print(f"期望值 E[I]: {moran.EI:.4f}")
    # print(f"方差: {moran.VI:.4f}")
    # print(f"Z-score: {moran.z:.4f}")
    print(f"P-value: {moran.p_norm:.4f}")
    
    # 判断显著性
    if moran.p_norm < 0.05:
        print("结果显著，存在空间自相关")
        if moran.I > moran.EI:
            print("表现为空间正相关（聚类）")
        else:
            print("表现为空间负相关（分散）")
    else:
        print("结果不显著，空间分布可能为随机")
    print("\n" + "="*50 + "\n")

# 准备数据
# 假设我们以'Green_Vis'为因变量，其他变量为自变量
y = gdf['Green_Vis'].values.reshape((-1,1))
X = gdf[columns_to_analyze[1:]].values  # 使用其他变量作为自变量

# 获取坐标
coords = list(zip(gdf.geometry.x, gdf.geometry.y))

# 选择带宽
bw_selector = Sel_BW(coords, y, X)
bw = bw_selector.search()

print(f"最优带宽: {bw}")

# 运行GWR模型
gwr_model = GWR(coords, y, X, bw)
gwr_results = gwr_model.fit()

# 打印结果摘要
print(gwr_results.summary())

# 获取局部R平方
local_r2 = gwr_results.localR2

# 将结果添加回GeoDataFrame
gdf['GWR_R2'] = local_r2
for i, col in enumerate(columns_to_analyze[1:]):
    gdf[f'GWR_{col}_coef'] = gwr_results.params[:, i]

# 可视化结果
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(column='GWR_R2', ax=ax, legend=True, 
         legend_kwds={'label': "局部R平方"}, 
         cmap='viridis')
plt.title("地理加权回归的局部R平方")
plt.show()

# 可视化某个变量的系数空间分布
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(column=f'GWR_{columns_to_analyze[1]}_coef', ax=ax, legend=True, 
         legend_kwds={'label': f"{columns_to_analyze[1]}的系数"}, 
         cmap='coolwarm')
plt.title(f"{columns_to_analyze[1]}变量的GWR系数空间分布")
plt.show()
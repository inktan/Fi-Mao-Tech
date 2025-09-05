import geopandas as gpd
import libpysal as lps
from esda.moran import Moran
import numpy as np

# 读取Shapefile文件
gdf = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp')

# 定义需要分析的列
factor_columns = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 'ID_Vis', 'PubArt_Vis', 'Arch_Vis','Histor_Vis','Faccon_Vis','Block_Vis','FacCol_Vis']
result_columns = ['文化感', '自然感', '娱乐感', '现代化', '人际情', '科教感']

# 检查坐标系：如果是地理坐标系（度），则需要投影到投影坐标系（米）
if gdf.crs is None or not gdf.crs.is_projected:
    # 如果还没有投影，这里假设原始数据是WGS84（EPSG:4326），我们将其投影到UTM zone 50N（EPSG:32650）
    # 请根据你的数据实际所在位置选择合适的UTM带
    gdf = gdf.to_crs(epsg=32650)  # 这里以UTM zone 50N（适用于中国大部分地区）为例，请根据实际情况调整

# 创建空间权重矩阵（使用Queen邻接）
w = lps.weights.Queen.from_dataframe(gdf)

# 确保权重矩阵是标准化的（可选，但通常建议）
w.transform = 'r'

# 定义一个函数来计算莫兰指数并打印结果
def calculate_moran(gdf, column, w):
    # 检查是否有缺失值
    if gdf[column].isnull().any():
        print(f"列 {column} 中存在缺失值，将自动删除缺失值所在的行。")
        # 获取非缺失值的索引
        non_missing_idx = gdf[column].notnull()
        y = gdf.loc[non_missing_idx, column]
        # 同时调整权重矩阵，删除对应行
        w_subset = w.subset(non_missing_idx)
    else:
        y = gdf[column]
        w_subset = w
    # 计算莫兰指数
    moran = Moran(y, w_subset)
    print(f"{column}: 莫兰指数 = {moran.I:.4f}, p值 = {moran.p_sim:.4f}")

# 对factor_columns中的每一列计算莫兰指数
print("对factor_columns中的视觉要素进行莫兰指数分析:")
for col in factor_columns:
    calculate_moran(gdf, col, w)

# 对result_columns中的每一列计算莫兰指数
print("\n对result_columns中的情感感知结果进行莫兰指数分析:")
for col in result_columns:
    calculate_moran(gdf, col, w)
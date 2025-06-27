import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

# 输入输出文件路径
input_shp = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_with_avg\山南市_with_avg.shp"  # 请替换为实际路径
output_shp = input_shp.replace('.shp', '_clustered02.shp')  # 输出文件名添加_clustered后缀

# 1. 读取Shapefile数据
gdf = gpd.read_file(input_shp)

# 2. 指定要使用的avg列
target_columns = ['avg_wall', 'avg_buildi', 'avg_sky', 
                 'avg_tree', 'avg_grass', 'avg_water', 'avg_plate']

# 检查这些列是否都存在
missing_cols = [col for col in target_columns if col not in gdf.columns]
if missing_cols:
    raise ValueError(f"以下列不存在于Shapefile中: {missing_cols}")

print(f"用于聚类的列: {target_columns}")

# 3. 提取数据并处理NaN值
data = gdf[target_columns].values
data = SimpleImputer(strategy='constant', fill_value=0).fit_transform(data)

# 4. 数据标准化（建议进行）
from sklearn.preprocessing import StandardScaler
data = StandardScaler().fit_transform(data)

# 5. 使用KMeans聚类（分为6类）
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
gdf['cluster'] = kmeans.fit_predict(data)

# 6. 保存结果到新Shapefile
gdf.to_file(output_shp)
print(f"聚类完成！结果已保存到: {output_shp}")

# 7. 输出聚类结果统计信息
print("\n聚类结果统计:")
cluster_stats = gdf.groupby('cluster')[target_columns].mean()
print(cluster_stats)

# 8. 可视化前5行结果
print("\n前5行聚类结果:")
print(gdf[target_columns + ['cluster', 'geometry']].head())
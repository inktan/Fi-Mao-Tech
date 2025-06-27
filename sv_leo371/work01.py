import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

# 输入输出文件路径
input_shp = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_with_avg\山南市_with_avg.shp"  # 请替换为实际路径
output_shp = input_shp.replace('.shp', '_clustered.shp')  # 输出文件名添加_clustered后缀

# 1. 读取Shapefile数据
gdf = gpd.read_file(input_shp)

# 2. 筛选avg_开头的列（排除avg_lon和avg_lat）
avg_columns = [col for col in gdf.columns 
              if col.startswith('avg_') 
              and col.lower() not in ['avg_lon', 'avg_lat']]

if not avg_columns:
    raise ValueError("未找到任何符合条件的avg_列")

print(f"用于聚类的列: {avg_columns}")

# 3. 提取数据并处理NaN值
data = gdf[avg_columns].values
data = SimpleImputer(strategy='constant', fill_value=0).fit_transform(data)

# 4. 使用KMeans聚类（分为6类）
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)  # 显式设置n_init避免警告
gdf['cluster'] = kmeans.fit_predict(data)

# 5. 保存结果到新Shapefile
gdf.to_file(output_shp)
print(f"聚类完成！结果已保存到: {output_shp}")
print("各类统计信息:")
print(gdf['cluster'].value_counts())

# 可选：查看前5行聚类结果
print("\n前5行聚类结果:")
print(gdf[avg_columns + ['cluster', 'geometry']].head())
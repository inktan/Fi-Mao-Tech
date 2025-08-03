import geopandas as gpd
import numpy as np
import pandas as pd

# 打开SHP文件
shp_file_path = r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_04.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)  # 替换为你的SHP文件路径

# 定义要计算平均值的列
cols_for_mean = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 
                 'ID_Vis', 'PubArt_Vis', 'Arch_Vis', 'FacCol_Vis']

# 计算每行的平均值
mean_values = gdf[cols_for_mean].mean(axis=1)

# 添加新列并赋值为平均值加上随机数
gdf['Histor_Vis'] = mean_values + np.random.uniform(-0.1, 0.1, size=len(gdf))
gdf['Faccon_Vis'] = mean_values + np.random.uniform(-0.1, 0.1, size=len(gdf))
gdf['Block_Vis'] = mean_values + np.random.uniform(-0.1, 0.1, size=len(gdf))

# 确保新值在合理范围内（例如0-1之间，如果需要）
# gdf[['Histor_Vis', 'Faccon_Vis', 'Block_Vis']] = gdf[['Histor_Vis', 'Faccon_Vis', 'Block_Vis']].clip(0, 1)

# 保存修改后的文件
gdf.to_file(r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_05.shp')  # 替换为你想要的输出路径
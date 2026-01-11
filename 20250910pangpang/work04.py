import pandas as pd
import geopandas as gpd

# 1. 读取两个 CSV 文件
df1 = pd.read_csv(r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos_02.csv')
shp_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_GSV_30m_points.shp'

gdf = gpd.read_file(shp_path)

# 3. 添加 FID 列，默认为 index
gdf['FID'] = gdf.index
# 2. 基于 'FID' 列进行左连接 (Left Join)
# left_on 和 right_on 指定列名，如果两表列名完全相同，只需用 on='FID'
# how='left' 表示保留第一个文件的所有行，把第二个文件的匹配数据接上去
merged_df = pd.merge(df1, gdf, on='FID', how='left')

# 3. 保存为新的 CSV 文件
# index=False 避免在保存时多出一列行索引
merged_df.to_csv(r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos_03.csv', index=False, encoding='utf-8-sig')

print("合并完成！")
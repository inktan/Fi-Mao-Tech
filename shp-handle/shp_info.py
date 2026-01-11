import pandas as pd
import geopandas as gpd

# 1. 禁止横向折叠（解决 \ 换行问题）
pd.set_option('display.expand_frame_repr', False)

# 2. 设置显示的最大行数（设置为 None 表示全部显示，慎用，如果数据有几万行会卡死）
pd.set_option('display.max_rows', None)

# 3. 设置显示的最大列数
pd.set_option('display.max_columns', None)

# 4. 解决浮点数精度（防止经纬度被截断）
pd.set_option('display.precision', 15)

# 5. 如果列宽还是不够（防止 geometry 列太长显示 ...）
pd.set_option('display.max_colwidth', None)

shp_file_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_GSV_30m_points.shp'  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path)

# print(gdf.columns)
print(gdf.columns.tolist())
print(gdf.shape)
print(gdf.head(100))
# print(gdf)
# print(gdf.crs)
# print(gdf['geometry'].head())

# gdf = gdf.to_crs(epsg=4326)

# gdf.to_file(r'e:\work\sv_nanzhu\shp文件\50mSVI_cai123_4326.shp')

# gdf = gpd.read_file(shp_file_path)

# 检查是否有 'fclass' 列
# if 'fclass' in gdf.columns:
#     unique_fclasses = gdf['fclass'].unique()
#     print("唯一 fclass 值:", unique_fclasses)
# else:
#     print("该 Shapefile 没有 'fclass' 字段！")





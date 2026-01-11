# 链接shp与csv中的表格数据

shp_path = r'e:\work\sv_pangpang\4_tree_species_deeplearning\GIS_data\CoS_GSV_30m_points.shp'
csv_path = r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos_.csv'

output_path = r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos_01.csv'

import pandas as pd
import geopandas as gpd

# 1. 设置显示配置（如你之前要求的）
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 15)

# 2. 读取数据 (请替换为你的实际文件名)

gdf = gpd.read_file(shp_path)
df_csv = pd.read_csv(csv_path)

# 3. 添加 FID 列，默认为 index
gdf['FID'] = gdf.index

# 4. 统一列名和数据类型以便合并
# 注意：你的描述中 CSV 的列名是小写 'year', 'month'，SHP 是大写 'Year', 'Month'
# 我们将 CSV 的列名临时改为与 SHP 一致
df_csv = df_csv.rename(columns={'year': 'Year', 'month': 'Month'})

# 5. 执行合并 (基于第一个判断条件：ORIG_FID, rid, Year, Month)
# 使用 left join 保证 shp 的行数不减少
merged = pd.merge(
    gdf, 
    df_csv[['ORIG_FID', 'rid', 'Year', 'Month', 'longitude', 'latitude', 'panoid', 'pitch', 'heading', 'fov01', 'fov02']], 
    on=['ORIG_FID', 'rid', 'Year', 'Month'], 
    how='left',
    suffixes=('', '_csv')
)

# 6. 第二个判断条件：坐标差值绝对值小于 0.0000001
# 转换为 float 确保计算准确
merged['lngX'] = merged['lngX'].astype(float)
merged['latY'] = merged['latY'].astype(float)
merged['longitude'] = merged['longitude'].astype(float)
merged['latitude'] = merged['latitude'].astype(float)

mask = (
    (abs(merged['lngX'] - merged['longitude']) < 0.0000001) & 
    (abs(merged['latY'] - merged['latitude']) < 0.0000001)
)

# 7. 筛选符合条件的行
# 如果不符合坐标条件，则将 CSV 带来的扩展列设为 Null
cols_to_keep = ['panoid', 'pitch', 'heading', 'fov01', 'fov02']
merged.loc[~mask, cols_to_keep] = None

# 8. 处理“符合条件的第一行”
# 因为 merge 可能会产生 1 对多的关系（如果 CSV 里有多行符合条件），
# 我们按原始 FID 分组，取每一组的第一行。
result_df = merged.groupby('FID').first().reset_index()

# 9. 保存为新的 CSV 文件
# 使用 utf-8-sig 编码确保中文（如有）不乱码
result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"处理完成，结果已保存至: {output_path}")
print(result_df.head())
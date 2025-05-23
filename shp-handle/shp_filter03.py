import geopandas as gpd

# 1. 读取原始 SHP 文件
input_shp = r"f:\立方数据\202405更新_2024年省市县三级行政区划数据（审图号：GS（2024）0650号）\shp格式的数据（调整过行政区划代码，补全省市县信息）\县.shp"  # 替换为你的输入文件路径
gdf = gpd.read_file(input_shp)

# 2. 设置筛选条件
target_counties = ["西湖区", "上城区", "拱墅区","滨江区"]
target_city = "杭州市"

# 3. 多条件筛选（县名在指定列表中且市名为杭州市）
# 注意：字段名'县名'和'市名'需要根据实际数据调整
filtered_gdf = gdf[
    (gdf['县名'].isin(target_counties)) & 
    (gdf['市名'] == target_city)
]

# 4. 保存为新的 SHP 文件
output_shp = r"e:\work\sv_momo\sv_20250512\sv_20250512.shp"  # 输出文件路径
filtered_gdf.to_file(output_shp, encoding='utf-8')

print(f"筛选完成，共找到 {len(filtered_gdf)} 条记录，已保存到 {output_shp}")
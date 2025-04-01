# import geopandas as gpd

# # 加载Shapefile文件
# gdf = gpd.read_file('f:\sv_suzhou\gis数据\道路网\苏州市.shp')

# # 筛选包含“历史”的行
# # 假设'name'是列名，根据实际情况替换
# filtered_gdf = gdf[gdf['name'].str.contains('山塘', na=False)]

# # 输出筛选后的结果
# print(filtered_gdf['name'])


# Maaherrankatu
# Savilahdenkatu
# Nuijamiestenkatu

import geopandas as gpd

# 1. 读取SHP文件
input_shp = r"e:\work\sv_guannvzhou\street_network.shp"  # 替换为你的SHP文件路径
gdf = gpd.read_file(input_shp)

# 2. 检查是否存在'name'列
if 'name' not in gdf.columns:
    raise ValueError("SHP文件中没有'name'列！")

# 3. 定义要过滤的名称列表
target_names = ["Maaherrankatu", "Savilahdenkatu", "Nuijamiestenkatu"]

# 4. 过滤数据
filtered_gdf = gdf[gdf['name'].isin(target_names)]

# 5. 检查是否找到匹配数据
if len(filtered_gdf) == 0:
    print("警告：没有找到匹配的名称！")
else:
    print(f"找到 {len(filtered_gdf)} 条匹配记录")

# 6. 保存为新的SHP文件
output_shp = "e:\work\sv_guannvzhou\street_network01.shp"
filtered_gdf.to_file(output_shp, encoding='utf-8')

print(f"过滤后的数据已保存到: {output_shp}")
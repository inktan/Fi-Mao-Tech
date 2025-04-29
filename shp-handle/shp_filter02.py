import geopandas as gpd

# 读取SHP文件
input_shp = r"e:\work\sv_shushu\所有指标\six_sv_count_res10.shp"  # 替换为你的输入文件路径
output_shp = r"e:\work\sv_shushu\所有指标\six_sv_count_res1001.shp"  # 替换为你想要的输出文件路径

gdf = gpd.read_file(input_shp)

# 2. 定义要修改的属性字段名
target_field = "sv_counts"  # 替换为你实际要修改的字段名

# 3. 处理数据
for index, row in gdf.iterrows():
    # 获取几何体的中心点坐标（也可以使用其他方法获取代表性坐标）
    centroid = row.geometry.centroid
    latitude = centroid.y  # y坐标对应纬度
    
    # 判断纬度是否小于22.176076
    if latitude < 22.165:
        # 将目标字段值乘以4
        if target_field in row:
            try:
                gdf.at[index, target_field] = float(row[target_field]) * 3.5
            except (ValueError, TypeError):
                print(f"警告：无法转换索引 {index} 的 {target_field} 值为数值")

# 4. 保存为新的SHP文件
gdf.to_file(output_shp)

print(f"处理完成，结果已保存到 {output_shp}")
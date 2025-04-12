import geopandas as gpd

shp_file_path = r"e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd.shp"  # 替换为你的SHP文件路径

encodings_to_try = ['utf-8', 'gbk', 'gb18030', 'big5', 'latin1', 'cp1252']

for encoding in encodings_to_try:
    try:
        gdf = gpd.read_file(shp_file_path, encoding=encoding)
        print(f"成功使用编码: {encoding}")
            
        if 'name_2' in gdf.columns:
            # 假设 gdf 已经读取，但 name_2 列乱码
            gdf['name_2'] = gdf['name_2'].str.encode(encoding).str.decode('utf-8')  # 尝试 latin1 → gbk

            unique_values = gdf['name_2'].unique()
            print("name_2列的唯一值:")
            print(unique_values)
            print(encoding,len(unique_values))
            print(gdf.crs)

            # - EPSG:3857 (Web Mercator，全球适用，但面积和长度有变形)
            # - EPSG:32650 (UTM Zone 50N，适用于中国部分地区)
            target_crs = "EPSG:32650"  # 或 "EPSG:32650"（根据实际位置选择）
            gdf_projected = gdf.to_crs(target_crs)

            # 3. 计算每条几何元素的长度（单位：米）
            if gdf_projected.geometry.type.str.contains("Line").any():
                gdf_projected["length_meters"] = gdf_projected.geometry.length
                print(gdf_projected[["geometry", "length_meters"]])
                print(gdf_projected)
                print(gdf_projected.columns.tolist())
                print(len(gdf_projected.columns.tolist()))
            else:
                print("⚠️ 该SHP文件不包含折线（LineString/MultiLineString）数据！")




        # else:
        #     print("可用列名:", gdf.columns.tolist())
            
        # break
    except UnicodeDecodeError:
        continue
import geopandas as gpd

shp_file_path = r"e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd.shp"  # 替换为你的SHP文件路径
gdf = gpd.read_file(shp_file_path, encoding='latin1')

if 'osm_id' in gdf.columns:

    unique_values = gdf['osm_id'].unique()
    print(unique_values)
    print(len(unique_values))


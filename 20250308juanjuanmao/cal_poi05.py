import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString

# Define the POI shapefile paths with their categories
poi_categories = {
    '餐饮服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_餐饮服务.shp',
    '购物服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_购物服务.shp',
    '生活服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_生活服务.shp',
    '体育休闲服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_体育休闲服务.shp',
    '医疗保健服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_医疗保健服务.shp',
    '住宿服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_住宿服务.shp',
    '金融保险服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_金融保险服务.shp',
    # '教育培训': r'',
    # '文化传媒机构': r'',
    '交通设施': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_交通设施服务.shp',
    '政府机构及社会团体': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_政府机构及社会团体.shp', 
    '公司企业': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_公司企业.shp',
    '汽车服务': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_汽车服务.shp',
    # '房地产': r'',
    # '自然地理': r'',
    '公共设施': r'e:\work\sv_kaixindian\长春市2020\shp\长春市_公共设施.shp',

    '道路附属设施':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_道路附属设施.shp',
    '地名地址信息':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_地名地址信息.shp',
    '风景名胜':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_风景名胜.shp',
    '科教文化服务':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_科教文化服务.shp',
    '摩托车服务':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_摩托车服务.shp',
    '汽车维修':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_汽车维修.shp',
    '汽车销售':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_汽车销售.shp',
    '商务住宅':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_商务住宅.shp',
    '室内设施':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_室内设施.shp',
    '通行设施':r'e:\work\sv_kaixindian\长春市2020\shp\长春市_通行设施.shp',
}

# Load all POI data with their categories
poi_dfs = []
for category, path in poi_categories.items():
    df = gpd.read_file(path)
    df['poi_category'] = category  # Add category column
    poi_dfs.append(df)

# Combine all POIs into one GeoDataFrame
all_pois = gpd.GeoDataFrame(pd.concat(poi_dfs, ignore_index=True))
all_pois = all_pois.to_crs(epsg=32633)  # Convert to UTM for accurate distance calculations

# Process each road shapefile
input_dir = r'E:\work\sv_juanjuanmao\20250308\八条路线'
for filename in os.listdir(input_dir):
    if filename.endswith("03.shp"):
        file_path = os.path.join(input_dir, filename)
        line_gdf = gpd.read_file(file_path).to_crs(epsg=32633)
        print(f"Processing: {file_path}")
        
        # Initialize columns for results
        line_gdf['h_value'] = 0.0
        
        for index, road in line_gdf.iterrows():
            road_geom = road.geometry
            
            # Find POIs within 100m buffer
            buffer = road_geom.buffer(100)
            nearby_pois = all_pois[all_pois.within(buffer)]
            
            if not nearby_pois.empty:
                # Count POIs by category
                category_counts = nearby_pois['poi_category'].value_counts()
                total_pois = category_counts.sum()
                
                # Calculate proportions and H-value
                h_value = 0.0
                for count in category_counts:
                    p = count / total_pois
                    if p > 0:  # Avoid log(0)
                        h_value -= p * np.log(p)
                
                # Store results
                line_gdf.at[index, 'h_value'] = h_value 
        
        # Convert back to original CRS and save
        output_path = file_path.replace('03.shp', '04.shp')
        print(f"Output path: {output_path}")
        line_gdf.to_crs(epsg=4326).to_file(output_path, driver='ESRI Shapefile')
        print(f"Processed and saved: {output_path}")






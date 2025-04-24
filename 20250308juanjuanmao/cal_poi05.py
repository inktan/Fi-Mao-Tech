import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString

# Define the POI shapefile paths with their categories
poi_categories = {
    '餐饮服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_餐饮服务_20220103_145738.shp',
    '购物服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_购物服务_20220103_145740.shp',
    '金融保险服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_金融保险服务_20220103_145744.shp',
    '摩托车服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_摩托车服务_20220103_145738.shp',
    '汽车服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车服务_20220103_145737.shp',
    '汽车维修': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车维修_20220103_145737.shp',
    '汽车销售': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车销售_20220103_145737.shp',
    '生活服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_生活服务_20220103_145740.shp',
    '体育休闲服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_体育休闲服务_20220103_145741.shp',
    '医疗保健服务': r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_医疗保健服务_20220103_145741.shp'
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






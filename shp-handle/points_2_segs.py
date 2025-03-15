import geopandas as gpd
from shapely.geometry import LineString


shape_files=[
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T1.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T2.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T3.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T4.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T5.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T6.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T7.shp',
    r'e:\work\sv_juanjuanmao\20250308\八条路线\T8.shp',
]

for file_path in shape_files:
    print(file_path.replace('.shp','_50m_.shp'))
    gdf_points = gpd.read_file(file_path.replace('.shp','_50m_.shp'))  # 替换为你的输入文件路径

    if len(gdf_points) < 2:
        raise ValueError("需要至少两个点来创建线段")

    lines = []

    for i in range(len(gdf_points) - 1):
        point1 = gdf_points.geometry.iloc[i]
        point2 = gdf_points.geometry.iloc[i + 1]
        line = LineString([point1, point2])
        lines.append(line)

    gdf_lines = gpd.GeoDataFrame(geometry=lines, crs=gdf_points.crs)

    gdf_lines.to_file(file_path.replace('.shp','_50m_SEG.shp')) 
    
    
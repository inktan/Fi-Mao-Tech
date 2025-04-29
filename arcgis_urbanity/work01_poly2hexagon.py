import geopandas
import geodatasets
import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd

import geopandas as gpd
import shapely.geometry
import h3
from shapely.geometry import Polygon
import numpy as np

import geopandas as gpd
import h3
from shapely.geometry import Polygon
import pandas as pd

def calculate_h3_metrics(cell_id):
    """安全计算H3单元的面积和边长"""
    try:
        area_km2 = h3.cell_area(cell_id, unit='km^2')
        area_m2 = h3.cell_area(cell_id, unit='m^2')
        
        # 计算边长需要先获取六边形的边
        edges = h3.cell_to_boundary(cell_id, geo_json=False)
        if len(edges) < 2:  # 确保有足够的点形成边
            raise ValueError("Not enough points to form an edge")
        
        # 计算第一条边的长度作为代表
        start = edges[0]
        end = edges[1]
        edge_length = h3.point_dist(start, end, unit='km')
        
        return pd.Series({
            'area_km2': area_km2,
            'area_m2': area_m2,
            'edge_km': edge_length,
            'edge_m': edge_length * 1000
        })
    except Exception as e:
        print(f"Error processing cell {cell_id}: {str(e)}")
        return pd.Series({
            'area_km2': None,
            'area_m2': None,
            'edge_km': None,
            'edge_m': None
        })

def plot_df(df, column=None, ax=None):
    "Plot based on the `geometry` column of a GeoPandas dataframe"
    df = df.copy()
    df = df.to_crs(epsg=3857)  # web mercator

    if ax is None:
        _, ax = plt.subplots(figsize=(8,8))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    df.plot(
        ax=ax,
        alpha=0.5, edgecolor='k',
        column=column, categorical=True,
        legend=True, legend_kwds={'loc': 'upper left'},
    )
    cx.add_basemap(ax, crs=df.crs, source=cx.providers.CartoDB.Positron)
    plt.show()

def plot_shape(shape, ax=None):
    df = geopandas.GeoDataFrame({'geometry': [shape]}, crs='EPSG:4326')
    plot_df(df, ax=ax)

def plot_cells(cells, ax=None):
    shape = h3.cells_to_h3shape(cells)
    plot_shape(shape, ax=ax)

def plot_shape_and_cells(shape, res=10):
    fig, axs = plt.subplots(1,2, figsize=(10,5), sharex=True, sharey=True)
    plot_shape(shape, ax=axs[0])
    plot_cells(h3.h3shape_to_cells(shape, res), ax=axs[1])
    fig.tight_layout()

# 选择生成六边形的原始范围
shp_file_path = r'e:\work\sv_shushu\20250423\all_points_convex_hull.shp'
gdf = gpd.read_file(shp_file_path)
# 设置CRS为EPSG:4326
gdf.crs = 'EPSG:4326'
geo = gdf.geometry[0]

cells =h3.geo_to_cells(geo, res=10)

shape_column = [h3.cells_to_h3shape([cell]) for cell in cells]

polygons = [Polygon(poly['coordinates'][0]) for poly in [i.__geo_interface__ for i in shape_column]]

gdf = gpd.GeoDataFrame({'geometry': polygons, 'cellId': cells})

gdf.crs = 'EPSG:4326'

# 应用计算到所有单元
# metrics = gdf['cellId'].apply(lambda x: pd.Series(calculate_h3_metrics(x), 
#                                 index=['area_km2', 'area_m2', 'edge_km', 'edge_m']))
# gdf = pd.concat([gdf, metrics], axis=1)

# 4. 打印统计信息
# print("\nH3六边形单元统计信息 (res=10):")
# print(f"总单元数: {len(gdf)}")
# print(f"平均面积: {gdf['area_km2'].mean():.6f} km² ({gdf['area_m2'].mean():.2f} m²)")
# print(f"平均边长: {gdf['edge_km'].mean():.6f} km ({gdf['edge_m'].mean():.2f} m)")
# print(f"面积标准差: {gdf['area_km2'].std():.6f} km²")
# print(f"边长标准差: {gdf['edge_km'].std():.6f} km")

# 5. 打印前5个单元的具体信息
print("\n前5个单元的具体信息:")
print(gdf[['cellId', 'area_km2', 'area_m2', 'edge_km', 'edge_m']].head().to_string())

raise ValueError("Invalid cell ID")

















# 导出为SHP文件
gdf.to_file(r'e:\work\sv_shushu\20250423\all_points_convex_hull_six_polygon_res10.shp')

plot_df(gdf)




import geopandas
import geodatasets
import contextily as cx
import matplotlib.pyplot as plt

import geopandas as gpd
import shapely.geometry
import h3
from shapely.geometry import Polygon

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

def plot_shape_and_cells(shape, res=9):
    fig, axs = plt.subplots(1,2, figsize=(10,5), sharex=True, sharey=True)
    plot_shape(shape, ax=axs[0])
    plot_cells(h3.h3shape_to_cells(shape, res), ax=axs[1])
    fig.tight_layout()

# 选择生成六边形的原始范围
shp_file_path = r'e:\work\sv_shushu\Export_Output-澳门\Export_Output-澳门.shp'
gdf = gpd.read_file(shp_file_path)
# 设置CRS为EPSG:4326
gdf.crs = 'EPSG:4326'
geo = gdf.geometry[1]

cells =h3.geo_to_cells(geo, res=10)
shape_column = [h3.cells_to_h3shape([cell]) for cell in cells]

polygons = [Polygon(poly['coordinates'][0]) for poly in [i.__geo_interface__ for i in shape_column]]

gdf = gpd.GeoDataFrame({'geometry': polygons, 'cellId': cells})

gdf.crs = 'EPSG:4326'
# 导出为SHP文件
gdf.to_file('e:\work\sv_shushu\Export_Output-澳门\six_polygon.shp')

plot_df(gdf)




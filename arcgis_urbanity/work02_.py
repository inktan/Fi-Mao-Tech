import geopandas
import geodatasets
import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd

import geopandas as gpd
import shapely.geometry
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
        alpha=0.15, edgecolor='k',
        column=column, categorical=True,
        legend=True, legend_kwds={'loc': 'upper left'},
    )
    # cx.add_basemap(ax, crs=df.crs, source=cx.providers.CartoDB.Positron)
    plt.show()

# sg_gdf 六边形数据
output_filepath = r'e:\work\sv_shushu\Export_Output-澳门\six_polygon.shp'
polygons_gdf = gpd.read_file(output_filepath)
print(polygons_gdf.shape)
plot_df(polygons_gdf)

# geo_df1 点数据
input_file = r'e:\work\sv_shushu\谷歌\index\scaler.csv'
df = pd.read_csv(input_file)
dst_crs = 'EPSG:4326'

points_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=dst_crs)

print(points_gdf.shape)

joined = gpd.sjoin(points_gdf, polygons_gdf, how="left", predicate='intersects')  
print(joined.shape)
print(joined.head())

print(joined.columns)

geo_df2 = gpd.GeoDataFrame()
# # 取出有效数据列
for i in ['Annoying', 'Calm', 'Chaotic', 'Eventful', 'Human_sounds',
       'Mechanicl_noise', 'Monotonous', 'Music_noise', 'Natural_sounds',
       'Pleasant', 'Sound_intensity', 'Soundscape_quality', 'Sum_building',
       'Sum_plant', 'Sum_road', 'Sum_sky', 'Traffic_noise', 'Uneventful',
       'Vibrant', 'beautiful', 'boring', 'depressing', 'lively', 'safety',
       'wealthy', 'cellId']:
    print(i)
    geo_df2[i] = joined[i]

# # 基于六边形就行分组，计算每组的均值
joined_group = geo_df2.groupby('cellId', as_index=False).mean()

# # 根据hexid分组，并计算每组的数量
# joined_group = joined.groupby('cellId').size().reset_index(name='sv_counts')
print(joined_group.head())

# 将 polygons_gdf 的几何信息合并到 joined_group 中
joined_group = joined_group.merge(
    polygons_gdf[['cellId', 'geometry']],  # 只选择 cellId 和 geometry 列
    on='cellId',  # 根据 cellId 列进行合并
    how='left'    # 左连接，保留 joined_group 的所有行
)

# 将合并后的 DataFrame 转换为 GeoDataFrame
joined_group_gdf = gpd.GeoDataFrame(joined_group, geometry='geometry')

# 打印前几行检查结果
print(joined_group_gdf.head())
joined_group_gdf.to_file(r'E:\work\sv_shushu\谷歌\index\six_sv_scaler.shp')
plot_df(joined_group_gdf)


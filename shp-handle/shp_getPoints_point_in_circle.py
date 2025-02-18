import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import pyproj
import numpy as np
from tqdm import tqdm
import pandas as pd
# 读取WGS84坐标系的点Shapefile文件
input_shp = r'e:\work\sv_j_ran\points\data_coor_unique.shp'
gdf = gpd.read_file(input_shp)
print(gdf.shape)

# 定义WGS84坐标系和UTM坐标系（用于计算距离）
wgs84 = pyproj.CRS('EPSG:4326')
utm = pyproj.CRS('EPSG:32633')  # 这里使用UTM 33N，根据你的数据位置选择合适的UTM带

# 定义坐标转换函数
project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
project_back = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform

# 创建一个新的GeoDataFrame来存储结果
new_points = []

# 遍历每个点
angles = np.linspace(0, 2 * np.pi, 20, endpoint=False)
radius = 500  # 150米

points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude', 'id_circle', 'longitude_circle', 'longitude_circle'])

for idx, row in tqdm(gdf.iterrows()):
    # print(idx)
    # print(row)

    center = row.geometry
    
    # 将中心点从WGS84转换为UTM坐标系
    center_utm = transform(project, center)
    # print(center_utm)
    
    # 在UTM坐标系中生成圆上的点
    points = []
    # 定义函数：在圆上等距离取点
    for index, angle in enumerate(angles):
        x = center_utm.x + radius * np.cos(angle)
        y = center_utm.y + radius * np.sin(angle)

        circle_points_wgs84_temp = transform(project_back, Point(x, y))

        points_df.loc[len(points_df)] = [row['id'], row['long'], row['lat'],index, circle_points_wgs84_temp.x, circle_points_wgs84_temp.y]

output_csv = input_shp.replace('.shp', f'_{radius}_circle.csv')
points_df.to_csv(output_csv, index=False)

print(f"已保存为: {output_csv}")

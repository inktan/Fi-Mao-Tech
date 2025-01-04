import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def main(csv_file,shapefile,output_csv_file):
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 假设CSV文件中有'lon'和'lat'列
    # 创建一个GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry)

    # 读取shapefile
    gdf_polygon = gpd.read_file(shapefile)

    # 检查每个点是否在多边形中
    # 假设shapefile中只有一个多边形
    polygon = gdf_polygon.geometry.unary_union

    # 使用GeoPandas的`within`方法来判断点是否在多边形内
    gdf_points['in_polygon'] = gdf_points.within(polygon)

    # 过滤出在多边形内的点
    gdf_points_in_polygon = gdf_points[gdf_points['in_polygon']]

    # 保存结果到新的CSV文件
    gdf_points_in_polygon.drop(columns='geometry').to_csv(output_csv_file, index=False)

    print(f"Filtered points saved to {output_csv_file}")

if __name__ == "__main__":
    csv_file = r'f:\地学大数据\2024年5月全国路网数据\2024年5月全国路网数据_分省市\广东省\深圳市.csv'
    shapefile = r'e:\work\sv_小丸\福田区面\福田区面.shp'
    output_csv_file = r'e:\work\sv_小丸\points_in_polygon.csv'

    main(csv_file,shapefile,output_csv_file,)
    # pass


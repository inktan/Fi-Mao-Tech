import json
import geopandas as gpd
import osmnx as ox
from shapely.geometry import shape, Polygon
from coord_convert import transform  # 确保你的转换工具可用

def process_geojson_and_download_osm(geojson_path, output_shp):
    try:
        # 1. 读取 GeoJSON 文件
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 兼容处理嵌套的 features 格式
        if "features" in data and isinstance(data["features"], dict):
            inner_features = data["features"]["features"]
        else:
            inner_features = data["features"]

        # 3. 提取第一个有效的多边形 (Polygon)
        # 假设 GeoJSON 中只有一个主要区域，或者我们取第一个
        target_geometry = None
        for feature in inner_features:
            geom = shape(feature['geometry'])
            if geom.geom_type in ['Polygon', 'MultiPolygon']:
                target_geometry = geom
                break
        
        if not target_geometry:
            print("错误：在 GeoJSON 中未找到多边形几何体。")
            return

        # 4. 坐标转换：从 GCJ-02 转换为 WGS84
        # 处理 Polygon 的外轮廓 (exterior)
        print("正在进行坐标转换 (GCJ-02 -> WGS84)...")
        
        def convert_polygon(poly):
            # 转换外轮廓
            wgs_exterior = [transform.gcj2wgs(lng, lat) for lng, lat in poly.exterior.coords]
            # 转换内环（如果有的话）
            wgs_interiors = []
            for hole in poly.interiors:
                wgs_interiors.append([transform.gcj2wgs(lng, lat) for lng, lat in hole.coords])
            return Polygon(wgs_exterior, wgs_interiors)

        if target_geometry.geom_type == 'Polygon':
            polygon_wgs = convert_polygon(target_geometry)
        else:
            # 如果是 MultiPolygon，处理每一个子多边形
            from shapely.geometry import MultiPolygon
            polygon_wgs = MultiPolygon([convert_polygon(p) for p in target_geometry.geoms])

        # 5. 使用 OSMnx 下载路网
        print(f"正在下载该区域的 OSM 路网数据 (此步骤取决于网络和区域大小)...")
        # network_type 可选: 'all', 'drive', 'walk', 'bike'
        G = ox.graph_from_polygon(polygon_wgs, network_type='all', retain_all=True)

        # 6. 转换为 GeoDataFrame 并保存
        # ox.graph_to_gdfs 默认返回 (nodes, edges)
        nodes, edges = ox.graph_to_gdfs(G)
        
        # 移除不支持保存到 Shp 的复杂列（如 lists）
        for col in edges.columns:
            if isinstance(edges[col].iloc[0], list):
                edges[col] = edges[col].astype(str)

        edges.to_file(output_shp, encoding='utf-8')
        print(f"路网已成功保存至: {output_shp}")

    except Exception as e:
        print(f"发生错误：{e}")

# --- 执行设置 ---
input_geojson = r"e:\work\sv_zhoujunling\20260209\OSMB-13ca4e6f72ce0d9773fe5206137002939b07a485.geojson"
output_shapefile = r"e:\work\sv_zhoujunling\20260209\lisiben_network.shp"

process_geojson_and_download_osm(input_geojson, output_shapefile)
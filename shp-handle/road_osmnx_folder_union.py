"""
读取指定文件夹下全部 SHP，合并几何并 unary_union 为一个面域后，
用 OSMnx 下载该范围内的路网（逻辑同 road_osmnx02.py）。
"""
import os
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.ops import unary_union

# 输入：包含多个街道/片区 shp 的文件夹
INPUT_FOLDER = r"E:\work\四个街道"
# 输出路网 shp（可按需修改）
OUTPUT_SHP = r"E:\work\四个街道\_network_union.shp"


def read_all_shps(folder: Path) -> gpd.GeoDataFrame:
    shp_files = sorted(folder.glob("*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"文件夹内未找到 .shp 文件: {folder}")

    pieces = []
    for path in shp_files:
        gdf = gpd.read_file(path)
        if gdf.empty:
            continue
        if gdf.crs is not None:
            gdf = gdf.to_crs("EPSG:4326")
        else:
            gdf = gdf.set_crs("EPSG:4326", allow_override=True)
        pieces.append(gdf)

    if not pieces:
        raise ValueError("所有 shp 均为空，无法合并")

    merged = gpd.GeoDataFrame(
        pd.concat(pieces, ignore_index=True),
        crs="EPSG:4326",
    )
    return merged

def main():
    folder = Path(INPUT_FOLDER)
    if not folder.is_dir():
        raise NotADirectoryError(f"路径不存在或不是文件夹: {folder}")

    gdf = read_all_shps(folder)
    filtered_gdf = gdf

    allowed = {"Polygon", "MultiPolygon"}
    bad = ~filtered_gdf.geometry.geom_type.isin(allowed)
    if bad.any():
        raise ValueError(
            "以下几何类型不允许（需为 Polygon/MultiPolygon）: "
            f"{filtered_gdf.loc[bad, 'geometry'].geom_type.unique().tolist()}"
        )

    merged_polygon = unary_union(filtered_gdf.geometry)

    # 可选：简化以加速下载
    # merged_polygon = merged_polygon.simplify(tolerance=0.0001)

    G = ox.graph_from_polygon(merged_polygon, network_type="all")
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)

    os.makedirs(os.path.dirname(OUTPUT_SHP) or ".", exist_ok=True)
    gdf_edges.to_file(OUTPUT_SHP, encoding="utf-8")
    print(f"路网数据已保存: {OUTPUT_SHP}")


if __name__ == "__main__":
    main()

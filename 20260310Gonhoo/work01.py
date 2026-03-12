# -*- coding: utf-8 -*-
"""
建成环境特征指标计算脚本（指定图层版）
- 街景样本点 300m 缓冲区，按指定 SHP 计算各项指标
- 结果输出：CSV（中文列名）+ SHP + 字段说明 CSV
"""

import os
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
try:
    from shapely.validation import make_valid
except ImportError:
    make_valid = None
from typing import Optional

try:
    from pyproj import CRS, Geod, Transformer
except ImportError:  # pyproj 是地理测地计算必需依赖
    CRS = Geod = Transformer = None

warnings.filterwarnings("ignore", category=UserWarning, module="geopandas")

# ============== 可配置路径 ==============
# 街景样本点（路网采样点）SHP
SAMPLE_POINTS_SHP = r"e:\work\sv_Gonhoo\大阪核心区GIS数据\大阪核心区GIS数据\road_单线_50m_Spatial.shp"
# 输出
OUTPUT_CSV_PATH = r"e:\work\sv_Gonhoo\大阪核心区_建成环境指标_300m.csv"
OUTPUT_SHP_PATH = r"e:\work\sv_Gonhoo\大阪核心区_建成环境指标_300m.shp"
OUTPUT_FIELDS_CSV_PATH = r"e:\work\sv_Gonhoo\大阪核心区_建成环境指标_字段说明.csv"

BUFFER_RADIUS_M = 300
METRIC_CRS = "EPSG:6668"
CHUNK_SIZE = 2000
# 面图层（建筑/绿地/水体）按该数量分块，避免单次 sjoin 过大导致长时间无进度
POLYGON_CHUNK_SIZE = 8000
# 道路/线图层按该数量分块，避免 sjoin(lines, buffers) 时结果表过大导致内存溢出
LINE_CHUNK_SIZE = 5000

# ---------- 指定数据图层（按指标） ----------
# 设施密度、设施多样性：多图层合并，每个要素带类型（来源图层名）
FACILITY_LAYERS = [
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\007-POI\2开源版本\Osaka_交通设施点.shp", "交通设施点"),
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\007-POI\2开源版本\Osaka_人文景观点.shp", "人文景观点"),
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\007-POI\2开源版本\Osaka_自然景观点.shp", "自然景观点"),
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\009-AOI\Osaka_基础设施.shp", "基础设施"),
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\009-AOI\Osaka_沙滩浴场.shp", "沙滩浴场"),
    (r"e:\work\sv_Gonhoo\日本-城市级-大阪\009-AOI\Osaka_宗教.shp", "宗教"),
]

# 公共交通密度：仅交通设施点
TRANSIT_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\007-POI\2开源版本\Osaka_交通设施点.shp",
]

# 建筑密度(%)：建筑轮廓面
BUILDING_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\002-建筑轮廓\Osaka_建筑轮廓.shp",
]

# 道路密度(米/公顷)：公路+轨道交通线
ROAD_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\003-道路网络\Osaka_公路交通.shp",
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\003-道路网络\Osaka_轨道交通.shp",
]

# 绿地占比(%)：草地、公园、林地、森林（面）
GREEN_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_草地.shp",
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_公园面.shp",
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_林地.shp",
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_森林.shp",
]

# 蓝空间占比(%)：湿地、水系面（面积）；水系线单独算长度
WATER_POLYGON_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_湿地.shp",
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_水系面.shp",
]
WATER_LINE_LAYERS = [
    r"e:\work\sv_Gonhoo\日本-城市级-大阪\004-蓝绿空间\Osaka_水系线.shp",
]

try:
    from tqdm.auto import tqdm
except Exception:
    tqdm = None


def _iter_chunks(index, chunk_size):
    n = len(index)
    for i in range(0, n, chunk_size):
        yield index[i : i + chunk_size]


def _is_finite_geometry(geom):
    """几何坐标是否全为有限数（无 NaN/Inf），避免 GEOS orientationIndex 报错。"""
    if geom is None or geom.is_empty:
        return False
    try:
        b = geom.bounds
        return b is not None and all(np.isfinite(b))
    except Exception:
        return False


def _prepare_for_sjoin(gdf, fix_invalid_polygons=False):
    """
    过滤掉坐标含 NaN/Inf 的几何，可选对多边形做 make_valid。
    返回过滤后的 GeoDataFrame（副本），避免 sjoin 时触发 GEOSException。
    """
    if gdf is None or gdf.empty:
        return gdf
    mask = gdf.geometry.apply(_is_finite_geometry)
    out = gdf.loc[mask].copy()
    if out.empty:
        return out
    if fix_invalid_polygons and make_valid is not None and out.geometry.geom_type.str.contains("Polygon", na=False).any():
        invalid = ~out.geometry.is_valid
        if invalid.any():
            out.loc[invalid, out.geometry.name] = out.loc[invalid].geometry.apply(
                lambda g: make_valid(g) if g is not None else g
            )
    return out


def geodesic_buffer_wgs84(points_wgs84: gpd.GeoSeries, radius_m: float) -> gpd.GeoSeries:
    """
    在 WGS84(EPSG:4326) 下为点做“米”为单位的缓冲区（地理坐标系下严禁直接 buffer(m)）。
    做法：对每个点建立本地点位的 Azimuthal Equidistant 投影（单位米）-> buffer -> 再投回 WGS84。
    """
    if CRS is None or Transformer is None:
        raise ImportError("缺少 pyproj：无法在 WGS84 下生成米单位缓冲区（请先安装 pyproj）。")
    if points_wgs84 is None or len(points_wgs84) == 0:
        return points_wgs84
    crs_wgs84 = CRS.from_epsg(4326)

    def _one(p):
        if p is None or p.is_empty:
            return None
        lon, lat = float(p.x), float(p.y)
        if not np.isfinite(lon) or not np.isfinite(lat):
            return None
        local_aeqd = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs"
        )
        return gpd.GeoSeries([p], crs="EPSG:4326").to_crs(local_aeqd).iloc[0].buffer(radius_m)

    # 先在本地投影做 buffer，再统一投回 WGS84
    bufs_local = points_wgs84.apply(_one)
    bufs_local = gpd.GeoSeries(bufs_local, crs=None)
    # 逐个投回 WGS84（每个 buffer 的 local CRS 不同，只能逐个转换）
    out = []
    for geom, p in zip(bufs_local, points_wgs84):
        if geom is None or geom.is_empty or p is None or p.is_empty:
            out.append(None)
            continue
        lon, lat = float(p.x), float(p.y)
        local_aeqd = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs"
        )
        inv = Transformer.from_crs(local_aeqd, crs_wgs84, always_xy=True).transform
        out.append(gpd.GeoSeries([geom], crs=local_aeqd).to_crs("EPSG:4326").iloc[0])
    return gpd.GeoSeries(out, crs="EPSG:4326")


def geodesic_area_m2_wgs84(polygons_wgs84: gpd.GeoSeries) -> pd.Series:
    """用椭球测地线计算 WGS84 多边形面积（平方米），适用于缓冲区面积。"""
    if Geod is None:
        raise ImportError("缺少 pyproj：无法计算测地面积（请先安装 pyproj）。")
    geod = Geod(ellps="WGS84")

    def _area(g):
        if g is None or g.is_empty:
            return 0.0
        if not _is_finite_geometry(g):
            return 0.0
        try:
            a, _ = geod.geometry_area_perimeter(g)
            return float(abs(a))
        except Exception:
            return 0.0

    return polygons_wgs84.apply(_area).astype("float64")


def geodesic_length_m_wgs84(lines_wgs84: gpd.GeoSeries) -> pd.Series:
    """用椭球测地线计算 WGS84 线几何长度（米）。"""
    if Geod is None:
        raise ImportError("缺少 pyproj：无法计算测地线长（请先安装 pyproj）。")
    geod = Geod(ellps="WGS84")

    def _len(g):
        if g is None or g.is_empty:
            return 0.0
        if not _is_finite_geometry(g):
            return 0.0
        try:
            return float(geod.geometry_length(g))
        except Exception:
            return 0.0

    return lines_wgs84.apply(_len).astype("float64")


def test_facility_layers_wgs84(
    sample_points_shp: str = SAMPLE_POINTS_SHP,
    buffer_radius_m: float = BUFFER_RADIUS_M,
    chunk_size: int = 2000,
    limit_points: Optional[int] = 2000,
):
    """
    便于测试：只计算 FACILITY_LAYERS 的 POI 数量/密度/多样性。
    - 全程统一使用 WGS84(EPSG:4326) 存储几何
    - 缓冲区为“米”半径的地理缓冲（本地 AEQD 投影生成，再回到 WGS84）
    - 面积用测地面积（m²）计算，避免在 WGS84 下用 .area 得到“度²”
    直接运行：python work01.py（把 __main__ 里改为调用该函数即可）
    """
    if not Path(sample_points_shp).exists():
        raise FileNotFoundError(sample_points_shp)

    print("=" * 60)
    print("测试：仅 FACILITY_LAYERS（WGS84 + 测地缓冲/面积）")
    print("=" * 60)

    # 样本点转 WGS84
    points = gpd.read_file(sample_points_shp)
    points = ensure_point_geometry(points)
    points = points.to_crs("EPSG:4326") if points.crs != "EPSG:4326" else points
    if limit_points is not None and len(points) > limit_points:
        points = points.iloc[: int(limit_points)].copy()

    # 生成 300m 缓冲区（WGS84 存储）
    buffers_geom = geodesic_buffer_wgs84(points.geometry, float(buffer_radius_m))
    buffers = gpd.GeoDataFrame(geometry=buffers_geom, index=points.index, crs="EPSG:4326")
    buffers = _prepare_for_sjoin(buffers, fix_invalid_polygons=True)

    # 缓冲区面积（测地面积）
    buffer_area_m2 = geodesic_area_m2_wgs84(buffers.geometry)
    print(
        f"样本点数: {len(points)}; 缓冲区面积(m²) 统计: "
        f"min={buffer_area_m2.min():.0f}, mean={buffer_area_m2.mean():.0f}, max={buffer_area_m2.max():.0f}"
    )
    print(f"理论值(圆, r=300m): {np.pi * buffer_radius_m**2:.0f} m²")

    # 加载 FACILITY_LAYERS 并统一到 WGS84
    poi = load_multiple_points_with_type(FACILITY_LAYERS, "EPSG:4326")
    if poi is None or poi.empty:
        raise RuntimeError("FACILITY_LAYERS 加载为空，请检查路径/文件。")
    poi = _prepare_for_sjoin(poi)

    # 统计（within：POI 在缓冲区内）
    poi_count = spatial_join_count_chunked(
        buffers, poi, "within", int(chunk_size), "测试-设施数量(POI within buffer)"
    )
    area_km2 = (buffer_area_m2 / 1e6).replace(0, np.nan)
    poi_density = (poi_count / area_km2).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    poi_div = spatial_join_entropy_chunked(
        buffers, poi, "poi_type", "within", int(chunk_size), "测试-设施多样性(Shannon)"
    )

    out = pd.DataFrame(
        {
            "sid": points.index.astype("int64"),
            "poi_n": poi_count.values,
            "poi_den_km2": poi_density.values,
            "poi_div": poi_div.values,
            "buf_area_m2": buffer_area_m2.reindex(points.index).values,
            "lon": points.geometry.x.values,
            "lat": points.geometry.y.values,
        },
        index=points.index,
    )
    print(out.head(10))
    print("完成。你可以检查 poi_n/poi_den_km2 是否随点变化。")
    return out


def ensure_point_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """线/面转点（取质心），用于设施计数。"""
    if gdf is None or gdf.empty:
        return gdf
    geom_types = gdf.geometry.geom_type.unique()
    if "Point" in geom_types or "MultiPoint" in geom_types:
        pts = gdf.geometry.copy()
        multi = pts.geom_type == "MultiPoint"
        if multi.any():
            pts = pts.copy()
            pts.loc[multi] = pts.loc[multi].centroid
        return gdf.set_geometry(pts)
    return gdf.set_geometry(gdf.geometry.centroid)


def load_and_prepare_sample_points(path: str, to_crs: str) -> gpd.GeoDataFrame:
    """加载街景样本点，转为点并投影到米制 CRS。"""
    gdf = gpd.read_file(path)
    gdf = ensure_point_geometry(gdf)
    if gdf.crs != to_crs:
        gdf = gdf.to_crs(to_crs)
    return gdf


def load_gdf(path: str, to_crs: str = None):
    """读取 SHP，可选投影。"""
    gdf = gpd.read_file(path)
    if to_crs and gdf.crs != to_crs:
        gdf = gdf.to_crs(to_crs)
    return gdf


def load_multiple_points_with_type(path_type_list, to_crs: str):
    """
    path_type_list: [(path, type_name), ...]
    返回合并后的 GeoDataFrame，含列 poi_type（用于多样性）。
    几何统一为点（线/面取质心）。
    """
    out = []
    it = path_type_list
    if tqdm:
        it = tqdm(it, desc="加载设施图层(点)")
    for path, type_name in it:
        if not Path(path).exists():
            continue
        gdf = load_gdf(path, to_crs)
        gdf = ensure_point_geometry(gdf)
        gdf["poi_type"] = type_name
        out.append(gdf[["poi_type", gdf.geometry.name]])
    if not out:
        return None
    return gpd.GeoDataFrame(pd.concat(out, ignore_index=True), crs=out[0].crs)


def load_multiple_files(path_list, to_crs: str, geom_filter=None):
    """
    加载多个 SHP 并合并。geom_filter: "point"|"line"|"polygon" 只保留对应几何类型。
    """
    out = []
    it = path_list
    if tqdm:
        it = tqdm(it, desc="加载多图层")
    for path in it:
        if not Path(path).exists():
            continue
        gdf = load_gdf(path, to_crs)
        if geom_filter:
            gt = gdf.geometry.geom_type
            if geom_filter == "point":
                gdf = gdf[gt.str.contains("Point", na=False)]
            elif geom_filter == "line":
                gdf = gdf[gt.str.contains("Line", na=False)]
            elif geom_filter == "polygon":
                gdf = gdf[gt.str.contains("Polygon", na=False)]
            if gdf.empty:
                continue
        out.append(gdf)
    if not out:
        return None
    return gpd.GeoDataFrame(pd.concat(out, ignore_index=True), crs=out[0].crs)


def shannon_entropy(series: pd.Series) -> float:
    """Shannon 熵。"""
    counts = series.dropna().value_counts()
    if counts.empty or counts.sum() == 0:
        return 0.0
    p = counts / counts.sum()
    return -float((p * np.log(p + 1e-12)).sum())


def spatial_join_count_chunked(buffers, features, predicate, chunk_size, desc):
    """分块：每个 buffer 内要素数量。"""
    if features is None or features.empty:
        return pd.Series(0, index=buffers.index, dtype="int64")
    f = features.to_crs(buffers.crs) if features.crs != buffers.crs else features.copy()
    f = _prepare_for_sjoin(f)
    if f.empty:
        return pd.Series(0, index=buffers.index, dtype="int64")
    out = pd.Series(0, index=buffers.index, dtype="int64")
    it = list(_iter_chunks(buffers.index, chunk_size))
    pbar = tqdm(it, desc=desc) if tqdm else it
    for ix in pbar:
        b = _prepare_for_sjoin(buffers.loc[ix], fix_invalid_polygons=True)
        if b.empty:
            continue
        joined = gpd.sjoin(f, b, how="inner", predicate=predicate)
        if "index_right" in joined.columns and not joined.empty:
            out.loc[b.index] += joined.groupby("index_right").size().reindex(b.index, fill_value=0).astype("int64")
    return out


def spatial_join_entropy_chunked(buffers, poi, type_column, predicate, chunk_size, desc):
    """分块：每个 buffer 内按 type_column 的 Shannon 熵。"""
    if poi is None or poi.empty or type_column not in poi.columns:
        return pd.Series(0.0, index=buffers.index)
    f = poi.to_crs(buffers.crs) if poi.crs != buffers.crs else poi.copy()
    f = _prepare_for_sjoin(f)
    if f.empty:
        return pd.Series(0.0, index=buffers.index)
    geom_name = f.geometry.name
    type_counts = {}
    it = list(_iter_chunks(buffers.index, chunk_size))
    pbar = tqdm(it, desc=desc) if tqdm else it
    for ix in pbar:
        b = _prepare_for_sjoin(buffers.loc[ix], fix_invalid_polygons=True)
        if b.empty:
            continue
        joined = gpd.sjoin(f[[type_column, geom_name]], b, how="inner", predicate=predicate)
        if joined.empty or "index_right" not in joined.columns:
            continue
        grp = joined.groupby(["index_right", type_column]).size()
        for (buf_id, t), cnt in grp.items():
            buf_id = int(buf_id)
            d = type_counts.get(buf_id)
            if d is None:
                d = {}
                type_counts[buf_id] = d
            key = str(t)
            d[key] = d.get(key, 0) + int(cnt)
    out = pd.Series(0.0, index=buffers.index, dtype="float64")
    for buf_id, d in type_counts.items():
        s = pd.Series(d)
        out.loc[buf_id] = shannon_entropy(s.repeat(s.values)) if len(s) else 0.0
    return out


def spatial_join_sum_area_chunked(buffers, polygons, predicate, chunk_size, desc):
    """分块：按 buffer 分块，与 buffer 相交的面面积和。适用于面数量较少的图层。"""
    if polygons is None or polygons.empty:
        return pd.Series(0.0, index=buffers.index)
    f = polygons.to_crs(buffers.crs).copy()
    f = _prepare_for_sjoin(f)
    if f.empty:
        return pd.Series(0.0, index=buffers.index)
    if f.crs and f.crs.is_geographic and Geod is not None:
        f["_area"] = geodesic_area_m2_wgs84(f.geometry)
    else:
        f["_area"] = f.geometry.area
    out = pd.Series(0.0, index=buffers.index, dtype="float64")
    it = list(_iter_chunks(buffers.index, chunk_size))
    pbar = tqdm(it, desc=desc, mininterval=1.0) if tqdm else it
    for ix in pbar:
        b = _prepare_for_sjoin(buffers.loc[ix], fix_invalid_polygons=True)
        if b.empty:
            continue
        joined = gpd.sjoin(f[["_area", f.geometry.name]], b, how="inner", predicate=predicate)
        if joined.empty or "index_right" not in joined.columns:
            continue
        out.loc[b.index] += joined.groupby("index_right")["_area"].sum().reindex(b.index, fill_value=0.0)
    return out


def spatial_join_sum_area_by_polygon_chunks(buffers, polygons, predicate, polygon_chunk_size, desc):
    """
    按「面图层」分块做 sjoin，避免建筑等大面层单次 join 卡死、进度条不动。
    每块处理 polygon_chunk_size 个面，与全部 buffers 做 sjoin，汇总面积后累加。
    """
    if polygons is None or polygons.empty:
        return pd.Series(0.0, index=buffers.index)
    f = polygons.to_crs(buffers.crs).copy()
    f = _prepare_for_sjoin(f)
    if f.empty:
        return pd.Series(0.0, index=buffers.index)
    if f.crs and f.crs.is_geographic and Geod is not None:
        f["_area"] = geodesic_area_m2_wgs84(f.geometry)
    else:
        f["_area"] = f.geometry.area
    buffers_work = _prepare_for_sjoin(buffers, fix_invalid_polygons=True)
    n = len(f)
    out = pd.Series(0.0, index=buffers.index, dtype="float64")
    starts = list(range(0, n, polygon_chunk_size))
    pbar = tqdm(starts, desc=desc, mininterval=0.5, unit="块") if tqdm else starts
    if tqdm:
        pbar.set_postfix({"总面数": n})
    for start in pbar:
        end = min(start + polygon_chunk_size, n)
        chunk = f.iloc[start:end]
        joined = gpd.sjoin(chunk[["_area", chunk.geometry.name]], buffers_work, how="inner", predicate=predicate)
        if joined.empty or "index_right" not in joined.columns:
            continue
        out += joined.groupby("index_right")["_area"].sum().reindex(buffers.index, fill_value=0.0)
    return out


def spatial_join_sum_length_chunked(buffers, lines, predicate, chunk_size, desc, line_chunk_size=5000):
    """
    分块：与 buffer 相交的线长度和。
    - WGS84 下用测地线长(米)；否则用投影坐标系下 .length。
    - 对「线」分块、与「全部 buffers」做 sjoin，避免 (全量线 × 缓冲区) 结果表过大导致内存溢出。
    - 自动过滤坐标含 NaN/Inf 的几何并对缓冲区做 make_valid，避免 GEOSException。
    """
    if lines is None or lines.empty:
        return pd.Series(0.0, index=buffers.index)
    line_chunk_size = line_chunk_size or 5000

    f = lines.to_crs(buffers.crs).copy()
    use_geodesic = f.crs and f.crs.is_geographic and Geod is not None
    if use_geodesic:
        buffers_work = buffers.copy()
    else:
        if f.crs is None or f.crs.is_geographic:
            metric_crs = "EPSG:3857"
            f = f.to_crs(metric_crs)
            buffers_work = buffers.to_crs(metric_crs) if (buffers.crs != metric_crs) else buffers.copy()
        else:
            buffers_work = buffers.copy()
    # 过滤 NaN/Inf 几何，避免 CGAlgorithmsDD::orientationIndex 报错；对缓冲区做 make_valid
    f = _prepare_for_sjoin(f)
    buffers_work = _prepare_for_sjoin(buffers_work, fix_invalid_polygons=True)
    if f.empty or buffers_work.empty:
        return pd.Series(0.0, index=buffers.index)
    if use_geodesic:
        f["_len"] = geodesic_length_m_wgs84(f.geometry)
    else:
        f["_len"] = f.geometry.length

    out = pd.Series(0.0, index=buffers.index, dtype="float64")
    line_starts = list(range(0, len(f), line_chunk_size))
    pbar = tqdm(line_starts, desc=desc, mininterval=0.5, unit="块") if tqdm else line_starts
    if tqdm:
        pbar.set_postfix({"线要素数": len(f)})
    for start in pbar:
        end = min(start + line_chunk_size, len(f))
        chunk = f.iloc[start:end][["_len", f.geometry.name]]
        try:
            joined = gpd.sjoin(chunk, buffers_work, how="inner", predicate=predicate)
        except Exception as e:
            if tqdm:
                pbar.write(f"  警告: 跳过一块线要素(start={start}), 原因: {e}")
            continue
        if joined.empty or "index_right" not in joined.columns:
            continue
        out += joined.groupby("index_right")["_len"].sum().reindex(buffers.index, fill_value=0.0)
    return out


def main():
    sample_path = SAMPLE_POINTS_SHP
    out_csv = OUTPUT_CSV_PATH
    out_shp = OUTPUT_SHP_PATH
    out_fields = OUTPUT_FIELDS_CSV_PATH
    radius = BUFFER_RADIUS_M
    chunk_size = CHUNK_SIZE

    print("=" * 60)
    print("第一步：加载街景样本点并创建 300m 缓冲区（WGS84 + 测地缓冲/面积）")
    print("=" * 60)
    if not Path(sample_path).exists():
        print(f"街景样本点文件不存在: {sample_path}")
        return
    points = gpd.read_file(sample_path)
    points = ensure_point_geometry(points)
    points = points.to_crs("EPSG:4326") if (points.crs is None or points.crs != "EPSG:4326") else points
    if CRS is None or Geod is None:
        raise ImportError("main() 使用 WGS84 测地缓冲/面积，请先安装 pyproj。")
    buffers_geom = geodesic_buffer_wgs84(points.geometry, float(radius))
    buffers = gpd.GeoDataFrame(geometry=buffers_geom, index=points.index, crs="EPSG:4326")
    buffer_area = geodesic_area_m2_wgs84(buffers.geometry)
    n_samples = len(points)
    print(f"样本点数量: {n_samples}, 缓冲区面积(约): min={buffer_area.min():.0f} mean={buffer_area.mean():.0f} max={buffer_area.max():.0f} m²")

    print("\n第二步：加载指定数据图层（统一 WGS84）")
    print("=" * 60)
    # 设施（密度+多样性）：6 个图层合并，带 poi_type
    gdf_facility = load_multiple_points_with_type(FACILITY_LAYERS, "EPSG:4326")
    if gdf_facility is not None:
        print(f"  设施图层(合并): {len(gdf_facility)} 条")

    # 公共交通：仅交通设施点
    gdf_transit = load_multiple_files(TRANSIT_LAYERS, "EPSG:4326", geom_filter="point")
    if gdf_transit is not None:
        gdf_transit = ensure_point_geometry(gdf_transit)
        print(f"  公共交通图层(合并): {len(gdf_transit)} 条")

    # 建筑
    gdf_building = load_multiple_files(BUILDING_LAYERS, "EPSG:4326", geom_filter="polygon")
    if gdf_building is not None:
        print(f"  建筑图层(合并): {len(gdf_building)} 条")

    # 道路（线）
    gdf_road = load_multiple_files(ROAD_LAYERS, "EPSG:4326", geom_filter="line")
    if gdf_road is not None:
        print(f"  道路图层(合并): {len(gdf_road)} 条")

    # 绿地（面）
    gdf_green = load_multiple_files(GREEN_LAYERS, "EPSG:4326", geom_filter="polygon")
    if gdf_green is not None:
        print(f"  绿地图层(合并): {len(gdf_green)} 条")

    # 蓝空间：面 + 线
    gdf_water_poly = load_multiple_files(WATER_POLYGON_LAYERS, "EPSG:4326", geom_filter="polygon")
    gdf_water_line = load_multiple_files(WATER_LINE_LAYERS, "EPSG:4326", geom_filter="line")
    if gdf_water_poly is not None:
        print(f"  蓝空间(面)图层(合并): {len(gdf_water_poly)} 条")
    if gdf_water_line is not None:
        print(f"  蓝空间(线)图层(合并): {len(gdf_water_line)} 条")

    print("\n第三步：在缓冲区内计算各项指标")
    print("=" * 60)

    # 设施密度：缓冲区内设施点数量 / 缓冲区面积（个/km²）
    if gdf_facility is not None:
        poi_count = spatial_join_count_chunked(
            buffers, gdf_facility, "within", chunk_size, "设施密度-POI数量"
        )
        area_km2 = buffer_area / 1e6
        facility_density = (poi_count / area_km2).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        poi_count = pd.Series(0, index=buffers.index)
        facility_density = pd.Series(0.0, index=buffers.index)

    # 设施多样性：同上 6 类，按 poi_type 算 Shannon 熵
    if gdf_facility is not None:
        facility_diversity = spatial_join_entropy_chunked(
            buffers, gdf_facility, "poi_type", "within", chunk_size, "设施多样性-Shannon熵"
        )
    else:
        facility_diversity = pd.Series(0.0, index=buffers.index)

    # 公共交通密度：交通设施点数量 / 缓冲区面积（个/km²）
    if gdf_transit is not None:
        transit_count = spatial_join_count_chunked(
            buffers, gdf_transit, "within", chunk_size, "公共交通密度-站点数"
        )
        area_km2 = buffer_area / 1e6
        transit_density = (transit_count / area_km2).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        transit_count = pd.Series(0, index=buffers.index)
        transit_density = pd.Series(0.0, index=buffers.index)

    # 建筑密度(%)：建筑面积 / 缓冲区面积 × 100（按建筑面分块，避免大图层卡死、进度条不动）
    if gdf_building is not None:
        building_area = spatial_join_sum_area_by_polygon_chunks(
            buffers, gdf_building, "intersects", POLYGON_CHUNK_SIZE, "建筑密度-建筑面积"
        )
        building_density_pct = (building_area / buffer_area * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        building_area = pd.Series(0.0, index=buffers.index)
        building_density_pct = pd.Series(0.0, index=buffers.index)

    # 道路密度(m/ha)：道路长度 / 缓冲区面积(ha)
    if gdf_road is not None:
        road_length_per_buffer = spatial_join_sum_length_chunked(
            buffers, gdf_road, "intersects", chunk_size, "道路密度-道路长度", line_chunk_size=LINE_CHUNK_SIZE
        )
        area_ha = buffer_area / 1e4
        road_density = (road_length_per_buffer / area_ha).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        road_length_per_buffer = pd.Series(0.0, index=buffers.index)
        road_density = pd.Series(0.0, index=buffers.index)

    # 绿地占比(%)：绿地面积 / 缓冲区面积 × 100（按面分块，进度可见）
    if gdf_green is not None:
        green_area = spatial_join_sum_area_by_polygon_chunks(
            buffers, gdf_green, "intersects", POLYGON_CHUNK_SIZE, "绿地占比-绿地面积"
        )
        green_ratio_pct = (green_area / buffer_area * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        green_area = pd.Series(0.0, index=buffers.index)
        green_ratio_pct = pd.Series(0.0, index=buffers.index)

    # 蓝空间占比(%)：湿地+水系面 面积 / 缓冲区面积 × 100（按面分块，进度可见）
    if gdf_water_poly is not None:
        water_area = spatial_join_sum_area_by_polygon_chunks(
            buffers, gdf_water_poly, "intersects", POLYGON_CHUNK_SIZE, "蓝空间占比-水体面积"
        )
        water_ratio_pct = (water_area / buffer_area * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
    else:
        water_area = pd.Series(0.0, index=buffers.index)
        water_ratio_pct = pd.Series(0.0, index=buffers.index)

    if gdf_water_line is not None:
        water_line_length = spatial_join_sum_length_chunked(
            buffers, gdf_water_line, "intersects", chunk_size, "蓝空间-水系线长度", line_chunk_size=LINE_CHUNK_SIZE
        )
    else:
        water_line_length = pd.Series(0.0, index=buffers.index)

    destination_count = poi_count

    # 组装结果（短英文字段名供 SHP）
    result_en = pd.DataFrame(
        {
            "sid": points.index.astype("int64"),
            "poi_n": poi_count.values,
            "poi_den": facility_density.values,
            "poi_div": facility_diversity.values,
            "tr_n": transit_count.values,
            "tr_den": transit_density.values,
            "bld_a": building_area.values,
            "bld_pct": building_density_pct.values,
            "rd_len": road_length_per_buffer.values,
            "rd_den": road_density.values,
            "gr_a": green_area.values,
            "gr_pct": green_ratio_pct.values,
            "wa_a": water_area.values,
            "wa_pct": water_ratio_pct.values,
            "wa_ln": water_line_length.values,
            "dest_n": destination_count.values,
            "buf_a": buffer_area.values,
        },
        index=points.index,
    )
    result_en["x"] = points.geometry.x.values
    result_en["y"] = points.geometry.y.values

    col_zh = {
        "sid": "样本点ID",
        "poi_n": "POI数量(个)",
        "poi_den": "设施密度(个/平方公里)",
        "poi_div": "设施多样性(Shannon熵)",
        "tr_n": "公共交通站点数(个)",
        "tr_den": "公共交通密度(个/平方公里)",
        "bld_a": "建筑面积(平方米)",
        "bld_pct": "建筑密度(%)",
        "rd_len": "道路总长度(米)",
        "rd_den": "道路密度(米/公顷)",
        "gr_a": "绿地面积(平方米)",
        "gr_pct": "绿地占比(%)",
        "wa_a": "水体面积(平方米)",
        "wa_pct": "蓝空间占比(%)",
        "wa_ln": "水系线长度(米)",
        "dest_n": "目的地数量(个)",
        "buf_a": "缓冲区面积(平方米)",
        "x": "经度(WGS84)",
        "y": "纬度(WGS84)",
    }
    result_zh = result_en.rename(columns=col_zh)

    fields_meta = pd.DataFrame(
        [
            ["poi_den", "设施密度(个/平方公里)", "6类设施点(交通/人文/自然/基础设施/沙滩浴场/宗教)数量/缓冲区面积(km²)"],
            ["poi_div", "设施多样性(Shannon熵)", "上述6类设施类型的Shannon熵 H=-Σ(p_i·ln p_i)"],
            ["tr_den", "公共交通密度(个/平方公里)", "交通设施点数量/缓冲区面积(km²)"],
            ["bld_pct", "建筑密度(%)", "建筑轮廓面积/缓冲区面积×100%"],
            ["rd_den", "道路密度(米/公顷)", "公路+轨道交通线长度/缓冲区面积(ha)"],
            ["gr_pct", "绿地占比(%)", "草地+公园+林地+森林面积/缓冲区面积×100%"],
            ["wa_pct", "蓝空间占比(%)", "湿地+水系面面积/缓冲区面积×100%"],
            ["wa_ln", "水系线长度(米)", "水系线与缓冲区相交的线长度"],
        ],
        columns=["字段名(用于SHP)", "中文指标名(用于CSV)", "计算说明"],
    )

    os.makedirs(Path(out_csv).parent, exist_ok=True)
    result_zh.to_csv(out_csv, index=False, encoding="utf-8-sig")
    fields_meta.to_csv(out_fields, index=False, encoding="utf-8-sig")

    out_gdf = gpd.GeoDataFrame(result_en, geometry=points.geometry, crs=points.crs)
    try:
        out_gdf.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")
    except Exception:
        out_gdf.to_file(out_shp, driver="ESRI Shapefile")

    print(f"\n结果已保存(CSV): {out_csv}")
    print(f"结果已保存(SHP): {out_shp}")
    print(f"字段说明已保存: {out_fields}")
    return result_zh


if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     test_facility_layers_wgs84(limit_points=2000)  # 可把 limit_points 调小便于快速测试


import os
from typing import List, Optional, Tuple

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

# 第一步：点 shp 中 5 个颜色的列名配置。
# - 比例列：R1, R2, R3, R4, R5 （值如 0.25555），总和理论上为 1
# - 颜色列：rgbCode1, ..., rgbCode5 （值如 "rgb(211,187,206)"）
DEFAULT_RGBCODE_COLUMNS = ["rgbCode1", "rgbCode2", "rgbCode3", "rgbCode4", "rgbCode5"]
DEFAULT_RATIO_COLUMNS = ["R1", "R2", "R3", "R4", "R5"]


def _parse_rgb_code(value) -> Tuple[float, float, float]:
    """
    将 'rgb(211,187,206)' 或 '211,187,206' 转为 (R,G,B) 浮点数（0-255）。
    非法或缺失时返回 (0,0,0)。
    """
    s = str(value).strip()
    if not s:
        return 0.0, 0.0, 0.0
    s_lower = s.lower()
    if s_lower.startswith("rgb"):
        l = s.find("(")
        r = s.rfind(")")
        if l != -1 and r != -1 and r > l:
            s = s[l + 1 : r]
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) != 3:
        return 0.0, 0.0, 0.0
    try:
        r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
        return r, g, b
    except Exception:
        return 0.0, 0.0, 0.0


def _rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """RGB 0-255 -> H(0-360), S(0-1), V(0-1)。"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx
    if mx == 0:
        return 0.0, 0.0, 0.0
    s = (mx - mn) / mx
    if mx == mn:
        return 0.0, s, v
    if mx == r:
        h = (g - b) / (mx - mn) + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / (mx - mn) + 2
    else:
        h = (r - g) / (mx - mn) + 4
    h = h / 6.0 * 360.0
    return h, s, v


def _luminance(r: float, g: float, b: float) -> float:
    """亮度（明度分量），0-255 -> 0-1。"""
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _circular_std_degrees(angles_deg: np.ndarray, weights: np.ndarray) -> float:
    """加权环形标准差（角度 0-360），用于协调度。"""
    if len(angles_deg) == 0 or weights.sum() <= 0:
        return 0.0
    rad = np.deg2rad(angles_deg)
    x = np.sum(weights * np.cos(rad)) / weights.sum()
    y = np.sum(weights * np.sin(rad)) / weights.sum()
    r = np.sqrt(x * x + y * y)
    if r <= 1e-10:
        return 180.0
    return np.rad2deg(np.sqrt(-2 * np.log(r)))


def add_lightness_chroma_harmony(
    gdf: gpd.GeoDataFrame,
    rgb_code_columns: Optional[List[str]] = None,
    ratio_columns: Optional[List[str]] = None,
) -> gpd.GeoDataFrame:
    """
    基于 5 个 RGB 颜色及占比，为 gdf 增加三列：明度、彩度、协调度。
    - 明度：加权平均亮度（0.299R+0.587G+0.114B）/255，加权为各色占比。
    - 彩度：加权平均饱和度（HSV 的 S）。
    - 协调度：色相分布越集中越协调，取 1/(1+色相加权环形标准差)，值越大越协调。
    """
    rgb_code_columns = rgb_code_columns or DEFAULT_RGBCODE_COLUMNS
    ratio_columns = ratio_columns or DEFAULT_RATIO_COLUMNS
    if len(rgb_code_columns) != len(ratio_columns):
        raise ValueError("颜色列与占比列数量不一致。")

    out = gdf.copy()
    lightness_list = []
    chroma_list = []
    harmony_list = []

    for i in range(len(gdf)):
        row = gdf.iloc[i]
        ratios = []
        luminances = []
        saturations = []
        hues = []
        for k, code_col in enumerate(rgb_code_columns):
            code_val = row[code_col] if code_col in row.index else None
            rr, gg, bb = _parse_rgb_code(code_val)
            ratio_col = ratio_columns[k]
            w = float(row[ratio_col]) if ratio_col in row.index else 0.0
            ratios.append(w)
            luminances.append(_luminance(rr, gg, bb))
            h, s, v = _rgb_to_hsv(rr, gg, bb)
            hues.append(h)
            saturations.append(s)

        ratios = np.array(ratios)
        total_ratio = ratios.sum()
        if total_ratio <= 0:
            total_ratio = 1.0
        weights = ratios / total_ratio

        lightness = float(np.sum(weights * np.array(luminances)))
        chroma = float(np.sum(weights * np.array(saturations)))
        hue_std = _circular_std_degrees(np.array(hues), weights)
        harmony = 1.0 / (1.0 + hue_std / 180.0)

        lightness_list.append(lightness)
        chroma_list.append(chroma)
        harmony_list.append(harmony)

    out["明度"] = lightness_list
    out["彩度"] = chroma_list
    out["协调度"] = harmony_list
    return out


def load_points_shp_with_color(
    points_shp_path: str,
    rgb_code_columns: Optional[List[str]] = None,
    ratio_columns: Optional[List[str]] = None,
) -> gpd.GeoDataFrame:
    """
    第一步：打开指定路径的点 shp，每个点对应一张图像，附带 5 个 RGB 颜色及占比（总和约为 1）。
    - 比例列：R1~R5
    - 颜色列：rgbCode1~rgbCode5，内容为 "rgb(211,187,206)"。
    增加三列：明度、彩度、协调度，并返回 GeoDataFrame。
    """
    gdf = gpd.read_file(points_shp_path)
    rgb_code_columns = rgb_code_columns or DEFAULT_RGBCODE_COLUMNS
    ratio_columns = ratio_columns or DEFAULT_RATIO_COLUMNS
    for c in rgb_code_columns:
        if c not in gdf.columns:
            raise KeyError(f"点 shp 缺少颜色列: {c}，现有列: {list(gdf.columns)}")
    for rcol in ratio_columns:
        if rcol not in gdf.columns:
            raise KeyError(f"点 shp 缺少占比列: {rcol}，现有列: {list(gdf.columns)}")
    return add_lightness_chroma_harmony(gdf, rgb_code_columns, ratio_columns)


def project_to_match(points_gdf: gpd.GeoDataFrame, line_gdf: gpd.GeoDataFrame):
    """
    将点和线投影到同一坐标系。
    - 如果 shp 已经是投影坐标系（单位一般为米），则将点投影到该坐标系；
    - 如果 shp 是地理坐标系，则统一转到 EPSG:3857（Web Mercator，单位近似为米）。
    """
    if line_gdf.crs is None:
        # 如果 shp 没有 CRS 信息，假定为 WGS84
        line_gdf = line_gdf.set_crs("EPSG:4326", allow_override=True)

    if line_gdf.crs.is_geographic:
        target_crs = "EPSG:3857"
        line_proj = line_gdf.to_crs(target_crs)
        points_proj = points_gdf.to_crs(target_crs)
    else:
        target_crs = line_gdf.crs
        line_proj = line_gdf
        points_proj = points_gdf.to_crs(target_crs)

    return points_proj, line_proj


def _safe_filename(name: str) -> str:
    """将道路名转为可作文件名的字符串。"""
    return "".join(c if c not in r'\/:*?"<>|' else "_" for c in str(name).strip() or "unnamed")


def _to_linestring(geom):
    """
    将 LineString 或 MultiLineString 规范为单条 LineString 用于后续处理。
    - LineString：直接返回；
    - MultiLineString：用 linemerge 合并，若得到一条线则返回，否则取最长的一段。
    其他类型或合并失败返回 None。
    """
    if geom is None or geom.is_empty:
        return None
    if isinstance(geom, LineString):
        return geom
    if isinstance(geom, MultiLineString):
        try:
            merged = linemerge(geom)
            if isinstance(merged, LineString):
                return merged
            if isinstance(merged, MultiLineString):
                # 合并后仍为多段（不连通），取最长的一段
                return max(merged.geoms, key=lambda g: g.length)
        except Exception:
            return None
    return None


def process_lines_and_points_from_gdf(
    points_gdf: gpd.GeoDataFrame,
    line_shp_path: str,
    output_folder: str,
    line_name_field: str = "name",
    distance_threshold_m: float = 10.0,
) -> None:
    """
    第二步：
    1. 读取指定路径的线 shp 中的每一条线；
    2. 对于每条线，从几何点中查找距离该线 < distance_threshold_m 的点；
    3. 按在线上的投影距离沿道路排序，给出新的排序 index；
    4. 保留源数据所有信息，按道路名分别保存为 CSV 和 SHP。
    """
    os.makedirs(output_folder, exist_ok=True)
    lines_gdf = gpd.read_file(line_shp_path)
    if line_name_field not in lines_gdf.columns:
        raise KeyError(
            f"线 shp 中未找到道路名字段 '{line_name_field}'，"
            f"现有字段：{list(lines_gdf.columns)}"
        )
    points_proj, lines_proj = project_to_match(points_gdf, lines_gdf)

    for idx, row in lines_proj.iterrows():
        geom = _to_linestring(row.geometry)
        if geom is None:
            continue

        road_name = str(row[line_name_field]).strip() or f"line_{idx}"
        safe_name = _safe_filename(road_name)

        distances = points_proj.distance(geom)
        mask = distances <= distance_threshold_m
        near_points = points_proj[mask].copy()
        if near_points.empty:
            continue

        projections = near_points.geometry.apply(geom.project)
        near_points["proj_dist"] = projections
        near_points_sorted = near_points.sort_values("proj_dist").reset_index(drop=True)
        near_points_sorted["index"] = near_points_sorted.index + 1

        # 保留所有列（含 geometry），写 CSV 时排除 geometry
        cols_for_csv = [c for c in near_points_sorted.columns if c != "geometry"]
        out_csv = os.path.join(output_folder, f"{safe_name}.csv")
        near_points_sorted[cols_for_csv].to_csv(out_csv, index=False, encoding="utf-8-sig")

        out_shp = os.path.join(output_folder, f"{safe_name}.shp")
        near_points_sorted.to_file(out_shp, encoding="utf-8")


def process_lines_and_points(
    image_folder: str,
    shp_path: str,
    output_folder: str,
    line_name_field: str = "name",
    distance_threshold_m: float = 10.0,
) -> None:
    """
    为兼容旧脚本，保留函数签名，但不再从图片文件夹解析点。
    实际逻辑同：先从点 shp 读取颜色信息并计算明度/彩度/协调度，再按线 shp 做 10m 内点排序。
    如无图片相关需求，建议直接使用：load_points_shp_with_color + process_lines_and_points_from_gdf。
    """
    os.makedirs(output_folder, exist_ok=True)
    # 这里简单假定 image_folder 传入的是点 shp 路径，为避免误用请优先使用新流程。
    points_shp_path = image_folder
    points_gdf = load_points_shp_with_color(points_shp_path)
    process_lines_and_points_from_gdf(
        points_gdf,
        line_shp_path=shp_path,
        output_folder=output_folder,
        line_name_field=line_name_field,
        distance_threshold_m=distance_threshold_m,
    )


def main():
    """
    第一步：打开点 shp，根据 5 个 RGB 颜色及占比计算明度、彩度、协调度并增加三列。
    第二步：读取线 shp，对每条线筛选距离 <10m 的点，沿道路排序后按道路名输出 CSV 和 SHP（保留全部属性）。
    使用前请根据实际情况修改下面路径与字段名。
    """
    # ---------- 第一步：点 shp（每个点对应一张图，含 5 个颜色比例 R1~R5 与 rgbCode1~5）----------
    points_shp_path = r"E:\work\work_suncaiyu\points_with_colors.shp"  # 指定点 shp 路径
    # 若颜色/占比列名不是 R1~R5 与 rgbCode1~5，请在调用 load_points_shp_with_color 时传入自定义列名
    points_gdf = load_points_shp_with_color(points_shp_path)
    # 可选：保存带明度/彩度/协调度的点 shp
    # points_gdf.to_file(points_shp_path.replace(".shp", "_with_indicators.shp"), encoding="utf-8")

    # ---------- 第二步：线 shp，按道路输出排序后的点（CSV + SHP）----------
    line_shp_path = r"e:\work\work_suncaiyu\road_typical.shp"  # 道路线 shp 路径
    output_folder = r"E:\work\work_suncaiyu\output_by_road"  # 每条道路一个 CSV 和一个 SHP，以道路名命名
    line_name_field = "name"  # 线 shp 中表示道路名的字段
    process_lines_and_points_from_gdf(
        points_gdf=points_gdf,
        line_shp_path=line_shp_path,
        output_folder=output_folder,
        line_name_field=line_name_field,
        distance_threshold_m=10.0,
    )


if __name__ == "__main__":
    main()




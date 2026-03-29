"""
从指定文件夹读取图片文件名，按 _ 分割解析为 index/lon/lat/heading_degree/year/month/svi_degree，
保存全量 CSV，再按 lon+lat 去重后保存唯一点 CSV 与 SHP。
"""
import os
import pandas as pd
import geopandas as gpd
from pathlib import Path

# ========== 配置（直接修改后运行） ==========
# 图片所在文件夹路径
folder_path = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\厦门市\街景"
# 全量结果 CSV 保存路径
# output_csv = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\厦门市\svi_厦门市_points.csv"
# 去重后 CSV 保存路径（仅唯一 lon,lat）
output_csv_unique = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\厦门市\svi_厦门市_points_unique.csv"
# 去重后 SHP 保存路径
output_shp_unique = r"F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\厦门市\svi_厦门市_points_unique.shp"

# 支持的图片扩展名（小写）
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

# 全量表列名（与文件名按 _ 分割后的顺序一致）
COLUMNS = ["index", "lon", "lat", "heading_degree", "year", "month", "svi_degree"]


def collect_image_names(folder: str) -> list[str]:
    """读取指定文件夹下所有图片文件名（不含路径）。"""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"文件夹不存在: {folder}")
    return [
        f.name
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]


def parse_filename_to_row(name: str) -> dict | None:
    """
    按 _ 分割文件名（去掉扩展名），得到 7 列：index, lon, lat, heading_degree, year, month, svi_degree。
    若分割后不足 7 段则返回 None。
    """
    stem = Path(name).stem
    parts = stem.split("_")
    if len(parts) < len(COLUMNS):
        return None
    row = {col: parts[i] for i, col in enumerate(COLUMNS)}
    return row


def build_full_dataframe(folder_path: str) -> pd.DataFrame:
    """从文件夹收集图片名并解析为 DataFrame，列名为 COLUMNS。"""
    names = collect_image_names(folder_path)
    rows = []
    for name in names:
        row = parse_filename_to_row(name)
        if row is not None:
            rows.append(row)
    return pd.DataFrame(rows, columns=COLUMNS)


def save_full_csv(df: pd.DataFrame, path: str) -> None:
    """保存全量数据到 CSV。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"全量数据已保存: {path}，共 {len(df)} 行")


def deduplicate_by_lon_lat(df: pd.DataFrame) -> pd.DataFrame:
    """按 lon, lat 两列去重，保留第一次出现的行。lon/lat 转为数值再比较。"""
    df = df.copy()
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df = df.dropna(subset=["lon", "lat"])
    return df.drop_duplicates(subset=["lon", "lat"], keep="first").reset_index(drop=True)


def save_unique_csv(df_unique: pd.DataFrame, path: str) -> None:
    """保存去重后的 CSV（仅保留 lon, lat 等列）。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df_unique.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"去重数据已保存: {path}，共 {len(df_unique)} 行")


def save_unique_shp(df_unique: pd.DataFrame, path: str) -> None:
    """将去重后的 lon/lat 保存为点矢量 SHP（WGS84）。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    gdf = gpd.GeoDataFrame(
        df_unique,
        geometry=gpd.points_from_xy(df_unique["lon"], df_unique["lat"]),
        crs="EPSG:4326",
    )
    gdf.to_file(path, driver="ESRI Shapefile", encoding="utf-8")
    print(f"去重点 SHP 已保存: {path}，共 {len(gdf)} 个点")


def main():
    # 1) 读取文件夹中所有图片文件名，按 _ 分割，得到全量 DataFrame
    df = build_full_dataframe(folder_path)
    if df.empty:
        print("未解析到任何有效图片记录，请检查文件夹路径与文件名格式（需至少 7 段用 _ 分隔）。")
        return

    # 2) 保存全量 CSV
    # save_full_csv(df, output_csv)

    # 3) 按 lon, lat 去重
    df_unique = deduplicate_by_lon_lat(df)
    if df_unique.empty:
        print("去重后无有效数值坐标，未写入唯一 CSV/SHP。")
        return

    # 4) 保存去重后的 CSV 与 SHP
    save_unique_csv(df_unique, output_csv_unique)
    save_unique_shp(df_unique, output_shp_unique)


if __name__ == "__main__":
    main()

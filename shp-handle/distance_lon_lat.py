import csv
import math
from pathlib import Path
from statistics import mean

CSV_PATH = Path(r"E:\work\sv_tw\test_network_10m_Optimized_top5_osm_ids.csv")
MAX_POINTS = 2
EARTH_RADIUS_M = 6371.0 * 1000.0


def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """两点大圆距离（米）。"""
    lon1, lat1, lon2, lat2 = map(math.radians, (lon1, lat1, lon2, lat2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    a = min(1.0, max(0.0, a))
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_M * c


def load_lon_lat(path: Path, limit: int) -> tuple[list[float], list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"找不到 CSV：{path}")

    lons: list[float] = []
    lats: list[float] = []

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV 无表头")

        fields = {name.strip().lower(): name for name in reader.fieldnames}
        lon_key = fields.get("longitude") or fields.get("lon")
        lat_key = fields.get("latitude") or fields.get("lat")
        if not lon_key or not lat_key:
            raise ValueError(
                "需要包含 longitude/latitude（或 lon/lat）列，当前表头："
                + ", ".join(reader.fieldnames)
            )

        for row in reader:
            if len(lons) >= limit:
                break
            try:
                lo = float(row[lon_key])
                la = float(row[lat_key])
            except (KeyError, TypeError, ValueError):
                continue
            if not math.isfinite(lo) or not math.isfinite(la):
                continue
            lons.append(lo)
            lats.append(la)

    if len(lons) < 2:
        raise ValueError(f"有效经纬度点不足 2 个（当前 {len(lons)}）")

    return lons, lats


def main() -> None:
    lons, lats = load_lon_lat(CSV_PATH, MAX_POINTS)
    n = len(lons)
    seg_m = [
        haversine_m(lons[i], lats[i], lons[i + 1], lats[i + 1]) for i in range(n - 1)
    ]
    avg_m = mean(seg_m)

    print(f"文件: {CSV_PATH}")
    print(f"使用点数: {n}（至多 {MAX_POINTS}）")
    print(f"相邻段数: {len(seg_m)}")
    print(f"相邻段距离平均值: {avg_m:.6f} m")


if __name__ == "__main__":
    main()

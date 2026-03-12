# -*- coding: utf-8 -*-
"""
上海地标区域与采样点生成：100 个地标区域，每区域 100 个经纬度点。
输出：地标 CSV/SHP、采样点 CSV/SHP（用于后续百度街景等）。
"""

import csv
import math
from pathlib import Path
from typing import Optional

# ============== 输出路径配置（请按需修改） ==============
# 输出根目录（所有 CSV/SHP 均在此目录下）；若写字符串路径请用 Path() 包裹
OUTPUT_DIR = Path(r"E:\work\sv_Humpy\output")

# 地标区域文件（100 个地标中心信息）
LANDMARKS_CSV_FILENAME = "shanghai_landmarks.csv"
LANDMARKS_SHP_FILENAME = "shanghai_landmarks.shp"

# 每个区域 100 个采样点文件（自动添加 _points 后缀在“逻辑名”上，实际文件名见下）
POINTS_CSV_FILENAME = "shanghai_landmark_points.csv"
POINTS_SHP_FILENAME = "shanghai_landmark_points.shp"

# 生成后的完整路径（供程序内部使用）
LANDMARKS_CSV_PATH = OUTPUT_DIR / LANDMARKS_CSV_FILENAME
LANDMARKS_SHP_PATH = OUTPUT_DIR / LANDMARKS_SHP_FILENAME
POINTS_CSV_PATH = OUTPUT_DIR / POINTS_CSV_FILENAME
POINTS_SHP_PATH = OUTPUT_DIR / POINTS_SHP_FILENAME

# 上海地标：名称, 经度, 纬度, 覆盖半径(米)
SHANGHAI_LANDMARKS = [
    ("外滩", 121.4909, 31.2397, 350),
    ("东方明珠", 121.4997, 31.2397, 200),
    ("南京路步行街", 121.4785, 31.2384, 300),
    ("豫园", 121.4933, 31.2270, 250),
    ("人民广场", 121.4754, 31.2315, 300),
    ("上海博物馆", 121.4736, 31.2284, 150),
    ("新天地", 121.4737, 31.2192, 250),
    ("田子坊", 121.4634, 31.2104, 200),
    ("静安寺", 121.4454, 31.2236, 200),
    ("徐家汇天主教堂", 121.4372, 31.1925, 150),
    ("陆家嘴滨江", 121.5050, 31.2400, 300),
    ("世纪公园", 121.5517, 31.2194, 500),
    ("中山公园", 121.4204, 31.2194, 250),
    ("复兴公园", 121.4694, 31.2178, 200),
    ("上海迪士尼度假区", 121.6574, 31.1434, 600),
    ("上海野生动物园", 121.7234, 31.0503, 400),
    ("朱家角古镇", 121.0486, 31.1086, 350),
    ("七宝古镇", 121.3531, 31.1553, 250),
    ("多伦路文化街", 121.4847, 31.2661, 150),
    ("武康路", 121.4342, 31.2025, 200),
    ("思南路", 121.4692, 31.2142, 180),
    ("上海环球金融中心", 121.5054, 31.2394, 150),
    ("上海中心大厦", 121.5058, 31.2336, 150),
    ("金茂大厦", 121.5052, 31.2354, 150),
    ("上海大剧院", 121.4736, 31.2311, 120),
    ("上海城市规划展示馆", 121.4742, 31.2311, 120),
    ("上海当代艺术博物馆", 121.4942, 31.2125, 150),
    ("中华艺术宫", 121.4936, 31.1853, 250),
    ("世博公园", 121.4942, 31.1850, 400),
    ("后滩公园", 121.4714, 31.1753, 350),
    ("前滩公园", 121.4711, 31.1589, 300),
    ("滨江大道", 121.5028, 31.2389, 350),
    ("上海科技馆", 121.5444, 31.2194, 200),
    ("世纪大道", 121.5278, 31.2289, 400),
    ("张江高科", 121.5853, 31.2036, 300),
    ("五角场", 121.5153, 31.2986, 300),
    ("大学路", 121.5103, 31.2989, 200),
    ("江湾体育场", 121.5131, 31.3036, 200),
    ("鲁迅公园", 121.4842, 31.2719, 250),
    ("虹口足球场", 121.4831, 31.2711, 180),
    ("1933老场坊", 121.4911, 31.2589, 150),
    ("M50创意园", 121.4486, 31.2553, 150),
    ("苏州河步道", 121.4600, 31.2450, 400),
    ("天安千树", 121.4486, 31.2536, 150),
    ("长风公园", 121.3942, 31.2264, 300),
    ("真如寺", 121.3892, 31.2522, 150),
    ("上海西站商圈", 121.4011, 31.2625, 250),
    ("曹杨商城", 121.4053, 31.2394, 200),
    ("环球港", 121.4186, 31.2322, 200),
    ("中山北路商圈", 121.4589, 31.2625, 250),
    ("大宁国际", 121.4553, 31.2789, 200),
    ("大宁灵石公园", 121.4511, 31.2811, 300),
    ("彭浦夜市", 121.4486, 31.3053, 200),
    ("吴江路", 121.4686, 31.2336, 150),
    ("淮海路", 121.4711, 31.2197, 400),
    ("陕西南路", 121.4589, 31.2153, 300),
    ("衡山路", 121.4486, 31.2089, 250),
    ("永康路", 121.4589, 31.2125, 150),
    ("安福路", 121.4436, 31.2189, 150),
    ("巨鹿路", 121.4589, 31.2203, 180),
    ("长乐路", 121.4636, 31.2189, 200),
    ("上海图书馆", 121.4442, 31.2089, 150),
    ("上海体育馆", 121.4378, 31.1853, 180),
    ("龙华寺", 121.4486, 31.1753, 200),
    ("西岸美术馆", 121.4589, 31.1853, 150),
    ("龙美术馆", 121.4611, 31.1825, 120),
    ("徐汇滨江", 121.4589, 31.1889, 350),
    ("上海南站", 121.4328, 31.1536, 250),
    ("锦江乐园", 121.4136, 31.1425, 250),
    ("梅陇", 121.4089, 31.1489, 200),
    ("莘庄", 121.3853, 31.1111, 300),
    ("七宝万科", 121.3511, 31.1589, 200),
    ("虹桥机场火车站", 121.3361, 31.1978, 400),
    ("国家会展中心", 121.3053, 31.1489, 350),
    ("青浦奥特莱斯", 121.2236, 31.1589, 200),
    ("松江大学城", 121.1853, 31.0311, 400),
    ("泰晤士小镇", 121.2136, 31.0353, 300),
    ("广富林遗址", 121.2311, 31.0489, 300),
    ("佘山", 121.1889, 31.1053, 400),
    ("上海欢乐谷", 121.1953, 31.0989, 300),
    ("东平国家森林公园", 121.4511, 31.6236, 500),
    ("崇明岛瀛洲公园", 121.3989, 31.6289, 250),
    ("南汇嘴观海公园", 121.9511, 31.0264, 300),
    ("滴水湖", 121.9289, 30.9089, 400),
    ("临港大道", 121.9111, 30.9253, 350),
    ("上海海昌海洋公园", 121.9236, 30.9089, 300),
    ("奉贤碧海金沙", 121.5011, 30.9089, 350),
    ("古猗园", 121.3189, 31.2953, 250),
    ("南翔古镇", 121.3189, 31.2953, 250),
    ("嘉定州桥", 121.2653, 31.3753, 200),
    ("上海汽车博物馆", 121.2236, 31.3589, 200),
    ("宝山顾村公园", 121.4236, 31.3453, 400),
    ("吴淞炮台", 121.5011, 31.3811, 200),
    ("杨浦滨江", 121.5311, 31.2589, 400),
    ("复兴岛", 121.5489, 31.2811, 250),
    ("共青森林公园", 121.5389, 31.3153, 400),
    ("上海国际时尚中心", 121.5236, 31.3189, 200),
    ("北外滩", 121.5011, 31.2589, 300),
    ("白玉兰广场", 121.5011, 31.2611, 150),
    ("提篮桥", 121.5089, 31.2553, 200),
    ("上海犹太难民纪念馆", 121.5103, 31.2553, 120),
    ("下海庙", 121.5089, 31.2536, 120),
    ("瑞虹新城", 121.4989, 31.2689, 250),
    ("临平路", 121.4911, 31.2689, 200),
    ("和平公园", 121.5011, 31.2711, 250),
    ("曲阳公园", 121.4911, 31.2836, 200),
    ("上海马戏城", 121.4511, 31.2789, 150),
    ("上海自然博物馆", 121.4611, 31.2389, 150),
    ("静安雕塑公园", 121.4689, 31.2311, 200),
    ("昌平路", 121.4486, 31.2353, 180),
    ("同乐坊", 121.4486, 31.2389, 150),
    ("江宁路", 121.4453, 31.2353, 200),
    ("长寿路", 121.4389, 31.2411, 250),
    ("玉佛寺", 121.4336, 31.2489, 150),
    ("上海站", 121.4553, 31.2489, 200),
    ("苏河湾", 121.4689, 31.2489, 250),
    ("四行仓库", 121.4789, 31.2489, 120),
    ("外白渡桥", 121.4911, 31.2511, 100),
    ("黄浦公园", 121.4911, 31.2411, 150),
    ("十六铺", 121.4989, 31.2311, 200),
    ("老码头", 121.5011, 31.2189, 150),
    ("世博轴", 121.4942, 31.1853, 300),
]


def meters_to_degree_delta(lat: float, meters: float) -> tuple[float, float]:
    """将米转换为约等于的经纬度偏移（近似，适用于上海纬度）。"""
    dlat = meters / 111_000
    dlon = meters / (111_000 * math.cos(math.radians(lat)))
    return dlat, dlon


def generate_grid_points(
    center_lon: float, center_lat: float, radius_m: float, n: int = 100
) -> list[tuple[float, float]]:
    """
    在以 (center_lon, center_lat) 为中心、半径约 radius_m 米的矩形区域内，
    生成 n 个均匀网格点（默认 100 个，10×10）。
    """
    dlat, dlon = meters_to_degree_delta(center_lat, radius_m)
    lon_min, lon_max = center_lon - dlon, center_lon + dlon
    lat_min, lat_max = center_lat - dlat, center_lat + dlat
    side = int(math.isqrt(n))
    points = []
    for i in range(side):
        for j in range(side):
            if len(points) >= n:
                break
            lon = lon_min + (lon_max - lon_min) * (i + 0.5) / side
            lat = lat_min + (lat_max - lat_min) * (j + 0.5) / side
            points.append((lon, lat))
    return points[:n]


def ensure_output_dir() -> None:
    """确保输出目录存在。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_landmarks_csv() -> None:
    """保存 100 个地标区域信息为 CSV。"""
    ensure_output_dir()
    with open(LANDMARKS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["landmark_name", "longitude", "latitude", "radius_m"])
        for name, lon, lat, radius in SHANGHAI_LANDMARKS:
            w.writerow([name, lon, lat, radius])
    print(f"  地标 CSV: {LANDMARKS_CSV_PATH}")


def save_landmarks_shp() -> Optional[str]:
    """保存 100 个地标中心点为 SHP。若缺少 pyshp 则返回错误信息。"""
    try:
        import shapefile
    except ImportError:
        return "未安装 pyshp，跳过地标 SHP。请执行: pip install pyshp"

    ensure_output_dir()
    w = shapefile.Writer(str(LANDMARKS_SHP_PATH), shapeType=shapefile.POINT)
    w.field("name", "C", size=80)
    w.field("lon", "N", size=14, decimal=6)
    w.field("lat", "N", size=14, decimal=6)
    w.field("radius_m", "N", size=8, decimal=0)
    for name, lon, lat, radius in SHANGHAI_LANDMARKS:
        w.point(lon, lat)
        w.record(name, round(lon, 6), round(lat, 6), radius)
    w.close()
    _write_prj(LANDMARKS_SHP_PATH.with_suffix(".prj"))
    print(f"  地标 SHP: {LANDMARKS_SHP_PATH}")
    return None


def save_points_csv() -> None:
    """保存每个地标区域的 100 个采样点为 CSV（带 _points 含义的文件名）。"""
    ensure_output_dir()
    with open(POINTS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["landmark_name", "longitude", "latitude", "point_index"])
        for name, lon, lat, radius in SHANGHAI_LANDMARKS:
            points = generate_grid_points(lon, lat, radius, n=100)
            for idx, (plon, plat) in enumerate(points):
                w.writerow([name, plon, plat, idx])
    print(f"  采样点 CSV: {POINTS_CSV_PATH}")


def save_points_shp() -> Optional[str]:
    """保存采样点为 SHP（文件名已带 _points 后缀）。若缺少 pyshp 则返回错误信息。"""
    try:
        import shapefile
    except ImportError:
        return "未安装 pyshp，跳过采样点 SHP。请执行: pip install pyshp"

    ensure_output_dir()
    w = shapefile.Writer(str(POINTS_SHP_PATH), shapeType=shapefile.POINT)
    w.field("landmark", "C", size=80)
    w.field("lon", "N", size=14, decimal=6)
    w.field("lat", "N", size=14, decimal=6)
    w.field("point_idx", "N", size=4, decimal=0)
    for name, lon, lat, radius in SHANGHAI_LANDMARKS:
        points = generate_grid_points(lon, lat, radius, n=100)
        for idx, (plon, plat) in enumerate(points):
            w.point(plon, plat)
            w.record(name, round(plon, 6), round(plat, 6), idx)
    w.close()
    _write_prj(POINTS_SHP_PATH.with_suffix(".prj"))
    print(f"  采样点 SHP: {POINTS_SHP_PATH}")
    return None


def _write_prj(prj_path: Path) -> None:
    """写入 WGS84 的 .prj 文件。"""
    wgs84 = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
    prj_path.write_text(wgs84, encoding="utf-8")


def main() -> None:
    print("输出目录:", OUTPUT_DIR)
    print("地标数量:", len(SHANGHAI_LANDMARKS))
    print("每区域点数: 100")
    print("总采样点数:", len(SHANGHAI_LANDMARKS) * 100)
    print()

    save_landmarks_csv()
    err = save_landmarks_shp()
    if err:
        print("  ", err)

    save_points_csv()
    err = save_points_shp()
    if err:
        print("  ", err)

    print("\n完成。")


if __name__ == "__main__":
    main()

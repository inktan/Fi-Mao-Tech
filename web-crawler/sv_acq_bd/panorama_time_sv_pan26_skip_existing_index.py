# -*- coding:utf-8 -*-
"""
基于 `panorama_time_new_linux_csvs.py` 的街景采集变体（默认输出目录 `sv_pan26`）。

在 `panorama_time_new_linux_csvs.py` 的基础上增加 **按已有图片推断已占用 index**：

- 处理每个 CSV 之前，扫描 **同级目录下输出子文件夹**（默认 `sv_pan26`）中已有图片；
- 对每个文件名（去掉扩展名）按 `_` 分割，**只取第一个片段**；若该片段为整数则视为已占用的 index（与 CSV 列对齐）；
- CSV 中 `index` 落在该集合中的行视为已有图，**只对剩余行**发起下载。

多 CSV 扫描仅检查根目录下一层子文件夹内**直接放置**的 `*.csv`（不递归更深层），以加快启动。
"""
import math
import json
import re
import requests
import os
from PIL import Image
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
import functools
from io import BytesIO
import time
import random
from typing import List, Optional

# ====================== 坐标转换相关（与原脚本保持一致） ======================
array1 = [75, 60, 45, 30, 15, 0]
array3 = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
array2 = [
    [-0.0015702102444, 111320.7020616939, 1704480524535203, -10338987376042340,
     26112667856603880, -35149669176653700, 26595700718403920,
     -10725012454188240, 1800819912950474, 82.5],
    [0.0008277824516172526, 111320.7020463578, 647795574.6671607,
     -4082003173.641316, 10774905663.51142, -15171875531.51559,
     12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
    [0.00337398766765, 111320.7020202162, 4481351.045890365,
     -23393751.19931662, 79682215.47186455, -115964993.2797253,
     97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
    [0.00220636496208, 111320.7020209128, 51751.86112841131,
     3796837.749470245, 992013.7397791013, -1221952.21711287,
     1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
    [-0.0003441963504368392, 111320.7020576856, 278.2353980772752,
     2485758.690035394, 6070.750963243378, 54821.18345352118,
     9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
    [-0.0003218135878613132, 111320.7020701615, 0.00369383431289,
     823725.6402795718, 0.46104986909093, 2351.343141331292,
     1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45]
]
array4 = [
    [1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331,
     200.9824383106796, -187.2403703815547, 91.6087516669843,
     -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
    [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289,
     96.32687599759846, -1.85204757529826, -59.36935905485877,
     47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
    [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616,
     59.74293618442277, 7.357984074871, -25.38371002664745,
     13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
    [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591,
     40.31678527705744, 0.65659298677277, -4.44255534477492,
     0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
    [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062,
     23.10934304144901, -0.00023663490511, -0.6321817810242,
     -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
    [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8,
     7.47137025468032, -0.00000353937994, -0.02145144861037,
     -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5]
]


def Convertor(x, y, param):
    T = param[0] + param[1] * abs(x)
    cC = abs(y) / param[9]
    cF = (
        param[2] + param[3] * cC + param[4] * cC * cC +
        param[5] * cC * cC * cC + param[6] * cC * cC * cC * cC +
        param[7] * cC * cC * cC * cC * cC +
        param[8] * cC * cC * cC * cC * cC * cC
    )
    T *= (-1 if x < 0 else 1)
    cF *= (-1 if y < 0 else 1)
    return T, cF


# 平面坐标转百度经纬度
def pointtolnglat(pointx, pointy):
    arr = []
    for i in range(len(array3)):
        if abs(pointy) >= array3[i]:
            arr = array4[i]
            break
    res = Convertor(abs(pointx), abs(pointy), arr)
    return [round(res[0], 6), round(res[1], 6)]


# 百度经纬度转平面坐标
def lnglattopoint(lng, lat):
    arr = []
    lat = 74 if lat > 74 else lat
    lat = -74 if lat < -74 else lat

    for i in range(len(array1)):
        if lat >= array1[i]:
            arr = array2[i]
            break

    if not arr:
        for i in range(len(array1))[::-1]:
            if lat <= -array1[i]:
                arr = array2[i]
                break

    res = Convertor(lng, lat, arr)
    return [res[0], res[1]]


# ====================== 网络与并发配置（与原脚本保持一致） ======================
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5
MIN_REQUEST_INTERVAL = 0.0

_session: Optional[requests.Session] = None
_last_request_time: float = 0.0


def _get_session() -> requests.Session:
    """每个进程懒加载一个全局 Session，用于复用连接。"""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _throttled_get(url: str, *, stream: bool = False, timeout: int = REQUEST_TIMEOUT):
    """
    带限速 + 简单重试的 GET。
    - 对 429 / 5xx 状态码会指数退避重试；
    - 对网络异常也会重试；
    - 其他 4xx 直接返回。
    """
    global _last_request_time
    sess = _get_session()

    for attempt in range(1, MAX_RETRIES + 1):
        # 简单的进程内限速
        if MIN_REQUEST_INTERVAL > 0:
            now = time.time()
            wait = _last_request_time + MIN_REQUEST_INTERVAL - now
            if wait > 0:
                time.sleep(wait)

        try:
            resp = sess.get(url, stream=stream, timeout=timeout)
            _last_request_time = time.time()

            # 成功
            if resp.status_code == 200:
                return resp

            # 对 429 / 5xx 做重试
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue

            # 其他状态直接返回
            return resp

        except requests.RequestException:
            _last_request_time = time.time()
            if attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue
            return None

    return None


def download_and_merge_streetview(timeLineId, x_count, y_count, save_file_path):
    final_img = Image.new('RGB', (512 * y_count, 512 * x_count), (0, 0, 0))

    for x in range(x_count):
        for y in range(y_count):
            url = (
                'https://mapsv1.bdimg.com/?qt=pdata&sid=' + str(timeLineId) +
                '&pos=' + str(x) + '_' + str(y) +
                '&z=' + str(resolution_ratio) +
                '&udt=20200825&from=PC&auth=GPJbXPMId1MK3NC4B41Mzx7H0%3DNMQDQ%3DuxLEELLENBEtw805wi09v7uvYgP1PcGCgYvjPuVtvYgPMGvgWv%40uVtvYgPPxRYuVtvYgP%40vYZcvWPCuVtvYgP%40ZPcPPuVtc3CuVteuxtf0wd0vyMFFMMFOyAupt66FcErZZWux&seckey=mx8n3s4BT%2BM5jF6vP0bY6%2Bm25GJG9bJAPCy40WbYcVI%3D%2CLObtdXnaK4xy2ePuTyzwbSgjY0lwTkDw27LrZ2b6EqVnuWsCWY8KRbk0pLU3O7nH3Bxrl6QDIDwn3mcxqW8ivuJSq9AWKTb3QWqDwXO1CjnfVgGjLX42xPm511xNwk-n-XPUVVZWEHCymx0r0rAvOnY4vCwIwhNdEUnVTGHwmiRVJeaHB6B6bIKynrJcZMVy'
            )
            response = _throttled_get(url, stream=True)
            if response is not None and response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                final_img.paste(img, (y * 512, x * 512))
            else:
                code = response.status_code if response is not None else "NO_RESPONSE"
                print(f"Failed to download image at ({x}, {y}), status code: {code}")

    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
    final_img.save(save_file_path)


def get_panoid(lng, lat):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = _throttled_get(url)
    if req is None or req.status_code != 200:
        return []
    try:
        data = json.loads(req.text)
    except json.JSONDecodeError:
        return []
    if not data:
        return []

    result = data.get('content')
    if not result or 'id' not in result:
        return []

    panoid = result['id']
    url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
    r = _throttled_get(url, stream=True)
    if r is None or r.status_code != 200:
        return []
    try:
        data = json.loads(r.text)
    except json.JSONDecodeError:
        return []

    if "content" not in data or not data["content"]:
        return []

    content0 = data["content"][0]
    timeLineIds = content0.get('TimeLine', [])
    Heading = content0.get('Heading')
    MoveDir = content0.get('MoveDir')
    NorthDir = content0.get('NorthDir')

    return [timeLineIds, Heading, MoveDir, NorthDir]


# ====================== 地点名称处理 ======================
BAIDU_GEOCODING_AK = r'h2pkOSJCmmInapyV11is4wOPNLjkr9ok'  # 百度地图 AK，也可直接写字符串如 "你的AK"


def _clean_place_name(raw: str) -> str:
    """
    清洗地点名称：
    - 去掉前缀中的“省”“市”等行政区划信息（粗略规则）；
    - 去除对文件名不友好的字符；
    - 返回适合用于文件名的一段短字符串。
    """
    if not raw:
        return ""

    name = str(raw).strip()

    # 简单规则：按常见分隔符拆分，去掉前两段可能是“省 / 市”
    for sep in [" ", "　", "-", "—", "_", "·"]:
        if sep in name:
            parts = [p for p in name.split(sep) if p]
            if len(parts) >= 2:
                # 丢弃前 1~2 段
                candidates = parts[2:] or parts[1:]
                name = sep.join(candidates) if candidates else parts[-1]
            break

    # 再按“省”“市”做一次截断（保留后半部分）
    for kw in ["省", "市", "自治区", "特别行政区"]:
        if kw in name:
            idx = name.find(kw)
            if idx != -1 and idx + 1 < len(name):
                name = name[idx + 1 :].lstrip()

    # 仅保留中英文、数字及部分安全符号
    name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff\-]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    # 限制长度，避免路径过长
    if len(name) > 40:
        name = name[:40]

    return name


def get_place_name_from_baidu(bd_lng: float, bd_lat: float) -> str:
    """
    通过百度逆地理编码接口获取地点信息，并清洗后返回用于文件名的地点字符串。

    使用说明：
    - 需要在环境变量 BAIDU_GEOCODING_AK 中配置百度地图 Web 服务的 ak；
    - 这里假定传入的坐标为 bd09 坐标（bd09ll）。
    """
    if not BAIDU_GEOCODING_AK:
        return ""

    url = (
        "https://api.map.baidu.com/reverse_geocoding/v3/"
        f"?ak={BAIDU_GEOCODING_AK}"
        # "&extensions_poi=1"
        # "&entire_poi=1"
        # "&sort_strategy=distance"
        "&output=json"
        "&coordtype=wgs84ll"
        f"&location={bd_lat},{bd_lng}"

    )
    resp = _throttled_get(url)
    if resp is None or resp.status_code != 200:
        return ""

    try:
        data = json.loads(resp.text)
    except json.JSONDecodeError:
        return ""

    if data.get("status") != 0:
        return ""

    result = data.get("result") or {}
    comp = result.get("addressComponent") or {}

    # 组合去掉“省、市”后的较细粒度地址：区 / 镇 / 街道 / 街道号
    parts = []
    for key in ["district", "town", "street", "street_number"]:
        val = comp.get(key)
        if val:
            parts.append(str(val))

    if not parts:
        formatted = result.get("formatted_address") or ""
        return _clean_place_name(formatted)

    raw_name = "".join(parts)
    return _clean_place_name(raw_name)


# ====================== 坐标系转换（与原脚本保持一致） ======================
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02_to_bd09(lng, lat):
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


# ====================== 业务逻辑 ======================
coordinate_point_category = 1
resolution_ratio = 4

# 扫描输出目录时视为图片的扩展名
_IMAGE_EXTS_FOR_INDEX_SCAN = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _segment_to_index_key(seg: str) -> Optional[str]:
    """若下划线分段整段为（非负）整数，则规范为与 CSV index 对齐的字符串，否则不参与匹配。"""
    s = seg.strip()
    if s.isdigit():
        return str(int(s))
    return None


def collect_occupied_indices_from_sv_folder(folder_out_path: str) -> set:
    """
    扫描 folder_out_path 下图片：去掉扩展名后按 '_' 分割，只取第一个片段；
    若该片段整段为非负整数，则加入集合（与 CSV 列 index 用 str(int) 对齐）。
    """
    occupied: set = set()
    if not os.path.isdir(folder_out_path):
        return occupied
    try:
        for name in os.listdir(folder_out_path):
            path = os.path.join(folder_out_path, name)
            if not os.path.isfile(path):
                continue
            if os.path.splitext(name)[1].lower() not in _IMAGE_EXTS_FOR_INDEX_SCAN:
                continue
            stem = os.path.splitext(name)[0]
            parts = stem.split("_")
            if not parts or not parts[0]:
                continue
            key = _segment_to_index_key(parts[0])
            if key is not None:
                occupied.add(key)
    except OSError:
        pass
    return occupied


def coord_convert(lng1, lat1):
    if coordinate_point_category == 1:
        result = wgs84_to_gcj02(lng1, lat1)
        result = gcj02_to_bd09(result[0], result[1])
        return lnglattopoint(result[0], result[1])
    elif coordinate_point_category == 5:
        return lnglattopoint(lng1, lat1)
    elif coordinate_point_category == 6:
        result = gcj02_to_bd09(lng1, lat1)
        return lnglattopoint(result[0], result[1])


def process_row_single_folder(
    row,
    folder_out_path: str,
    existing_index_prefixes: Optional[set] = None,
) -> str:
    """
    处理单行：CSV 列 longitude, latitude, index。
    所有图片直接统一保存在给定的 folder_out_path。
    若 existing_index_prefixes 中包含本行 index 的字符串形式，则跳过下载。
    """
    x_count = int(2 ** (resolution_ratio - 2))
    y_count = int(x_count * 2)

    # 显式转换为 int，避免浮点或字符串参与文件名
    index = int(row["index"])
    index_key = str(index)
    lng = row["longitude"]
    lat = row["latitude"]

    if existing_index_prefixes is not None and index_key in existing_index_prefixes:
        return f"{index}: Skip (index already in folder)."

    try:
        tar_lng_lat = coord_convert(lng, lat)
        panoidInfos = get_panoid(tar_lng_lat[0], tar_lng_lat[1])

        if not panoidInfos or len(panoidInfos[0]) == 0:
            return f"{index}: No panorama found."

        timeLineIds = panoidInfos[0]
        heading = panoidInfos[1]

        # 使用百度逆地理接口获取经纬度对应的地点信息（去除省、市等）
        # place_name = get_place_name_from_baidu(tar_lng_lat[0], tar_lng_lat[1])
        place_name = get_place_name_from_baidu(lng, lat)
        p = timeLineIds[0]
        year = int(p["TimeLine"][:4])
        month = int(p["TimeLine"][4:])
        pano_id = p["ID"]

        os.makedirs(folder_out_path, exist_ok=True)

        # 组装更丰富的文件名：索引、经纬度、panoid、朝向、年月、地点名称
        if place_name:
            filename = f"{index}_{lng}_{lat}_{pano_id}_{heading}_{year}_{month}_{place_name}.jpg"
        else:
            filename = f"{index}_{lng}_{lat}_{pano_id}_{heading}_{year}_{month}.jpg"

        save_file_path = os.path.join(folder_out_path, filename)

        if os.path.exists(save_file_path):
            return f"{index}: Already exists."

        download_and_merge_streetview(pano_id, x_count, y_count, save_file_path)
        return f"{index}: Downloaded."

    except Exception as e:
        return f"{index}: Error {e}"
 
 
def process_single_csv(
    csv_path: str,
    start_idx: int = 0,
    end_idx: Optional[int] = None,
    num_processes: int = 5,
    sv_folder_name: str = "sv_pan26",
) -> None:
    """
    处理单个 CSV：
    - 在该 CSV 所在目录下创建/复用输出文件夹（默认 sv_pan26）；
    - 使用多进程下载。
    """
    print(
        f"[CSV_PROCESS][START] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"csv={csv_path}, start_idx={start_idx}, end_idx={end_idx}"
    )

    csv_dir = os.path.dirname(csv_path)
    folder_out_path = os.path.join(csv_dir, sv_folder_name)
    df = pd.read_csv(csv_path)
    required = ["longitude", "latitude", "index"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"CSV 缺少列: {col}，当前列: {list(df.columns)}")
    if end_idx is None:
        end_idx = len(df)
    start_idx = max(0, start_idx)
    end_idx = min(end_idx, len(df))
    if start_idx >= end_idx:
        print(f"[SKIP] {csv_path} 行范围为空，start_idx={start_idx}, end_idx={end_idx}")
        print(
            f"[CSV_PROCESS][END  ] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
            f"csv={csv_path} (empty range)"
        )
        return
    target_df = df.iloc[start_idx:end_idx].copy()
    print(f"[CSV] {csv_path}")
    print(df.shape, "行范围:", start_idx, "~", end_idx, "共", len(target_df), "行")

    occupied_indices = collect_occupied_indices_from_sv_folder(folder_out_path)
    idx_as_key = target_df["index"].map(lambda v: str(int(v)))
    remaining_df = target_df[~idx_as_key.isin(occupied_indices)]
    skipped_n = len(target_df) - len(remaining_df)
    print(
        f"[INDEX_SKIP] 子文件夹 {folder_out_path} 中图片名（`_` 首段）推断已占用 index 共 "
        f"{len(occupied_indices)} 个；本批次跳过 {skipped_n} 行，待下载 {len(remaining_df)} 行。"
    )

    if remaining_df.empty:
        print(
            f"[CSV_PROCESS][END  ] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
            f"csv={csv_path}, 无需下载（均在已占用集合中）"
        )
        return

    func = functools.partial(
        process_row_single_folder,
        folder_out_path=folder_out_path,
        existing_index_prefixes=occupied_indices,
    )
    rows = [row for _, row in remaining_df.iterrows()]

    processed = 0
    with Pool(processes=num_processes) as pool:
        for _ in tqdm(
            pool.imap_unordered(func, rows),
            total=len(rows),
            desc=f"Downloading ({os.path.basename(csv_path)})",
        ):
            processed += 1

    print(
        f"[CSV_PROCESS][END  ] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"csv={csv_path}, processed={processed}"
    )


# ====================== 遍历 CSV（仅下一层子目录） ======================


def scan_csv_files_immediate_subdirs(root_dir: str) -> List[str]:
    """
    仅扫描 root_dir 的「下一层」各子目录中、直接位于该子目录下的 *.csv。
    不递归更深层目录，也不在 root_dir 根级查找 CSV，用于海量目录树时加速启动枚举。
    """
    result: List[str] = []
    try:
        sub_names = sorted(os.listdir(root_dir))
    except OSError:
        return result

    for name in sub_names:
        sub_path = os.path.join(root_dir, name)
        if not os.path.isdir(sub_path):
            continue
        try:
            for fn in os.listdir(sub_path):
                if fn.lower().endswith(".csv"):
                    result.append(os.path.join(sub_path, fn))
        except OSError:
            continue

    result.sort()
    return result


def main_multi_csv(
    root_dir: str,
    num_processes: int = 5,
    sv_folder_name: str = "sv_pan26",
) -> None:
    """枚举 root_dir 下一层子目录中的 CSV，依次下载。"""
    csv_files = scan_csv_files_immediate_subdirs(root_dir)

    csv_files = [r'e:\work\sv_temp\test_network_10m_Optimized.csv']

    if not csv_files:
        print(f"[INFO] 在目录 {root_dir} 下未发现任何 CSV 文件。")
        return

    total = len(csv_files)
    print(f"[INFO] 共发现 {total} 个 CSV 文件。")

    for idx, csv_path in enumerate(csv_files):
        print(f"[RUN ] ({idx + 1}/{total}) {csv_path}")
        try:
            process_single_csv(
                csv_path=csv_path,
                start_idx=0,
                end_idx=None,
                num_processes=num_processes,
                sv_folder_name=sv_folder_name,
            )
        except Exception as e:
            print(f"[ERROR] 处理 CSV 失败: {csv_path}, error={e}")
            break

    print("[DONE] 所有可处理的 CSV 已完成当前批次下载。")


if __name__ == '__main__':
    # ========== 请按需修改以下参数 ==========
    # 1. 根目录：仅在「下一层子文件夹」内查找直接放置的 *.csv（不递归更深、根下无 CSV）
    ROOT_DIR = r'H:\_50m_point'  # TODO: 换成你的根目录

    # 2. 多进程进程数（建议根据 CPU 与网络情况调整）
    NUM_PROCESSES = 30

    # 3. 每个 CSV 同级目录下用于保存图片的文件夹名
    SV_FOLDER_NAME = 'sv_pan26'

    main_multi_csv(
        root_dir=ROOT_DIR,
        num_processes=NUM_PROCESSES,
        sv_folder_name=SV_FOLDER_NAME,
    )

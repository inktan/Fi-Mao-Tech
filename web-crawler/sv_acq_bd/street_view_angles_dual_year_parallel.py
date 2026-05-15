# -*- coding: utf-8 -*-
"""
双年份百度街景（pr3d）四视角下载 — 基于 street_view_angles_parallel.py：

- 固定两个目标年份：2022、2016，分别写入子目录 svi_degrees_2022 / svi_degrees_2016
- 时间轴上无该年时，选取日历年份距离最近的一条；距离相同时优先较新年份
- 同一行若两个目标解析到同一 TimeLine，每视角只下载一次并复制到另一目录，减少请求
- 其余策略与原脚本一致：多进程、Session、_throttled_get、道路名 CSV
"""
import functools
import json
import os
import random
import shutil
import time
from multiprocessing import Pool, Lock
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from tqdm import tqdm

from coordinate_converter import transBmap, transCoordinateSystem

REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5
MIN_REQUEST_INTERVAL = 0.0

# 目标年份（可改常量）；输出目录为 folder_out_path/svi_degrees_{year}/
TARGET_YEARS: Tuple[int, ...] = (2022, 2016)

_session: Optional[requests.Session] = None
_last_request_time: float = 0.0
_road_name_lock: Any = None


def init_worker(road_lock: Lock) -> None:
    global _road_name_lock
    _road_name_lock = road_lock


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def _throttled_get(url: str, *, stream: bool = False, timeout: int = REQUEST_TIMEOUT, **kwargs):
    global _last_request_time
    sess = _get_session()

    for attempt in range(1, MAX_RETRIES + 1):
        if MIN_REQUEST_INTERVAL > 0:
            now = time.time()
            wait = _last_request_time + MIN_REQUEST_INTERVAL - now
            if wait > 0:
                time.sleep(wait)

        try:
            resp = sess.get(url, stream=stream, timeout=timeout, **kwargs)
            _last_request_time = time.time()

            if resp.status_code == 200:
                return resp

            if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue

            return resp

        except requests.RequestException:
            _last_request_time = time.time()
            if attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue
            return None

    return None


def download_baidu_panorama(
    save_path: str,
    panoid: str,
    fovy: int = 90,
    heading: float = 0,
    pitch: int = 0,
    width: int = 960,
    height: int = 720,
) -> bool:
    base_url = "https://mapsv0.bdimg.com/"
    params = {
        "qt": "pr3d",
        "fovy": fovy,
        "quality": 100,
        "panoid": panoid,
        "heading": heading,
        "pitch": pitch,
        "width": width,
        "height": height,
        "from": "PC",
        "auth": "PSDz2ONTUDcDv5EIHUSCCWSafAOBOX80uxNEHRTBEVxt1W4931688FB2Afy9GUIsxCwxz6ZwWvvkGcuVtvvhguVtvyheuzBtyEOIxXwvCQMuHTxtFQXmE21w8wkvOAuGhrVFcEv%40vcuVtvc3CuVtvcPPuxtwf2wvOAUIuIswVHa2Dp5IC%40BvhgMuzVVtvrMhuBxLRBtIff%3DfxXwegvcguxNEHRTBBTH",
        "seckey": "YSNoYBXRFcZK%2B2kRoOr3Ytr9QIkfl7VXc%2FZkupfasb8%3D%2CEkQ3gDtGyBiGnYmEbAfewqzVS3S5F7OJ9E20wGJo4318MZPiCt_4uPW29cbO50CIN9VOskJsTu5iPR80SPgIpPC0xgz-MiowW_XudfoltzsGJdOZtz_cNaLyibJlSVcg0AbA5foBC0X5KQCAbrwwRV7-OkgW2m87u9irYufqlvproZhrVf3xQD_g9nuWGQVl",
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        response = _throttled_get(base_url, stream=False, params=params, headers=headers)
        if response is None or response.status_code != 200:
            return False
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except OSError:
        return False


class Panorama:
    def __init__(self, pano, year_month: str, year: int, month: int):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month


def get_panoid(lng, lat, bound, sv_id, folder_out_path):
    url = "https://mapsv0.bdimg.com/?qt=qsdata&x=" + str(lng) + "&y=" + str(lat)
    req = _throttled_get(url)
    if req is None or req.status_code != 200:
        return []
    try:
        data = json.loads(req.text)
    except json.JSONDecodeError:
        return []

    if data is None or "content" not in data:
        return []

    result = data["content"]
    RoadName = result.get("RoadName", "")
    streetname = sv_id + "," + bound + "," + str(RoadName) + "\n"
    road_csv = os.path.join(folder_out_path, "road_name_results.csv")

    if _road_name_lock is not None:
        with _road_name_lock:
            os.makedirs(folder_out_path, exist_ok=True)
            with open(road_csv, "a", encoding="utf-8") as f:
                f.write(streetname)
    else:
        os.makedirs(folder_out_path, exist_ok=True)
        with open(road_csv, "a", encoding="utf-8") as f:
            f.write(streetname)

    panoid = result.get("id")
    if not panoid:
        return []

    url = "https://mapsv0.bdimg.com/?qt=sdata&sid=" + panoid + "&pc=1"
    r = _throttled_get(url, stream=False)
    if r is None or r.status_code != 200:
        return []
    try:
        data = json.loads(r.text)
    except json.JSONDecodeError:
        return []

    if "content" not in data or not data["content"]:
        return []

    content0 = data["content"][0]
    time_line_ids = content0.get("TimeLine", [])
    heading = content0.get("Heading")
    move_dir = content0.get("MoveDir")
    north_dir = content0.get("NorthDir")
    return [time_line_ids, heading, move_dir, north_dir]


coordinate_point_category = 1


def coord_convert(lng1, lat1):
    if coordinate_point_category == 1:
        result = transCoordinateSystem.wgs84_to_gcj02(lng1, lat1)
        result = transCoordinateSystem.gcj02_to_bd09(result[0], result[1])
        return transBmap.lnglattopoint(result[0], result[1])
    if coordinate_point_category == 5:
        return transBmap.lnglattopoint(lng1, lat1)
    if coordinate_point_category == 6:
        result = transCoordinateSystem.gcj02_to_bd09(lng1, lat1)
        return transBmap.lnglattopoint(result[0], result[1])
    return transBmap.lnglattopoint(lng1, lat1)


def select_panorama_for_target_year(panoramas: List[Panorama], target_year: int) -> Optional[Panorama]:
    """有目标年则取该年内最新月份；否则取日历年份最近的一条，等距时取较新年份。"""
    if not panoramas:
        return None
    same_year = [p for p in panoramas if p.year == target_year]
    if same_year:
        return max(same_year, key=lambda p: p.year_month)
    return min(panoramas, key=lambda p: (abs(p.year - target_year), -p.year))


def _append_year_log(folder_out_path: str, line: str) -> None:
    log_path = os.path.join(folder_out_path, "dual_year_resolution.csv")
    if _road_name_lock is not None:
        with _road_name_lock:
            os.makedirs(folder_out_path, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
    else:
        os.makedirs(folder_out_path, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)


def process_row(row, folder_out_path: str) -> str:
    """每行：解析时间轴，为每个目标年选全景并下载四视角；目录按目标年分文件夹。"""
    row_key = int(row["index"])
    lng = row["longitude"]
    lat = row["latitude"]

    try:
        tar_lng_lat = coord_convert(lng, lat)
        panoid_infos = get_panoid(
            tar_lng_lat[0], tar_lng_lat[1], str(lng) + "_" + str(lat), str(row_key), folder_out_path
        )
        if not panoid_infos:
            return f"{row_key}: no panoid data"

        time_line_ids = panoid_infos[0]
        if not time_line_ids:
            return f"{row_key}: empty timeline"

        heading = panoid_infos[1]
        if heading is None:
            return f"{row_key}: no heading"

        panoramas: List[Panorama] = []
        for time_line_id in time_line_ids:
            tl = time_line_id["TimeLine"]
            panoramas.append(Panorama(time_line_id, tl, int(tl[:4]), int(tl[4:])))

        chosen: List[Tuple[int, Panorama]] = []
        for ty in TARGET_YEARS:
            p = select_panorama_for_target_year(panoramas, ty)
            if p is None:
                return f"{row_key}: no panorama for target {ty}"
            chosen.append((ty, p))

        option1 = (heading + 90) % 360
        option2 = (heading + 180) % 360
        option3 = (heading + 270) % 360
        option4 = (heading + 0) % 360
        headings = [round(x, 1) for x in (option1, option2, option3, option4)]

        # 记录目标年 -> 实际使用的年月
        for ty, p in chosen:
            log_line = f"{row_key},{lng},{lat},{ty},{p.year},{p.month},{p.year_month},{p.pano.get('ID','')}\n"
            _append_year_log(folder_out_path, log_line)

        # (目标年, Panorama) 按 pano ID + TimeLine 去重下载
        unique_key_to_targets: Dict[Tuple[str, str], List[int]] = {}
        for ty, p in chosen:
            key = (str(p.pano["ID"]), p.year_month)
            unique_key_to_targets.setdefault(key, []).append(ty)

        for (_pano_id, time_line), target_years in unique_key_to_targets.items():
            p = next(pp for ty, pp in chosen if (str(pp.pano["ID"]), pp.year_month) == (_pano_id, time_line))
            pano_id = p.pano["ID"]

            for option in headings:
                primary_ty = target_years[0]
                pic_dir = os.path.join(folder_out_path, f"svi_degrees_{primary_ty}")
                os.makedirs(pic_dir, exist_ok=True)
                primary_path = os.path.join(
                    pic_dir,
                    f"{row_key}_{lng}_{lat}_{int(option)}_{time_line}.jpg",
                )

                if not os.path.exists(primary_path):
                    ok = download_baidu_panorama(
                        save_path=primary_path,
                        panoid=pano_id,
                        fovy=90,
                        heading=option,
                        pitch=0,
                        width=960,
                        height=720,
                    )
                    if not ok:
                        return f"{row_key}: download failed ty={primary_ty} heading {option}"

                for other_ty in target_years[1:]:
                    other_dir = os.path.join(folder_out_path, f"svi_degrees_{other_ty}")
                    os.makedirs(other_dir, exist_ok=True)
                    other_path = os.path.join(
                        other_dir,
                        f"{row_key}_{lng}_{lat}_{int(option)}_{time_line}.jpg",
                    )
                    if not os.path.exists(other_path):
                        try:
                            shutil.copy2(primary_path, other_path)
                        except OSError as e:
                            return f"{row_key}: copy failed {e}"

        return f"{row_key}: ok"

    except Exception as e:
        return f"{row_key}: error {e}"


def process_csv(
    csv_path: str,
    folder_out_path: str,
    num_processes: int = 8,
    start_idx: int = 0,
    end_idx: Optional[int] = None,
) -> None:
    os.makedirs(folder_out_path, exist_ok=True)

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
        print(f"[SKIP] 行范围为空 start_idx={start_idx}, end_idx={end_idx}")
        return

    target_df = df.iloc[start_idx:end_idx]
    print(df.shape, "行范围:", start_idx, "~", end_idx, "共", len(target_df), "行")
    print("目标年份 -> 子目录:", [f"svi_degrees_{y}" for y in TARGET_YEARS])

    log_path = os.path.join(folder_out_path, "dual_year_resolution.csv")
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("index,longitude,latitude,target_year,actual_year,actual_month,time_line,pano_id\n")

    rows = [row for _, row in target_df.iterrows()]
    func = functools.partial(process_row, folder_out_path=folder_out_path)
    road_lock = Lock()

    with Pool(processes=num_processes, initializer=init_worker, initargs=(road_lock,)) as pool:
        for _ in tqdm(
            pool.imap_unordered(func, rows),
            total=len(rows),
            desc="street_view dual-year (pr3d)",
        ):
            pass


def main(csv_path: str, folder_out_path: str, num_processes: int = 8) -> None:
    process_csv(csv_path, folder_out_path, num_processes=num_processes)


if __name__ == "__main__":
    csv_path = r"e:\work\sv_yyy\_network_10m_Optimized.csv"
    folder_out_path = r"e:\work\sv_yyy\sv_degrees_dual_year"
    NUM_PROCESSES = 16

    main(csv_path, folder_out_path, num_processes=NUM_PROCESSES)

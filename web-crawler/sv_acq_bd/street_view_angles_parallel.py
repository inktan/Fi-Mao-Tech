# -*- coding: utf-8 -*-
"""
四视角百度街景（pr3d）下载脚本 — 与 panorama_time_new_linux_csvs.py 对齐的加速策略：

- 多进程并行（Pool + imap_unordered）
- 每进程复用 requests.Session（连接池）
- 带退避的 _throttled_get，与 csvs 脚本同类重试逻辑
- 小图直接写入 response.content，避免 1KB 分块读盘

CSV 需含列：longitude, latitude, index（与 panorama_time_new_linux_csvs 一致）。
"""
import json
import os
import random
import time
import functools
from multiprocessing import Pool, Lock
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
import requests
from tqdm import tqdm

from coordinate_converter import transBmap, transCoordinateSystem

# ====================== 网络（与 panorama_time_new_linux_csvs 对齐）======================
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5
MIN_REQUEST_INTERVAL = 0.0

_session: Optional[requests.Session] = None
_last_request_time: float = 0.0
_road_name_lock: Any = None


def init_worker(road_lock: Lock) -> None:
    """Pool 子进程入口：绑定道路名 CSV 的写入锁。"""
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
    def __init__(self, pano, year_month, year, month):
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
# coordinate_point_category = 5
# coordinate_point_category = 6


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


def process_row(row, folder_out_path: str) -> str:
    """处理单行：查询 panoid 并下载四个朝向 pr3d 图。"""
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
            panoramas.append(
                Panorama(time_line_id, tl, int(tl[:4]), int(tl[4:]))
            )

        filtered_panoramas = panoramas

        pic_path = os.path.join(folder_out_path, "svi_degrees")
        os.makedirs(pic_path, exist_ok=True)

        for i in [0]:
            pano_id = filtered_panoramas[i].pano["ID"]
            time_line = filtered_panoramas[i].pano["TimeLine"]

            option1 = (heading + 90) % 360
            option2 = (heading + 180) % 360
            option3 = (heading + 270) % 360
            option4 = (heading + 0) % 360

            for option in [option1, option2, option3, option4]:
                option = round(option, 1)
                save_file_path = os.path.join(
                    pic_path,
                    f"{row_key}_{lng}_{lat}_{int(option)}_{time_line}.jpg",
                )

                if os.path.exists(save_file_path):
                    continue

                ok = download_baidu_panorama(
                    save_path=save_file_path,
                    panoid=pano_id,
                    fovy=90,
                    heading=option,
                    pitch=0,
                    width=960,
                    height=720,
                )
                if not ok:
                    return f"{row_key}: download failed at heading {option}"

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

    rows = [row for _, row in target_df.iterrows()]
    func = functools.partial(process_row, folder_out_path=folder_out_path)
    road_lock = Lock()

    with Pool(processes=num_processes, initializer=init_worker, initargs=(road_lock,)) as pool:
        for _ in tqdm(
            pool.imap_unordered(func, rows),
            total=len(rows),
            desc="street_view_angles (pr3d)",
        ):
            pass


def main(csv_path: str, folder_out_path: str, num_processes: int = 8) -> None:
    process_csv(csv_path, folder_out_path, num_processes=num_processes)


if __name__ == "__main__":
    # 与 panorama_time_new_linux_csvs 类似：按机器与带宽调高进程数
    csv_path = r"e:\work\sv_Celiaaa\城区范围_network_100m_Optimized.csv"
    folder_out_path = r"e:\work\sv_Celiaaa\sv_degrees"
    NUM_PROCESSES = 16

    main(csv_path, folder_out_path, num_processes=NUM_PROCESSES)

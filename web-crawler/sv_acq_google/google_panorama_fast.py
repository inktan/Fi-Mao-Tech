# -*- coding: utf-8 -*-
"""
Google 街景全景下载（提速版）。

相对 google_panorama_new.py 的优化思路（对齐 sv_acq_bd 里多进程 + 连接复用思路）：
1. 多进程：按 CSV 行并行，每行独立完成检索 + 拼图；
2. 进程内 requests.Session：检索接口复用 TCP 连接；
3. 单张全景多瓦片：ThreadPoolExecutor + 每线程独立 Session 并行拉取瓦片（I/O 密集）；
4. 有限次重试 + 指数退避，避免原版 while True 长时间阻塞。

测试 CSV 默认：test_network_10m_Optimized_top5_osm_ids.csv
保存文件名：{osm_id}_ 作为前缀（其后接经纬度、panoid、朝向、年月等）。
"""
from __future__ import annotations

import itertools
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from io import BytesIO
from multiprocessing import Pool
from typing import Any, Generator, Optional, Tuple

import pandas as pd
import requests
from PIL import Image
from tqdm import tqdm

# ----------------------------- 可调参数 -----------------------------
INPUT_CSV = r"e:\work\四个街道\_network_union_75m_Optimized.csv"
OUTPUT_DIR = r"e:\work\四个街道\google_pano"
ZOOM = 4

NUM_ROW_PROCESSES = 6
MAX_TILE_WORKERS = 24

REQUEST_TIMEOUT = 15
MAX_RETRIES = 4
RETRY_BACKOFF_BASE = 0.4
MIN_REQUEST_INTERVAL = 0.0

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# ----------------------------- 瓦片 / URL（与原版一致） -----------------------------
@dataclass
class TileInfo:
    x: int
    y: int
    fileurl: str


def get_width_and_height_from_zoom(zoom: int) -> Tuple[int, int]:
    return 2**zoom, 2 ** (zoom - 1)


def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    return (
        "https://streetviewpixels-pa.googleapis.com/v1/tile"
        f"?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}"
    )


def iter_tile_info(pano_id: str, zoom: int) -> Generator[TileInfo, None, None]:
    width, height = get_width_and_height_from_zoom(zoom)
    for x, y in itertools.product(range(width), range(height)):
        yield TileInfo(x=x, y=y, fileurl=make_download_url(pano_id, zoom, x, y))


def make_search_url(lat: float, lon: float) -> str:
    return (
        "https://maps.googleapis.com/maps/api/js/"
        "GeoPhotoService.SingleImageSearch"
        "?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10"
        "!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4"
        "!1e8!1e6!5m1!1e2!6m1!1e2"
        "&callback=_xdc_._v2mub5"
    ).format(lat, lon)


# ----------------------------- HTTP：Session + 重试 -----------------------------
_proc_session: Optional[requests.Session] = None
_last_req_ts: float = 0.0
_tls = threading.local()


def _get_proc_session() -> requests.Session:
    global _proc_session
    if _proc_session is None:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        _proc_session = s
    return _proc_session


def _get_thread_session() -> requests.Session:
    s = getattr(_tls, "session", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        _tls.session = s
    return s


def _throttled_get(
    session: requests.Session,
    url: str,
    *,
    stream: bool = False,
) -> Optional[requests.Response]:
    global _last_req_ts
    for attempt in range(1, MAX_RETRIES + 1):
        if MIN_REQUEST_INTERVAL > 0:
            now = time.time()
            wait = _last_req_ts + MIN_REQUEST_INTERVAL - now
            if wait > 0:
                time.sleep(wait)
        try:
            resp = session.get(url, stream=stream, timeout=REQUEST_TIMEOUT)
            _last_req_ts = time.time()
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random()))
                continue
            return resp
        except requests.RequestException:
            _last_req_ts = time.time()
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random()))
                continue
            return None
    return None


def search_request(lat: float, lon: float) -> Optional[requests.Response]:
    url = make_search_url(lat, lon)
    return _throttled_get(_get_proc_session(), url, stream=False)


# ----------------------------- 解析 panoid（与原版一致） -----------------------------
def panoids_from_response(text: str, closest: bool = False, disp: bool = False):
    pans = re.findall(
        r'\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+).*?\],\s*\[(-?[0-9]+\.[0-9]+).*?\[(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\]',
        text,
    )
    pans = [
        {
            "panoid": p[0],
            "lat": float(p[1]),
            "lon": float(p[2]),
            "pitch": float(p[3]),
            "heading": float(p[4]),
            "fov01": float(p[5]),
            "fov02": float(p[6]),
        }
        for p in pans
    ]
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    if not pans:
        return []

    dates = re.findall(r"([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]", text)
    dates = [list(d)[1:] for d in dates]

    if len(dates) > 0:
        dates = [[int(v) for v in d] for d in dates]
        dates = [d for d in dates if 1 <= d[1] <= 12]
        year, month = dates.pop(-1)
        pans[0].update({"year": year, "month": month})
        dates.reverse()
        for i, (yy, mm) in enumerate(dates):
            pans[-1 - i].update({"year": yy, "month": mm})

    def _sort_key(x: dict):
        if "year" in x:
            return (-x["year"], -x["month"])
        return (float("inf"), float("inf"))

    pans.sort(key=_sort_key)

    if closest:
        return [pans[i] for i in range(len(dates))]
    return pans


# ----------------------------- 并行下载瓦片并拼图 -----------------------------
def _download_single_tile(task: Tuple[str, int, int, int]) -> Tuple[int, int, Image.Image]:
    pano_id, zoom, x, y = task
    url = make_download_url(pano_id, zoom, x, y)
    sess = _get_thread_session()
    resp = _throttled_get(sess, url, stream=False)
    if resp is None or resp.status_code != 200:
        raise RuntimeError(f"tile ({x},{y}) status={getattr(resp, 'status_code', None)}")
    return x, y, Image.open(BytesIO(resp.content))


def get_panorama_parallel(pano_id: str, zoom: int, max_workers: int) -> Image.Image:
    tile_width = tile_height = 512
    total_w, total_h = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_w * tile_width, total_h * tile_height))
    tasks = [(pano_id, zoom, x, y) for x, y in itertools.product(range(total_w), range(total_h))]

    workers = min(max_workers, max(1, len(tasks)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_download_single_tile, t): t for t in tasks}
        for fut in as_completed(futures):
            x, y, im = fut.result()
            panorama.paste(im, (x * tile_width, y * tile_height))
    return panorama


def _safe_osm_id(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "unknown"
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        s = str(value).strip()
        return re.sub(r"[^\w\-.]", "_", s) or "unknown"


# ----------------------------- 子进程：处理一行 -----------------------------
def process_row(task: Tuple[dict, str, int, int]) -> str:
    """
    task: (row_dict, output_dir, zoom, max_tile_workers)
    """
    row, output_dir, zoom, max_tile_workers = task
    os.makedirs(output_dir, exist_ok=True)

    global _proc_session
    _proc_session = None

    try:
        lon = float(row["longitude"])
        lat = float(row["latitude"])
    except (KeyError, TypeError, ValueError) as e:
        return f"skip: bad lon/lat ({e})"

    colmap = {k.lower(): k for k in row}
    osm_key = colmap.get("osm_id")
    if not osm_key:
        return "skip: no osm_id column"
    osm_part = _safe_osm_id(row[osm_key])

    idx_part = ""
    if "index" in row and not (isinstance(row["index"], float) and pd.isna(row["index"])):
        try:
            idx_part = str(int(float(row["index"])))
        except (TypeError, ValueError):
            idx_part = str(row["index"]).strip()
        idx_part = f"{idx_part}_"

    resp = search_request(lat, lon)
    if resp is None:
        return f"{osm_part}: search no response"
    try:
        panoids = panoids_from_response(resp.text)
    except Exception as e:
        return f"{osm_part}: parse error {e}"

    if not panoids:
        return f"{osm_part}: no panorama"

    for pano in panoids:
        try:
            year = int(pano.get("year", 0))
            month = int(pano.get("month", 0))
        except (TypeError, ValueError):
            year, month = 0, 0
        heading = pano.get("heading", 0)
        panoid = pano["panoid"]
        # 文件名：osm_id 为第一段
        fname = (
            f"{osm_part}_{idx_part}{lon}_{lat}_{panoid}_{heading}_{year}_{month}.jpg"
        )
        save_path = os.path.join(output_dir, fname)
        if os.path.exists(save_path):
            return f"{osm_part}: exists"

        try:
            image = get_panorama_parallel(panoid, zoom, max_tile_workers)
            image.save(save_path, quality=92)
            return f"{osm_part}: ok -> {fname}"
        except Exception as e:
            if os.path.isfile(save_path):
                try:
                    os.remove(save_path)
                except OSError:
                    pass
            continue

    return f"{osm_part}: all pano attempts failed"


def _build_tasks(df: pd.DataFrame, output_dir: str, zoom: int, max_tile_workers: int):
    rows = []
    for _, row in df.iterrows():
        rows.append((row.to_dict(), output_dir, zoom, max_tile_workers))
    return rows


def main() -> None:
    if not os.path.isfile(INPUT_CSV):
        raise FileNotFoundError(f"找不到 CSV：{INPUT_CSV}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    for col in ("longitude", "latitude"):
        if col not in df.columns:
            raise ValueError(f"CSV 缺少列 {col}，当前：{list(df.columns)}")

    lower = {c.lower(): c for c in df.columns}
    if "osm_id" not in lower:
        raise ValueError(f"CSV 缺少 osm_id 列，当前：{list(df.columns)}")

    tasks = _build_tasks(df, OUTPUT_DIR, ZOOM, MAX_TILE_WORKERS)
    print(f"rows={len(tasks)} processes={NUM_ROW_PROCESSES} tile_workers={MAX_TILE_WORKERS} zoom={ZOOM}")
    print(f"out={OUTPUT_DIR}")

    worker = process_row
    with Pool(processes=NUM_ROW_PROCESSES) as pool:
        for _ in tqdm(
            pool.imap_unordered(worker, tasks),
            total=len(tasks),
            desc="google pano",
        ):
            pass


if __name__ == "__main__":
    main()

# -*- coding:utf-8 -*-
"""
基于地标 CSV 的街景采集（角度图，多 CSV 版本）。

目标：将原 `street_view_angles.py` 改造成与 `panorama_time_new_linux_csvs.py`
一致的批处理框架：
- 递归遍历 root_dir 下所有 CSV
- 每个 CSV 同级目录下创建统一输出文件夹（不再按点位建子目录）
- 使用进度文件做简单断点续传（按 CSV/行区间）
- 使用多进程提高下载效率
"""

import json
import os
import random
import time
import functools
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from tqdm import tqdm

from coordinate_converter import transBmap, transCoordinateSystem

# ====================== 网络与并发配置（参考 panorama_time_new_linux_csvs.py） ======================
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
        if MIN_REQUEST_INTERVAL > 0:
            now = time.time()
            wait = _last_request_time + MIN_REQUEST_INTERVAL - now
            if wait > 0:
                time.sleep(wait)

        try:
            resp = sess.get(url, stream=stream, timeout=timeout)
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
    *,
    fovy: int = 90,
    heading: float = 0,
    pitch: float = 0,
    width: int = 960,
    height: int = 720,
) -> bool:
    """
    下载百度街景角度图（pr3d）并保存到本地。
    """
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
        # 保持与原脚本一致（历史参数）
        "auth": (
            "PSDz2ONTUDcDv5EIHUSCCWSafAOBOX80uxNEHRTBEVxt1W4931688FB2Afy9GUIsxCwxz6ZwWvvkGcuVtvvhguVtvyheuzBtyEOIxXwvCQMuHTxtFQXmE21w8wkvOAuGhrVFcEv%40vcuVtvc3CuVtvcPPuxtwf2wvOAUIuIswVHa2Dp5IC%40BvhgMuzVVtvrMhuBxLRBtIff%3DfxXwegvcguxNEHRTBBTH"
        ),
        "seckey": (
            "YSNoYBXRFcZK%2B2kRoOr3Ytr9QIkfl7VXc%2FZkupfasb8%3D%2CEkQ3gDtGyBiGnYmEbAfewqzVS3S5F7OJ9E20wGJo4318MZPiCt_4uPW29cbO50CIN9VOskJsTu5iPR80SPgIpPC0xgz-MiowW_XudfoltzsGJdOZtz_cNaLyibJlSVcg0AbA5foBC0X5KQCAbrwwRV7-OkgW2m87u9irYufqlvproZhrVf3xQD_g9nuWGQVl"
        ),
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _get_session().get(
                base_url, params=params, headers=headers, stream=True, timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                return True

            if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue

            return False
        except requests.RequestException:
            if attempt < MAX_RETRIES:
                backoff = RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) * (0.5 + random.random())
                time.sleep(backoff)
                continue
            return False

    return False


# ====================== 坐标转换（与原脚本保持一致） ======================
coordinate_point_category = 1  # 1 / 5 / 6


def coord_convert(lng1: float, lat1: float):
    if coordinate_point_category == 1:
        result = transCoordinateSystem.wgs84_to_gcj02(lng1, lat1)
        result = transCoordinateSystem.gcj02_to_bd09(result[0], result[1])
        return transBmap.lnglattopoint(result[0], result[1])
    if coordinate_point_category == 5:
        return transBmap.lnglattopoint(lng1, lat1)
    if coordinate_point_category == 6:
        result = transCoordinateSystem.gcj02_to_bd09(lng1, lat1)
        return transBmap.lnglattopoint(result[0], result[1])
    raise ValueError(f"未知 coordinate_point_category={coordinate_point_category}")


# ====================== 街景元信息 ======================
def get_panoid(lng: float, lat: float):
    url = f"https://mapsv0.bdimg.com/?qt=qsdata&x={lng}&y={lat}"
    req = _throttled_get(url)
    if req is None or req.status_code != 200:
        return []
    try:
        data = json.loads(req.text)
    except json.JSONDecodeError:
        return []
    if not data:
        return []

    result = data.get("content")
    if not result or "id" not in result:
        return []

    panoid = result["id"]
    url = f"https://mapsv0.bdimg.com/?qt=sdata&sid={panoid}&pc=1"
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
    timeLineIds = content0.get("TimeLine", [])
    Heading = content0.get("Heading")
    MoveDir = content0.get("MoveDir")
    NorthDir = content0.get("NorthDir")
    return [timeLineIds, Heading, MoveDir, NorthDir]


def _row_get_lon_lat_index(row: pd.Series) -> Tuple[int, float, float]:
    """
    兼容两种 CSV 字段命名：
    - 新版：longitude / latitude / index
    - 旧版：lon / lat（index 使用行号）
    """
    if "longitude" in row and "latitude" in row:
        lng = float(row["longitude"])
        lat = float(row["latitude"])
    elif "lon" in row and "lat" in row:
        lng = float(row["lon"])
        lat = float(row["lat"])
    else:
        raise ValueError(f"CSV 缺少经纬度列，当前列: {list(row.index)}")

    if "index" in row:
        idx = int(row["index"])
    else:
        # pandas iterrows() 的 index
        idx = int(row.name)

    return idx, lng, lat


def process_row_single_folder(row: pd.Series, folder_out_path: str) -> str:
    """
    处理单行：下载 4 个方向（heading+0/90/180/270）角度图。
    所有图片统一保存在给定的 folder_out_path。
    """
    idx, lng, lat = _row_get_lon_lat_index(row)

    try:
        tar_lng_lat = coord_convert(lng, lat)
        panoidInfos = get_panoid(tar_lng_lat[0], tar_lng_lat[1])
        if not panoidInfos or len(panoidInfos[0]) == 0:
            return f"{idx}: No panorama found."

        timeLineIds = panoidInfos[0]
        base_heading = panoidInfos[1] or 0

        # 默认取最新/第一条历史街景
        p0 = timeLineIds[0]
        pano_id = p0["ID"]
        timeLine = p0["TimeLine"]

        os.makedirs(folder_out_path, exist_ok=True)

        options = [
            (base_heading + 0) % 360,
            (base_heading + 90) % 360,
            (base_heading + 180) % 360,
            (base_heading + 270) % 360,
        ]

        done = 0
        for option in options:
            option_int = int(round(option))
            save_file_path = os.path.join(
                folder_out_path, f"{idx}_{lng}_{lat}_{option_int}_{timeLine}.jpg"
            )
            if os.path.exists(save_file_path):
                done += 1
                continue

            ok = download_baidu_panorama(
                save_path=save_file_path,
                panoid=pano_id,
                fovy=90,
                heading=option_int,
                pitch=0,
                width=960,
                height=720,
            )
            if ok:
                done += 1

        return f"{idx}: Done {done}/4."
    except Exception as e:
        return f"{idx}: Error {e}"


def process_single_csv(
    csv_path: str,
    start_idx: int = 0,
    end_idx: Optional[int] = None,
    num_processes: int = 5,
    sv_folder_name: str = "svi_degrees",
    *,
    progress_path: Optional[str] = None,
    csv_global_index: Optional[int] = None,
    progress_interval: int = 10000,
) -> None:
    """
    处理单个 CSV：
    - 在该 CSV 所在目录下创建/复用一个名为 sv_folder_name 的文件夹；
    - 使用多进程下载；
    - 每处理 progress_interval 行保存一次进度（可选）。
    """
    print(
        f"[CSV_PROCESS][START] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"csv={csv_path}, start_idx={start_idx}, end_idx={end_idx}"
    )

    csv_dir = os.path.dirname(csv_path)
    folder_out_path = os.path.join(csv_dir, sv_folder_name)
    df = pd.read_csv(csv_path)

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

    rows = [row for _, row in target_df.iterrows()]

    processed = 0
    func = functools.partial(process_row_single_folder, folder_out_path=folder_out_path)
    with Pool(processes=num_processes) as pool:
        for _ in tqdm(
            pool.imap_unordered(func, rows),
            total=len(rows),
            desc=f"Downloading ({os.path.basename(csv_path)})",
        ):
            processed += 1
            if (
                progress_path is not None
                and csv_global_index is not None
                and progress_interval > 0
                and processed % progress_interval == 0
            ):
                current_row_index = start_idx + processed
                save_progress(progress_path, csv_index=csv_global_index, row_index=current_row_index)

    print(
        f"[CSV_PROCESS][END  ] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"csv={csv_path}, processed={processed}"
    )


# ====================== 递归遍历 CSV + 简单断点续传（同 panorama_time_new_linux_csvs.py） ======================
def scan_all_csv_files(root_dir: str) -> List[str]:
    result: List[str] = []
    for cur_root, _dirs, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".csv"):
                result.append(os.path.join(cur_root, f))
    result.sort()
    return result


def load_progress(progress_path: str) -> Tuple[int, int]:
    if not os.path.exists(progress_path):
        return 0, 0
    try:
        with open(progress_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        csv_idx = int(data.get("current_csv_index", 0))
        row_idx = int(data.get("current_row_index", 0))
        return max(csv_idx, 0), max(row_idx, 0)
    except Exception:
        return 0, 0


def save_progress(progress_path: str, csv_index: int, row_index: int) -> None:
    print(
        f"[PROGRESS][START] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"path={progress_path}, csv_index={csv_index}, row_index={row_index}"
    )
    data = {
        "current_csv_index": int(csv_index),
        "current_row_index": int(row_index),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }
    os.makedirs(os.path.dirname(progress_path), exist_ok=True)
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(
        f"[PROGRESS][END  ] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        f"path={progress_path}"
    )


def main_multi_csv(
    root_dir: str,
    num_processes: int = 5,
    progress_filename: str = "svi_degrees_progress.json",
    sv_folder_name: str = "svi_degrees",
) -> None:
    csv_files = scan_all_csv_files(root_dir)
    if not csv_files:
        print(f"[INFO] 在目录 {root_dir} 下未发现任何 CSV 文件。")
        return

    progress_path = os.path.join(root_dir, progress_filename)
    current_csv_index, current_row_index = load_progress(progress_path)

    total = len(csv_files)
    print(f"[INFO] 共发现 {total} 个 CSV 文件。")
    print(f"[INFO] 进度文件: {progress_path}")
    print(f"[INFO] 已完成到 CSV 索引: {current_csv_index}, 行区间起点: {current_row_index}")

    if current_csv_index < 0:
        current_csv_index = 0
    if current_csv_index > total:
        current_csv_index = total

    for idx, csv_path in enumerate(csv_files):
        if idx < current_csv_index:
            print(f"[SKIP] ({idx + 1}/{total}) {csv_path}")
            continue

        if idx == current_csv_index and current_row_index > 0:
            start_idx = current_row_index
        else:
            start_idx = 0

        print(f"[RUN ] ({idx + 1}/{total}) {csv_path}, start_idx={start_idx}")
        try:
            process_single_csv(
                csv_path=csv_path,
                start_idx=start_idx,
                end_idx=None,
                num_processes=num_processes,
                sv_folder_name=sv_folder_name,
                progress_path=progress_path,
                csv_global_index=idx,
            )
            save_progress(progress_path, csv_index=idx + 1, row_index=0)
            current_row_index = 0
        except Exception as e:
            print(f"[ERROR] 处理 CSV 失败: {csv_path}, error={e}")
            break

    print("[DONE] 所有可处理的 CSV 已完成当前批次下载。")


if __name__ == "__main__":
    # ========== 请按需修改以下参数 ==========
    # 1. 需要遍历的根目录，脚本会在该目录及所有子目录中递归查找 *.csv
    ROOT_DIR = r"H:\_50m_point"  # TODO: 换成你的根目录

    # 2. 多进程进程数（建议根据 CPU 与网络情况调整）
    NUM_PROCESSES = 30

    # 3. 进度文件名，会存放在 ROOT_DIR 下
    PROGRESS_FILENAME = "svi_degrees26_progress.json"

    # 4. 每个 CSV 同级目录下用于保存图片的文件夹名
    SV_FOLDER_NAME = "svi_degrees26"

    main_multi_csv(
        root_dir=ROOT_DIR,
        num_processes=NUM_PROCESSES,
        progress_filename=PROGRESS_FILENAME,
        sv_folder_name=SV_FOLDER_NAME,
    )

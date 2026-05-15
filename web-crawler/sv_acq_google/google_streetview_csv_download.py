# -*- coding: utf-8 -*-
"""
基于 rrwen/google_streetview 的批量下载脚本：从 CSV 读取经纬度，调用 Google Street View
Static API（与该项目一致），将全景静态图与元数据保存到指定目录。

第三方库（需单独安装）：
  pip install google_streetview requests

使用前请在 Google Cloud 启用「Street View Static API」，并配置结算与 API Key。

用法：编辑下方「用户配置」区域的变量，然后运行：
  python google_streetview_csv_download.py
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    import google_streetview.api as gsv_api
    import google_streetview.helpers as gsv_helpers
except ImportError:
    print(
        "未安装 google_streetview。请先执行: pip install google_streetview",
        file=sys.stderr,
    )
    sys.exit(2)

# ----------------------------- 用户配置（请修改） -----------------------------
# Google Maps API Key；若为空字符串，则尝试读取环境变量 GOOGLE_MAPS_API_KEY 或 GOOGLE_CLOUD_API_KEY
API_KEY = ""

# 输入 CSV 路径（含表头）
CSV_PATH = r"D:\path\to\points.csv"

# 保存图片与汇总 JSON 的输出目录（不存在会自动创建）
OUT_DIR = r"D:\path\to\gsv_output"

# CSV 中纬度、经度列名
LAT_COL = "lat"
LON_COL = "lon"

# 可选：用于生成文件名的 ID 列名；设为 None 则使用 row0、row1 …
ID_COL: Optional[str] = None

# CSV 文件编码
CSV_ENCODING = "utf-8-sig"

# 图片尺寸（Street View Static，最大约 640x640）
IMAGE_SIZE = "640x640"

# 朝向：逗号或分号分隔，如 "0" 或 "0,90,180,270"（多朝向会多次请求计费）
HEADINGS_STR = "0"

PITCH = "0"
FOV = "90"

# 每条 CSV 记录处理后的休眠秒数，降低限频风险
DELAY_SEC = 0.05

# 汇总元数据文件名（保存在 OUT_DIR 下）
METADATA_JSON = "batch_metadata.json"
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 60


def resolve_api_key(config_key: str) -> str:
    key = (config_key or "").strip()
    if key:
        return key
    key = (
        os.environ.get("GOOGLE_MAPS_API_KEY")
        or os.environ.get("GOOGLE_CLOUD_API_KEY")
        or ""
    ).strip()
    if not key:
        print(
            "错误：请在脚本顶部设置 API_KEY，或设置环境变量 GOOGLE_MAPS_API_KEY。",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def safe_filename_part(s: str, max_len: int = 80) -> str:
    s = re.sub(r'[<>:"/\\|?*]', "_", s.strip())
    s = re.sub(r"\s+", "_", s)
    return s[:max_len] if len(s) > max_len else s


def download_binary(url: str, file_path: str) -> bool:
    try:
        r = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return False
    if r.status_code != 200:
        return False
    os.makedirs(os.path.dirname(os.path.abspath(file_path)) or ".", exist_ok=True)
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
    return True


def parse_headings(s: str) -> List[str]:
    parts = [p.strip() for p in s.replace(";", ",").split(",") if p.strip()]
    return parts if parts else ["0"]


def read_csv_rows(
    path: str,
    encoding: str,
    lat_col: str,
    lon_col: str,
) -> Tuple[List[str], List[Dict[str, str]]]:
    with open(path, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV 无表头")
        fieldnames = list(reader.fieldnames)
        rows: List[Dict[str, str]] = []
        for row in reader:
            rows.append({k: (row.get(k) or "").strip() for k in fieldnames})
    if lat_col not in fieldnames:
        raise ValueError(f"CSV 中找不到纬度列: {lat_col}，当前列: {fieldnames}")
    if lon_col not in fieldnames:
        raise ValueError(f"CSV 中找不到经度列: {lon_col}，当前列: {fieldnames}")
    return fieldnames, rows


def main() -> None:
    api_key = resolve_api_key(API_KEY)
    headings = parse_headings(HEADINGS_STR)

    os.makedirs(OUT_DIR, exist_ok=True)

    _, rows = read_csv_rows(CSV_PATH, CSV_ENCODING, LAT_COL, LON_COL)

    summary: List[Dict[str, Any]] = []

    for i, row in enumerate(rows):
        lat_s = row.get(LAT_COL, "")
        lon_s = row.get(LON_COL, "")
        try:
            lat_f = float(lat_s)
            lon_f = float(lon_s)
        except ValueError:
            summary.append(
                {
                    "row_index": i,
                    "status": "SKIP_BAD_COORD",
                    "lat": lat_s,
                    "lon": lon_s,
                    "files": [],
                }
            )
            continue

        if ID_COL and ID_COL in row:
            base = safe_filename_part(row[ID_COL] or f"row{i}")
        else:
            base = f"row{i}"

        loc = f"{lat_f},{lon_f}"
        heading_joined = ";".join(headings)

        apiargs: Dict[str, str] = {
            "size": IMAGE_SIZE,
            "location": loc,
            "heading": heading_joined,
            "pitch": PITCH,
            "fov": FOV,
            "key": api_key,
        }

        param_list = gsv_helpers.api_list(apiargs)
        res = gsv_api.results(param_list)

        for j in range(len(res.links)):
            meta = res.metadata[j]
            st = meta.get("status")
            par = res.params[j]
            h = par.get("heading", headings[j] if j < len(headings) else str(j))

            entry: Dict[str, Any] = {
                "row_index": i,
                "base_name": base,
                "location_csv": loc,
                "heading": h,
                "metadata": meta,
            }

            if st != "OK":
                entry["saved_image"] = None
                summary.append(entry)
                continue

            fname = f"{base}_h{safe_filename_part(str(h))}.jpg"
            fpath = os.path.join(OUT_DIR, fname)
            if os.path.isfile(fpath):
                fname_alt = f"{base}_h{safe_filename_part(str(h))}_{i}_{j}.jpg"
                fpath = os.path.join(OUT_DIR, fname_alt)

            ok = download_binary(res.links[j], fpath)
            if ok:
                entry["saved_image"] = os.path.basename(fpath)
            else:
                entry["saved_image"] = None
                entry["download_error"] = True

            summary.append(entry)

        if DELAY_SEC > 0:
            time.sleep(DELAY_SEC)

    meta_path = os.path.join(OUT_DIR, METADATA_JSON)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    ok_cnt = sum(
        1
        for x in summary
        if x.get("metadata", {}).get("status") == "OK" and x.get("saved_image")
    )
    print(f"完成。成功保存图片条数（含多朝向则多条）: {ok_cnt}")
    print(f"汇总 JSON: {meta_path}")


if __name__ == "__main__":
    main()

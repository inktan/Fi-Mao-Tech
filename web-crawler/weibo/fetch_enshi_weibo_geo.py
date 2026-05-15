# -*- coding: utf-8 -*-
"""
获取恩施土家族苗族自治州范围内、带坐标与文本的微博动态（设计用于微博开放平台 API）。

原理简述
--------
微博开放平台提供「周边动态」接口 place/nearby_timeline：给定经纬度与搜索半径（米），可返回附近用户公开的带地点信息的动态。
恩施州地域远大于单次查询半径上限（约 11 km），因此对州域边界框做网格采样，在每个网格中心发起查询，并对微博 id 去重。

行政区域范围（文献常用口径，州域东西约 220 km、南北约 260 km）
----------------------------------------------------------------------
东经 108°23′12″～110°38′08″，北纬 29°07′10″～31°24′13″（区划地名网等公开资料）。
脚本内换算为十进制度作为默认边界框；边界框会略大于不规则行政区多边形，采集后可用自有 SHP 再过滤。

前置条件
--------
1. 在微博开放平台创建应用，为本应用申请「周边动态」等相关接口权限（以控制台实际可选权限为准）。
2. 通过 OAuth2 取得有效 access_token（环境变量 WEIBO_ACCESS_TOKEN）。
3. 安装 requests： pip install requests

重要说明
--------
- 仅能获取接口权限允许范围内的数据；若接口下线或权限收紧，需按开放平台最新文档调整。
- 通常只有用户主动标注/公开地理位置的微博才会出现在周边结果中，并非全州所有发帖。
- 请遵守《微博开放平台公约》及当地法律法规，控制频率避免被封禁。

用法示例
--------
  set WEIBO_ACCESS_TOKEN=你的token
  python fetch_enshi_weibo_geo.py -o enshi_weibo.csv

  # 缩小网格步长（更密、更慢、覆盖更全）
  python fetch_enshi_weibo_geo.py --step 0.05 --max-pages 5 -o out.csv

  # 仅打印网格点数与边界，不请求接口
  python fetch_enshi_weibo_geo.py --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple

import requests

# 恩施州州域默认边界框（十进制度，来源：州域经纬度区间常用公开表述）
ENS_MIN_LON = 108 + 23 / 60 + 12 / 3600  # 108°23′12″
ENS_MAX_LON = 110 + 38 / 60 + 8 / 3600  # 110°38′08″
ENS_MIN_LAT = 29 + 7 / 60 + 10 / 3600  # 29°07′10″
ENS_MAX_LAT = 31 + 24 / 60 + 13 / 3600  # 31°24′13″

NEARBY_URL = "https://api.weibo.com/2/place/nearby_timeline.json"
# 接口文档载明单次搜索半径上限约 11132 米
MAX_RANGE_M = 11132
MAX_COUNT = 50


def iter_grid(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    step_lat: float,
    step_lon: float,
) -> Iterator[Tuple[float, float]]:
    lat = min_lat
    while lat <= max_lat + 1e-9:
        lon = min_lon
        while lon <= max_lon + 1e-9:
            yield round(lat, 6), round(lon, 6)
            lon += step_lon
        lat += step_lat


def in_bbox(lon: float, lat: float, bounds: Tuple[float, float, float, float]) -> bool:
    min_lon, min_lat, max_lon, max_lat = bounds
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def extract_lon_lat(geo: Any) -> Optional[Tuple[float, float]]:
    """从 status.geo 解析经纬度（兼容常见 GeoJSON 与旧版字段）。"""
    if not geo:
        return None
    if isinstance(geo, str):
        try:
            geo = json.loads(geo)
        except json.JSONDecodeError:
            return None
    if not isinstance(geo, dict):
        return None
    coords = geo.get("coordinates")
    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
        try:
            return float(coords[0]), float(coords[1])
        except (TypeError, ValueError):
            return None
    try:
        lon = geo.get("longitude")
        lat = geo.get("latitude")
        if lon is not None and lat is not None:
            return float(lon), float(lat)
    except (TypeError, ValueError):
        pass
    return None


def fetch_nearby_page(
    token: str,
    lat: float,
    lon: float,
    page: int,
    range_m: int,
    session: requests.Session,
) -> Dict[str, Any]:
    params = {
        "access_token": token,
        "lat": lat,
        "long": lon,
        "range": range_m,
        "count": MAX_COUNT,
        "page": page,
        "sort": 0,
        "offset": 1,
    }
    r = session.get(NEARBY_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def normalize_status(
    st: Dict[str, Any],
    cell_lat: float,
    cell_lon: float,
    bounds: Tuple[float, float, float, float],
) -> Optional[Dict[str, Any]]:
    geo = st.get("geo")
    pair = extract_lon_lat(geo)
    if pair is None:
        return None
    lon, lat = pair
    if not in_bbox(lon, lat, bounds):
        return None
    user = st.get("user") or {}
    return {
        "id": st.get("idstr") or str(st.get("id", "")),
        "mid": st.get("mid", ""),
        "created_at": st.get("created_at", ""),
        "text": (st.get("text") or "").replace("\r\n", "\n").replace("\r", "\n"),
        "longitude": lon,
        "latitude": lat,
        "user_id": user.get("idstr") or str(user.get("id", "")),
        "screen_name": user.get("screen_name", ""),
        "source_cell_lat": cell_lat,
        "source_cell_lon": cell_lon,
        "raw_geo": json.dumps(geo, ensure_ascii=False) if geo else "",
    }


def collect_all(
    token: str,
    bounds: Tuple[float, float, float, float],
    grid: Iterable[Tuple[float, float]],
    range_m: int,
    sleep_s: float,
    max_pages_per_cell: int,
    session: requests.Session,
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    min_lon, min_lat, max_lon, max_lat = bounds
    bounds_check = (min_lon, min_lat, max_lon, max_lat)
    seen: Set[str] = set()
    rows: List[Dict[str, Any]] = []

    for cell_lat, cell_lon in grid:
        for page in range(1, max_pages_per_cell + 1):
            try:
                data = fetch_nearby_page(token, cell_lat, cell_lon, page, range_m, session)
            except requests.RequestException as e:
                print(f"[warn] 请求失败 cell=({cell_lat},{cell_lon}) page={page}: {e}", file=sys.stderr)
                break

            if "error" in data or "error_code" in data:
                err = data.get("error", data)
                code = data.get("error_code", "")
                print(f"[warn] API 返回错误 cell=({cell_lat},{cell_lon}) page={page}: {code} {err}", file=sys.stderr)
                break

            statuses = data.get("statuses") or []
            if not statuses:
                break

            new_in_page = 0
            for st in statuses:
                row = normalize_status(st, cell_lat, cell_lon, bounds_check)
                if row is None:
                    continue
                sid = row["id"]
                if sid in seen:
                    continue
                seen.add(sid)
                rows.append(row)
                new_in_page += 1

            if len(statuses) < MAX_COUNT:
                break
            if new_in_page == 0:
                break

            time.sleep(sleep_s)

        time.sleep(sleep_s)

    return rows, seen


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="恩施州范围内微博地理动态采集（开放平台 nearby_timeline + 网格）")
    p.add_argument("-o", "--output", default="enshi_weibo_geo.csv", help="输出 CSV 路径")
    p.add_argument("--min-lon", type=float, default=ENS_MIN_LON, help="边界框最小经度")
    p.add_argument("--min-lat", type=float, default=ENS_MIN_LAT, help="边界框最小纬度")
    p.add_argument("--max-lon", type=float, default=ENS_MAX_LON, help="边界框最大经度")
    p.add_argument("--max-lat", type=float, default=ENS_MAX_LAT, help="边界框最大纬度")
    p.add_argument(
        "--step",
        type=float,
        default=0.07,
        help="网格步长（度）。默认约 7–8 km 量级，与最大搜索半径配合覆盖",
    )
    p.add_argument("--range-m", type=int, default=MAX_RANGE_M, help="单次周边搜索半径（米），不超过 %d" % MAX_RANGE_M)
    p.add_argument("--sleep", type=float, default=0.8, help="每次请求后的休眠秒数（限速）")
    p.add_argument("--max-pages", type=int, default=8, help="每个网格中心最多翻页数")
    p.add_argument("--dry-run", action="store_true", help="只统计网格点数量并退出")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    token = os.environ.get("WEIBO_ACCESS_TOKEN", "").strip()
    bounds = (args.min_lon, args.min_lat, args.max_lon, args.max_lat)

    grid = list(
        iter_grid(
            bounds[1],
            bounds[3],
            bounds[0],
            bounds[2],
            args.step,
            args.step,
        )
    )
    print(f"边界框: 经度 [{bounds[0]:.6f}, {bounds[2]:.6f}] 纬度 [{bounds[1]:.6f}, {bounds[3]:.6f}]")
    print(f"网格点数: {len(grid)}（步长 {args.step}°）")

    if args.dry_run:
        return

    if not token:
        print("请设置环境变量 WEIBO_ACCESS_TOKEN（OAuth2 access_token）", file=sys.stderr)
        sys.exit(2)

    session = requests.Session()
    session.headers.setdefault("User-Agent", "Fi-Mao-Tech-weibo-enshi/1.0")

    rows, _ = collect_all(
        token,
        bounds,
        grid,
        min(args.range_m, MAX_RANGE_M),
        args.sleep,
        args.max_pages,
        session,
    )

    fieldnames = [
        "id",
        "mid",
        "created_at",
        "text",
        "longitude",
        "latitude",
        "user_id",
        "screen_name",
        "source_cell_lat",
        "source_cell_lon",
        "raw_geo",
    ]
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"已写入 {len(rows)} 条（去重后、且坐标落在边界框内） -> {args.output}")


if __name__ == "__main__":
    main()

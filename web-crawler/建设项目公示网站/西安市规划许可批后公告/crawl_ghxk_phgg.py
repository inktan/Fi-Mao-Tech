# -*- coding: utf-8 -*-
"""
西安市自然资源和规划局「规划许可批后公告」列表与详情批量归档。

说明（与官网页面逻辑一致）：
- 列表页 https://zygh.xa.gov.cn/dlyssz/ghxkphgg.html 中 #container-list 下 article.card.card-type
  由 Vue 通过 POST /dlyssz/jk/publicity/selectall 拉取；点击卡片等价于打开
  https://zygh.xa.gov.cn/dlyssz/ghxkDetail.html?id=<记录id>&t=<时间戳>
- 详情页 #printContent / #sssss 的正文与扫描图由 GET /dlyssz/jk/publicity/selectone/<id> 返回的数据渲染。
  本脚本直接调用上述接口，效果与浏览器渲染后保存一致，且不依赖 Playwright。

用法:
  python crawl_ghxk_phgg.py --output-dir "D:\\data\\xa_ghxk" [--timeout 300] [--detail-timeout 1800] [--retries 8]
  若列表 POST 仍超时，可加大 --timeout（例如 600）或检查本机到 zygh.xa.gov.cn 的网络/代理。

依赖: 仅 Python 3 标准库。
"""

from __future__ import annotations

import argparse
import base64
import errno
import json
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LIST_PAGE = "https://zygh.xa.gov.cn/dlyssz/ghxkphgg.html"
API_LIST = "https://zygh.xa.gov.cn/dlyssz/jk/publicity/selectall"
API_ONE_TMPL = "https://zygh.xa.gov.cn/dlyssz/jk/publicity/selectone/{}"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 与 ghxkDetail.html 中 #sssss 的 v-if 分支一致（证书类型 + 证号）
FLOWID_TO_TITLE_TEMPLATE: Dict[str, str] = {
    "t1001_8a8610056dbabcff016dd020b5960777": "《建设工程规划许可证》（{certificatenumber}）",
    "t1001_8a86100573a359470173a3ec1a4e163f": "《建设工程规划许可证（基坑部分）》（{certificatenumber}）",
    "t1001_8a8610056dbabcff016dd0297857078b": "《建设用地规划许可证》（{certificatenumber}）",
    "t1001_8a8610056dbabcff016dd02f71fb079f": "《建设项目用地预审与选址意见书》（{certificatenumber}）",
    "t1001_8a8610056eb9dbac016ec4a5b55507eb": "《乡村建设规划许可证》（{certificatenumber}）",
}

FIELD_LABEL_ZH: Dict[str, str] = {
    "projectname": "项目名称",
    "certificatenumber": "许可证号",
    "buildunit": "建设单位(个人)",
    "buildAddress": "建设位置",
    "jsgm": "建设规模",
    "ftjfjmc": "附图及附件名称",
    "fbrq": "发布日期",
    "certificatedate": "发证日期",
    "status": "状态",
    "flowid": "流程类型ID",
    "sxlx": "事项类型",
    "bindingunit": "编制单位",
    "publicperson": "发布人",
    "attachpath": "附件路径",
    "pid": "业务PID",
    "tdyt": "土地用途",
    "tdqdfs": "土地取得方式",
    "pzydjg": "批准用地机关",
    "ydmj": "用地面积",
    "jydmj": "净用地面积",
    "dzdlmj": "代征道路面积",
    "dzldmj": "代征绿地面积",
    "xmdm": "项目代码",
    "jsxmyj": "项目依据",
    "xxrq": "公告结束相关日期",
}


def _is_retryable_exc(exc: BaseException) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in (408, 429, 500, 502, 503, 504)
    if isinstance(
        exc,
        (
            TimeoutError,
            socket.timeout,
            ConnectionError,
            urllib.error.URLError,
        ),
    ):
        return True
    if isinstance(exc, OSError):
        no = getattr(exc, "winerror", None) or getattr(exc, "errno", None)
        if no in (
            errno.ETIMEDOUT,
            errno.ECONNRESET,
            errno.EPIPE,
            errno.ECONNABORTED,
            10060,
            10054,
        ):
            return True
    return False


def _request_json(
    url: str,
    method: str = "GET",
    body_obj: Optional[dict] = None,
    timeout: float = 180,
    retries: int = 6,
    backoff: float = 2.0,
) -> dict:
    data: Optional[bytes] = None
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "close",
    }
    if body_obj is not None:
        data = json.dumps(body_obj, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=UTF-8"
        headers["Origin"] = "https://zygh.xa.gov.cn"
        headers["Referer"] = LIST_PAGE

    curl_bin = shutil.which("curl.exe") or shutil.which("curl")

    def _request_via_curl_once() -> Optional[dict]:
        if not curl_bin:
            return None
        cmd = [
            str(curl_bin),
            "--max-time",
            str(int(max(1.0, timeout))),
            "-sS",
            "--location",
            "--request",
            method.upper(),
            url,
        ]
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])

        temp_file_path: Optional[str] = None
        temp_resp_path: Optional[str] = None
        try:
            if data is not None:
                with tempfile.NamedTemporaryFile(
                    suffix=".json", delete=False
                ) as tf:
                    tf.write(data)
                    temp_file_path = tf.name
                cmd.extend(["--data-binary", "@" + temp_file_path])

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as rf:
                temp_resp_path = rf.name
            cmd.extend(["--output", temp_resp_path, "--write-out", "%{http_code}"])

            cp = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if cp.returncode != 0:
                raise RuntimeError(
                    f"curl 失败 code={cp.returncode}: {cp.stderr[:300]}"
                )
            status = (cp.stdout or "").strip()
            status_code = int(status[-3:]) if len(status) >= 3 and status[-3:].isdigit() else 0
            out = ""
            if temp_resp_path:
                out = Path(temp_resp_path).read_text(encoding="utf-8", errors="replace")
            out = out.strip()
            if not out:
                raise RuntimeError(f"curl 返回空响应（HTTP {status_code or 'unknown'}）")
            if not (200 <= status_code < 300):
                raise RuntimeError(
                    f"curl HTTP {status_code} {url}: {out[:300]!r}"
                )
            # 兼容 UTF-8 BOM、前置噪声文本、代理注入等情况
            out = out.lstrip("\ufeff").strip()
            if not out:
                raise RuntimeError("curl 返回空文本")
            if not out.startswith("{") and not out.startswith("["):
                first_json_pos = min(
                    [p for p in (out.find("{"), out.find("[")) if p >= 0],
                    default=-1,
                )
                if first_json_pos > 0:
                    out = out[first_json_pos:].strip()
            if not out.startswith("{") and not out.startswith("["):
                raise RuntimeError(f"curl 返回非 JSON 内容: {out[:300]!r}")
            try:
                return json.loads(out)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"curl JSON 解析失败: {e}; 响应前300字符={out[:300]!r}"
                ) from e
        finally:
            if temp_file_path:
                try:
                    Path(temp_file_path).unlink(missing_ok=True)
                except Exception:
                    pass
            if temp_resp_path:
                try:
                    Path(temp_resp_path).unlink(missing_ok=True)
                except Exception:
                    pass

    last_err: Optional[BaseException] = None
    for attempt in range(max(1, retries)):
        try:
            # 如果系统可用 curl，优先且仅使用 curl（避免 urllib 在部分环境固定 404）
            by_curl = _request_via_curl_once()
            if by_curl is not None:
                return by_curl

            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            text = raw.decode("utf-8", errors="replace").lstrip("\ufeff").strip()
            if not text:
                raise RuntimeError("urllib 返回空响应")
            if not text.startswith("{") and not text.startswith("["):
                raise RuntimeError(f"urllib 返回非 JSON 内容: {text[:300]!r}")
            return json.loads(text)
        except urllib.error.HTTPError as e:
            if _is_retryable_exc(e) and attempt + 1 < retries:
                last_err = e
                delay = min(backoff**attempt, 60.0)
                print(
                    f"  [重试 {attempt + 1}/{retries}] HTTP {e.code} {url} — {delay:.0f}s 后重试",
                    flush=True,
                )
                time.sleep(delay)
                continue
            try:
                body_preview = e.read()[:500]
            except Exception:
                body_preview = b""
            raise RuntimeError(
                f"HTTP {e.code} {url}: {body_preview!r}"
            ) from e
        except (
            TimeoutError,
            socket.timeout,
            ConnectionError,
            urllib.error.URLError,
            OSError,
        ) as e:
            last_err = e
            if attempt + 1 >= retries or not _is_retryable_exc(e):
                raise RuntimeError(
                    f"请求失败（已重试 {retries} 次）: {url} — {e!r}"
                ) from e
            delay = min(backoff**attempt, 60.0)
            print(
                f"  [重试 {attempt + 1}/{retries}] {type(e).__name__}: {e!s} — {delay:.0f}s 后重试",
                flush=True,
            )
            time.sleep(delay)
        except RuntimeError as e:
            last_err = e
            if attempt + 1 >= retries:
                raise
            delay = min(backoff**attempt, 60.0)
            print(
                f"  [重试 {attempt + 1}/{retries}] RuntimeError: {e!s} — {delay:.0f}s 后重试",
                flush=True,
            )
            time.sleep(delay)

    raise RuntimeError(f"请求失败: {url} — {last_err!r}") from last_err


def detail_url(record_id: str) -> str:
    return (
        "https://zygh.xa.gov.cn/dlyssz/ghxkDetail.html?id="
        + record_id
        + "&t="
        + str(int(time.time() * 1000))
    )


def ss_title(data: dict) -> str:
    fid = data.get("flowid") or ""
    tpl = FLOWID_TO_TITLE_TEMPLATE.get(fid)
    cert = (data.get("certificatenumber") or "").strip()
    if tpl:
        return tpl.format(certificatenumber=cert or "（无证号）")
    pname = (data.get("projectname") or "").strip()
    return pname or fid or "未命名公示"


def sanitize_dir_name(name: str, max_len: int = 100) -> str:
    s = re.sub(r'[<>:"/\\|?*]', "_", name)
    s = s.strip(" .")
    if len(s) > max_len:
        s = s[:max_len].rstrip(" .")
    return s or "unnamed"


def _month_key(yyyymm_or_date: str) -> int:
    """
    兼容 'YYYY-MM' / 'YYYY-MM-DD' / 'YYYY/MM/DD'。
    返回 YYYYMM 整数，无法解析返回 0。
    """
    if not yyyymm_or_date:
        return 0
    s = str(yyyymm_or_date).strip().replace("/", "-")
    m = re.search(r"^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?$", s)
    if not m:
        return 0
    y = int(m.group(1))
    mon = int(m.group(2))
    if mon < 1 or mon > 12:
        return 0
    return y * 100 + mon


def save_data_uri_image(data_uri: str, dest_path: Path) -> Optional[Path]:
    if not data_uri or not data_uri.startswith("data:image"):
        return None
    m = re.match(r"^data:image/(\w+);base64,(.+)$", data_uri, re.DOTALL)
    if not m:
        return None
    ext = m.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    raw = base64.b64decode(m.group(2))
    dest_path = dest_path.with_suffix("." + ext)
    dest_path.write_bytes(raw)
    return dest_path


def build_print_content_text(data: dict) -> str:
    """模拟 #printContent 可见文字：标题(#sssss) + 主要字段。"""
    lines: List[str] = []
    title = ss_title(data)
    lines.append(title)
    lines.append("")
    if str(data.get("status")) == "1":
        lines.append("至公告期已结束（详情页 status==1）")
        lines.append("")
    lines.append("—— 公示字段 ——")
    keys = [
        "projectname",
        "certificatenumber",
        "buildunit",
        "buildAddress",
        "jsgm",
        "ftjfjmc",
        "fbrq",
        "certificatedate",
        "status",
        "bindingunit",
        "publicperson",
        "sxlx",
        "tdyt",
        "tdqdfs",
        "pzydjg",
        "ydmj",
        "jydmj",
        "dzdlmj",
        "dzldmj",
        "xmdm",
        "jsxmyj",
        "attachpath",
        "filepath",
        "flowid",
    ]
    seen = set(keys)
    for k in keys:
        v = data.get(k)
        if v is None or v == "":
            continue
        label = FIELD_LABEL_ZH.get(k, k)
        lines.append(f"{label}: {v}")
    for k, v in sorted(data.items()):
        if k in seen or k == "base64Str":
            continue
        if v is None or v == "":
            continue
        if isinstance(v, (dict, list)):
            continue
        label = FIELD_LABEL_ZH.get(k, k)
        lines.append(f"{label}: {v}")
    lines.append("")
    lines.append("详情页URL: " + detail_url(str(data.get("id", ""))))
    return "\n".join(lines)


def fetch_list_page(
    projectname: str,
    page_num: int,
    page_size: int,
    *,
    timeout: float,
    retries: int,
    backoff: float,
) -> Tuple[List[dict], int]:
    body = {
        "projectname": projectname,
        "pageNum": page_num,
        "pageSize": page_size,
        "status": "",
        "sxlx": "一书三证",
    }
    j = _request_json(
        API_LIST,
        method="POST",
        body_obj=body,
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    if j.get("msg") != "ok" and "data" not in j:
        raise RuntimeError(f"列表接口异常: {j!r}")
    rows = j.get("data") or []
    total = int(j.get("count") or 0)
    out: List[dict] = []
    for el in rows:
        if el.get("status") == "不公示":
            continue
        out.append(el)
    return out, total


def process_one(
    record_id: str,
    output_root: Path,
    *,
    timeout: float,
    retries: int,
    backoff: float,
) -> Path:
    url = API_ONE_TMPL.format(record_id)
    j = _request_json(
        url,
        method="GET",
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    if j.get("msg") != "ok" or not j.get("data"):
        raise RuntimeError(f"详情异常 id={record_id}: {str(j)[:500]}")
    data: Dict[str, Any] = j["data"]
    data.setdefault("id", record_id)

    fbrq = str(data.get("fbrq") or "").strip()
    project_name = str(data.get("projectname") or "").strip()
    if not project_name:
        project_name = ss_title(data)
    if not fbrq:
        fbrq = "unknown-date"

    # 按“发布日期_项目名称”命名（用户要求）
    folder_name = sanitize_dir_name(f"{fbrq}_{project_name}", max_len=180)
    folder = output_root / folder_name
    if folder.exists():
        # 极少数同名场景自动去重，避免覆盖
        folder = output_root / f"{folder_name}_{record_id[:8]}"
    folder.mkdir(parents=True, exist_ok=True)

    text = build_print_content_text(data)
    (folder / "printContent.txt").write_text(text, encoding="utf-8")

    b64 = data.get("base64Str")
    if isinstance(b64, str) and b64.startswith("data:image"):
        saved = save_data_uri_image(b64, folder / "扫描件")
        if saved:
            meta = folder / "images_manifest.txt"
            meta.write_text(saved.name + "\n", encoding="utf-8")

    fp = data.get("filepath")
    if fp and isinstance(fp, str) and not str(b64 or "").startswith("data:image"):
        (folder / "filepath说明.txt").write_text(
            "接口返回 filepath（本站可能仅用 base64 展示扫描件；若需文件可再对接内网 DocService）:\n" + fp,
            encoding="utf-8",
        )

    return folder


def main() -> None:
    ap = argparse.ArgumentParser(description="西安规划许可批后公告 — 列表+详情归档")
    ap.add_argument(
        "--output-dir",
        required=True,
        help="输出根目录；每条公示在其下新建子文件夹",
    )
    ap.add_argument("--projectname", default="", help="按项目名称筛选（与官网搜索一致）")
    ap.add_argument(
        "--stop-month",
        default="2024-12",
        help="抓取截止月份（含该月），格式 YYYY-MM；默认 2024-12",
    )
    ap.add_argument("--page-size", type=int, default=8, help="列表每页条数，默认与官网一致 8")
    ap.add_argument("--max-pages", type=int, default=0, help="最多抓取列表页数，0 表示直到取完")
    ap.add_argument(
        "--max-items",
        type=int,
        default=0,
        help="最多处理详情条数（调试用），0 表示不限制",
    )
    ap.add_argument(
        "--list-only",
        action="store_true",
        help="只拉列表并写入 list_urls.json，不请求详情",
    )
    ap.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="列表接口与预热 GET 的单次套接字超时（秒），默认 300",
    )
    ap.add_argument(
        "--detail-timeout",
        type=float,
        default=0.0,
        help="详情 selectone 超时（秒），默认 0 表示自动取 max(900, 3×列表超时)，因响应含大图 base64 可能很大",
    )
    ap.add_argument(
        "--retries",
        type=int,
        default=8,
        help="网络失败或 5xx 时的最大尝试次数，默认 8",
    )
    ap.add_argument(
        "--retry-backoff",
        type=float,
        default=2.0,
        help="重试间隔底数：第 n 次等待 min(backoff^n, 60) 秒，默认 2",
    )
    args = ap.parse_args()

    detail_timeout = args.detail_timeout
    if detail_timeout <= 0:
        detail_timeout = max(900.0, float(args.timeout) * 3.0)

    output_root = Path(args.output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    stop_month_key = _month_key(args.stop_month)
    if stop_month_key == 0:
        raise ValueError(f"--stop-month 格式错误: {args.stop_month!r}，应为 YYYY-MM")

    # 预热：先 GET 列表页 HTML（非 JSON），便于部分网络环境下后续 POST 更稳定
    for warm_attempt in range(max(1, args.retries // 2)):
        try:
            req = urllib.request.Request(
                LIST_PAGE,
                headers={"User-Agent": UA, "Connection": "close"},
                method="GET",
            )
            with urllib.request.urlopen(
                req, timeout=min(float(args.timeout), 120.0)
            ) as r:
                _ = r.read(2000)
            break
        except Exception:
            if warm_attempt + 1 >= max(1, args.retries // 2):
                break
            time.sleep(min(args.retry_backoff**warm_attempt, 30.0))

    all_meta: List[dict] = []
    page = 1
    total_count = None
    reached_stop_month = False

    while True:
        rows, total = fetch_list_page(
            args.projectname,
            page,
            args.page_size,
            timeout=float(args.timeout),
            retries=args.retries,
            backoff=args.retry_backoff,
        )
        if total_count is None:
            total_count = total
        for row in rows:
            row_month_key = _month_key(str(row.get("fbrq") or ""))
            # 列表按时间倒序，遇到早于截止月的数据即可停止后续抓取
            if row_month_key and row_month_key < stop_month_key:
                reached_stop_month = True
                break
            rid = row.get("id")
            if not rid:
                continue
            all_meta.append(
                {
                    "id": rid,
                    "detail_html_url": detail_url(str(rid)),
                    "projectname": row.get("projectname"),
                    "fbrq": row.get("fbrq"),
                    "certificatenumber": row.get("certificatenumber"),
                    "flowid": row.get("flowid"),
                }
            )
        if reached_stop_month:
            break
        if args.max_pages and page >= args.max_pages:
            break
        if not rows:
            break
        if page * args.page_size >= total_count:
            break
        page += 1

    list_json = output_root / "list_urls.json"
    list_json.write_text(
        json.dumps(all_meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"列表共 {len(all_meta)} 条（接口声明 total={total_count}），已写入 {list_json}")

    if args.list_only:
        return

    n_done = 0
    for i, meta in enumerate(all_meta, 1):
        if args.max_items and n_done >= args.max_items:
            break
        rid = meta["id"]
        try:
            dest = process_one(
                str(rid),
                output_root,
                timeout=float(detail_timeout),
                retries=args.retries,
                backoff=args.retry_backoff,
            )
            print(f"[{i}/{len(all_meta)}] OK {dest}")
            n_done += 1
        except Exception as e:
            print(f"[{i}/{len(all_meta)}] FAIL id={rid}: {e}")


if __name__ == "__main__":
    main()

import math
import os
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


CONFIG = {
    # 主要下载任务（你给的 URL）
    "url": "https://huggingface.co/BAAI/bge-m3/resolve/main/pytorch_model.bin?download=true",
    # 输出文件路径；None 表示使用 URL 里的文件名，保存到当前工作目录
    "out": r'D:\Users\mslne\Documents\GitHub\svi_JusticeScape\back-end-interface\SviEvaluation\models\bge-m3',
    # 并发连接数（越大通常越快，但也更吃 CPU/连接；建议 16/32/64 试）
    "connections": 32,
    # 每个连接的超时时间（秒）
    "timeout": 30,
    # 网络抖动重试（例如 SSL EOF）
    "max_retries": 12,
    "retry_backoff": 0.8,
    # 如遇到某些环境/代理导致 SSL 握手不稳定，可临时设为 True（不推荐长期使用）
    "insecure_ssl": False,
    # 下载后端： "auto" | "python" | "aria2c" | "curl"
    # - auto: 先用 python，多次失败后自动降级 aria2c/curl（如果系统里有）
    # - aria2c: 速度/断点续传最好（建议安装 aria2）
    # - curl: Windows 自带 curl，支持断点续传（但通常没 aria2c 快）
    "backend": "auto",
}

SSL_CONTEXT: ssl.SSLContext | None = None


def _which(cmd: str) -> str | None:
    try:
        p = subprocess.run(["where", cmd], capture_output=True, text=True, check=False)
        if p.returncode == 0:
            line = (p.stdout or "").strip().splitlines()[0].strip()
            return line or None
    except Exception:
        return None
    return None


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _download_with_aria2c(url: str, out_path: str, connections: int):
    exe = _which("aria2c")
    if not exe:
        raise RuntimeError("aria2c not found in PATH")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # -c resume, -x max connections per server, -s split, -k piece size
    args = [
        exe,
        "--continue=true",
        "--max-connection-per-server",
        str(max(1, min(connections, 16))),
        "--split",
        str(max(1, min(connections, 16))),
        "--min-split-size",
        "4M",
        "--out",
        os.path.basename(out_path),
        "--dir",
        os.path.dirname(out_path) or ".",
        url,
    ]
    started = time.time()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started))}")
    print("Using aria2c backend.")
    r = subprocess.run(args, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"aria2c failed with exit code {r.returncode}")
    ended = time.time()
    print(f"Finish time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))}")
    print(f"Elapsed: {_format_duration(ended - started)}")


def _download_with_curl(url: str, out_path: str, max_retries: int):
    exe = _which("curl")
    if not exe:
        raise RuntimeError("curl not found in PATH")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    args = [
        exe,
        "-L",
        "--fail",
        "--http1.1",
        "--retry",
        str(max(0, max_retries)),
        "--retry-all-errors",
        "--retry-delay",
        "1",
        "--connect-timeout",
        "15",
        "--speed-time",
        "30",
        "--speed-limit",
        "200000",
        "-C",
        "-",
        "-o",
        out_path,
        url,
    ]
    started = time.time()
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started))}")
    print("Using curl backend.")
    r = subprocess.run(args, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed with exit code {r.returncode}")
    ended = time.time()
    print(f"Finish time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))}")
    print(f"Elapsed: {_format_duration(ended - started)}")


def _format_bytes(n: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024
        i += 1
    if i == 0:
        return f"{int(n)}{units[i]}"
    return f"{n:.2f}{units[i]}"


def _safe_filename_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    name = os.path.basename(path) or "download.bin"
    return urllib.parse.unquote(name)


def _request(url: str, headers: dict, timeout: int):
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    merged = {**base_headers, **(headers or {})}
    req = urllib.request.Request(url, headers=merged, method="GET")
    return urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT)


def _head(url: str, timeout: int):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive",
        },
        method="HEAD",
    )
    return urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT)


def _get_remote_info(url: str, timeout: int, max_retries: int = 6, retry_backoff: float = 0.5):
    length = None
    accept_ranges = False
    final_url = url
    retries = 0
    backoff = float(retry_backoff)
    while retries <= max_retries:
        try:
            with _head(url, timeout=timeout) as resp:
                final_url = resp.geturl()
                cl = resp.headers.get("Content-Length")
                if cl is not None:
                    try:
                        length = int(cl)
                    except ValueError:
                        length = None
                ar = resp.headers.get("Accept-Ranges", "")
                accept_ranges = ("bytes" in ar.lower())
                if length is not None:
                    return final_url, length, accept_ranges
        except Exception:
            pass

        try:
            with _request(url, headers={"Range": "bytes=0-0"}, timeout=timeout) as resp:
                final_url = resp.geturl()
                cr = resp.headers.get("Content-Range")
                if cr:
                    # "bytes 0-0/12345"
                    if "/" in cr:
                        tail = cr.split("/")[-1].strip()
                        if tail.isdigit():
                            length = int(tail)
                            accept_ranges = True
                else:
                    cl = resp.headers.get("Content-Length")
                    if cl and cl.isdigit():
                        length = int(cl)
        except Exception:
            pass

        if length is not None:
            return final_url, length, accept_ranges

        retries += 1
        if retries <= max_retries:
            time.sleep(min(5.0, backoff))
            backoff *= 1.8

    return final_url, length, accept_ranges


class _Progress:
    def __init__(self, total: int | None):
        self.total = total
        self.lock = threading.Lock()
        self.downloaded = 0
        self._last_print = 0.0
        self._last_downloaded = 0
        self._last_ts = time.time()
        self.start_ts = self._last_ts

    def add(self, n: int):
        with self.lock:
            self.downloaded += n

    def start_time_str(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_ts))

    def maybe_print(self, force: bool = False):
        now = time.time()
        if not force and (now - self._last_print) < 0.5:
            return
        with self.lock:
            downloaded = self.downloaded
        dt = max(1e-6, now - self._last_ts)
        speed = (downloaded - self._last_downloaded) / dt
        self._last_downloaded = downloaded
        self._last_ts = now
        self._last_print = now

        elapsed = now - self.start_ts
        eta_str = "--:--"
        if self.total and speed > 1e-6 and downloaded <= self.total:
            remaining = self.total - downloaded
            eta_str = _format_duration(remaining / speed)

        if self.total:
            pct = downloaded / self.total * 100
            msg = (
                f"\r{_format_bytes(downloaded)}/{_format_bytes(self.total)} "
                f"({pct:6.2f}%)  {_format_bytes(speed)}/s  "
                f"elapsed {_format_duration(elapsed)}  eta {eta_str}"
            )
        else:
            msg = f"\r{_format_bytes(downloaded)}  {_format_bytes(speed)}/s  elapsed {_format_duration(elapsed)}"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def done(self):
        self.maybe_print(force=True)
        sys.stdout.write("\n")
        sys.stdout.flush()


def _download_range_to_part(
    url: str,
    part_path: str,
    start: int,
    end: int,
    timeout: int,
    progress: _Progress,
    stop_event: threading.Event,
):
    os.makedirs(os.path.dirname(part_path) or ".", exist_ok=True)
    max_retries = 8
    retries = 0
    backoff = 0.8

    while not stop_event.is_set():
        existing = os.path.getsize(part_path) if os.path.exists(part_path) else 0
        part_start = start + existing
        if part_start > end:
            return

        headers = {"Range": f"bytes={part_start}-{end}"}

        try:
            with _request(url, headers=headers, timeout=timeout) as resp:
                status = getattr(resp, "status", None)
                if status not in (200, 206, None):
                    raise RuntimeError(f"unexpected HTTP status: {status}")
                with open(part_path, "ab") as f:
                    while not stop_event.is_set():
                        chunk = resp.read(1024 * 256)
                        if not chunk:
                            break
                        f.write(chunk)
                        progress.add(len(chunk))
            retries = 0
            backoff = 0.8
        except Exception as ex:
            retries += 1
            if retries > max_retries:
                stop_event.set()
                raise RuntimeError(f"part download failed after retries: {ex}") from ex
            time.sleep(min(10.0, backoff))
            backoff *= 1.8
            continue


def _merge_parts(out_path: str, part_paths: list[str]):
    tmp_out = out_path + ".downloading"
    with open(tmp_out, "wb") as out:
        for p in part_paths:
            with open(p, "rb") as f:
                while True:
                    b = f.read(1024 * 1024)
                    if not b:
                        break
                    out.write(b)
    os.replace(tmp_out, out_path)


def download(
    url: str,
    out_path: str | None = None,
    connections: int = 16,
    timeout: int = 30,
    max_retries: int = 12,
    retry_backoff: float = 0.8,
):
    final_url, total, accept_ranges = _get_remote_info(
        url,
        timeout=timeout,
        max_retries=min(6, max_retries),
        retry_backoff=min(1.0, retry_backoff),
    )
    if out_path is None:
        out_path = _safe_filename_from_url(final_url)
    else:
        out_path = os.path.expanduser(out_path)
        if os.path.isdir(out_path):
            out_path = os.path.join(out_path, _safe_filename_from_url(final_url))
    out_path = os.path.abspath(out_path)
    base_dir = os.path.dirname(out_path) or "."
    os.makedirs(base_dir, exist_ok=True)

    if os.path.exists(out_path) and total and os.path.getsize(out_path) == total:
        print(f"Already downloaded: {out_path}")
        return

    if not total:
        print("Warning: cannot determine remote size; falling back to single stream.")
        accept_ranges = False

    if (not accept_ranges) or (connections <= 1):
        existing = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        progress = _Progress(total)
        progress.add(existing)
        started_str = progress.start_time_str()
        print(f"Start time: {started_str}")
        print(f"Downloading to: {out_path}")
        try:
            retries = 0
            backoff = float(retry_backoff)
            while True:
                headers = {}
                if existing > 0:
                    headers["Range"] = f"bytes={existing}-"

                try:
                    with _request(final_url, headers=headers, timeout=timeout) as resp:
                        status = getattr(resp, "status", None)
                        if existing > 0 and status == 200:
                            existing = 0
                            progress = _Progress(total)
                        mode = "ab" if existing > 0 else "wb"
                        with open(out_path, mode) as f:
                            while True:
                                chunk = resp.read(1024 * 256)
                                if not chunk:
                                    break
                                f.write(chunk)
                                existing += len(chunk)
                                progress.add(len(chunk))
                                progress.maybe_print()
                    break
                except (urllib.error.URLError, OSError) as ex:
                    retries += 1
                    if retries > max_retries:
                        raise RuntimeError(f"download failed after retries: {ex}") from ex
                    time.sleep(min(10.0, backoff))
                    backoff *= 1.8
                    continue
        finally:
            progress.done()
            ended = time.time()
            print(f"Finish time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))}")
            print(f"Elapsed: {_format_duration(ended - progress.start_ts)}")
        return

    part_dir = os.path.join(base_dir, "." + os.path.basename(out_path) + ".parts")
    os.makedirs(part_dir, exist_ok=True)

    connections = max(1, min(connections, 64))
    chunk_size = int(math.ceil(total / connections))
    ranges: list[tuple[int, int]] = []
    for i in range(connections):
        s = i * chunk_size
        e = min(total - 1, (i + 1) * chunk_size - 1)
        if s > e:
            break
        ranges.append((s, e))

    part_paths = [os.path.join(part_dir, f"part{i:03d}") for i in range(len(ranges))]

    progress = _Progress(total)
    for p, (s, e) in zip(part_paths, ranges):
        if os.path.exists(p):
            progress.add(os.path.getsize(p))

    started_str = progress.start_time_str()
    print(f"Start time: {started_str}")
    print(f"Downloading to: {out_path}")
    print(f"Connections: {len(ranges)}  Resume: enabled  Ranges: bytes")

    threads: list[threading.Thread] = []
    errors: list[BaseException] = []
    stop_event = threading.Event()

    def _runner(i: int):
        nonlocal errors
        try:
            s, e = ranges[i]
            _download_range_to_part(
                final_url,
                part_paths[i],
                s,
                e,
                timeout=timeout,
                progress=progress,
                stop_event=stop_event,
            )
        except BaseException as ex:
            errors.append(ex)

    for i in range(len(ranges)):
        t = threading.Thread(target=_runner, args=(i,), daemon=True)
        threads.append(t)
        t.start()

    try:
        while any(t.is_alive() for t in threads):
            if errors:
                stop_event.set()
                break
            progress.maybe_print()
            time.sleep(0.2)
    finally:
        for t in threads:
            t.join()
        progress.done()

    if errors:
        raise RuntimeError(f"download failed: {errors[0]}")

    for p, (s, e) in zip(part_paths, ranges):
        expected = (e - s + 1)
        got = os.path.getsize(p) if os.path.exists(p) else 0
        if got != expected:
            raise RuntimeError(f"part size mismatch: {os.path.basename(p)} got {got}, expected {expected}")

    _merge_parts(out_path, part_paths)
    print(f"Done: {out_path}")
    ended = time.time()
    print(f"Finish time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ended))}")
    print(f"Elapsed: {_format_duration(ended - progress.start_ts)}")


def run_from_config():
    try:
        global SSL_CONTEXT
        if CONFIG.get("insecure_ssl"):
            SSL_CONTEXT = ssl._create_unverified_context()
        else:
            SSL_CONTEXT = None

        url = CONFIG["url"]
        out = CONFIG.get("out")
        connections = int(CONFIG.get("connections", 16))
        timeout = int(CONFIG.get("timeout", 30))
        max_retries = int(CONFIG.get("max_retries", 12))
        retry_backoff = float(CONFIG.get("retry_backoff", 0.8))
        backend = str(CONFIG.get("backend", "auto")).lower().strip()

        # normalize output path early (support directory)
        final_url, _, _ = _get_remote_info(url, timeout=min(timeout, 10), max_retries=1, retry_backoff=0.2)
        if out is None:
            out_path = _safe_filename_from_url(final_url)
        else:
            out_path = os.path.expanduser(out)
            if os.path.isdir(out_path):
                out_path = os.path.join(out_path, _safe_filename_from_url(final_url))
        out_path = os.path.abspath(out_path)

        if backend == "aria2c":
            _download_with_aria2c(url, out_path, connections=connections)
        elif backend == "curl":
            _download_with_curl(url, out_path, max_retries=max_retries)
        else:
            try:
                download(
                    url,
                    out_path=out_path,
                    connections=connections,
                    timeout=timeout,
                    max_retries=max_retries,
                    retry_backoff=retry_backoff,
                )
            except Exception as ex:
                if backend == "python":
                    raise
                # auto fallback
                print(f"Python backend failed: {ex}")
                try:
                    _download_with_aria2c(url, out_path, connections=connections)
                except Exception as ex2:
                    print(f"aria2c fallback failed: {ex2}")
                    _download_with_curl(url, out_path, max_retries=max_retries)
        return True
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    run_from_config()


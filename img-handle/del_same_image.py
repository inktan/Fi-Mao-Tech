from __future__ import annotations

from PIL import Image
import imagehash
import os
import time
import sqlite3
from tqdm import tqdm
import ctypes
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('run_work.log'),  # 日志文件名
        logging.StreamHandler()  # 控制台输出
    ]
)
logger = logging.getLogger(__name__)

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE_DB = os.path.join(SCRIPT_DIR, "image_dedupe_cache.sqlite3")

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行原始函数
        end_time = time.time()  # 记录函数结束执行的时间
        elapsed_time = end_time - start_time  # 计算耗时
        print(f"{func.__name__} 耗时: {elapsed_time:.6f} 秒")  # 打印耗时
        return result  # 返回原始函数的结果
    return wrapper

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

@dataclass(frozen=True)
class ImageMeta:
    path: str
    size: int
    mtime: float


def _get_image_meta(path: str) -> Optional[ImageMeta]:
    try:
        st = os.stat(path)
        return ImageMeta(path=path, size=int(st.st_size), mtime=float(st.st_mtime))
    except OSError:
        return None


def _init_cache_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS image_hash_cache (
            path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            mtime REAL NOT NULL,
            algo TEXT NOT NULL,
            hash TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_algo_hash ON image_hash_cache(algo, hash)")
    conn.commit()


def _load_cached_hashes(
    conn: sqlite3.Connection,
    metas: List[ImageMeta],
    algo: str,
) -> Dict[str, str]:
    if not metas:
        return {}
    cached: Dict[str, str] = {}
    # SQLite 单次 IN 参数数量有限，分批查询
    batch = 500
    for i in range(0, len(metas), batch):
        part = metas[i : i + batch]
        placeholders = ",".join(["?"] * len(part))
        params: List[object] = []
        for m in part:
            params.extend([m.path])
        rows = conn.execute(
            f"SELECT path, size, mtime, hash FROM image_hash_cache WHERE algo=? AND path IN ({placeholders})",
            [algo, *params],
        ).fetchall()
        row_map = {r[0]: (int(r[1]), float(r[2]), str(r[3])) for r in rows}
        for m in part:
            hit = row_map.get(m.path)
            if hit and hit[0] == m.size and hit[1] == m.mtime:
                cached[m.path] = hit[2]
    return cached


def _upsert_cached_hashes(
    conn: sqlite3.Connection,
    algo: str,
    items: Iterable[Tuple[ImageMeta, str]],
) -> None:
    conn.executemany(
        """
        INSERT INTO image_hash_cache(path, size, mtime, algo, hash)
        VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            size=excluded.size,
            mtime=excluded.mtime,
            algo=excluded.algo,
            hash=excluded.hash
        """,
        [(m.path, m.size, m.mtime, algo, hv) for (m, hv) in items],
    )


def _compute_phash(path: str) -> Optional[str]:
    try:
        # 读文件 + 解码是 I/O + CPU，放到进程池里更能吃满多核
        with Image.open(path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None


def _pick_workers(user_workers: Optional[int]) -> int:
    cpu = os.cpu_count() or 4
    if user_workers is not None and user_workers > 0:
        return int(user_workers)
    # 默认留 1 个核心，尽量不把电脑卡死
    return max(1, cpu - 1)


def _bounded_submit_phash(
    paths: List[str],
    workers: int,
    max_in_flight: int,
) -> Dict[str, Optional[str]]:
    """
    受控并发：限制在途任务数，避免一次性提交太多导致内存上升/磁盘抖动。
    返回 {path: phash_or_none}
    """
    results: Dict[str, Optional[str]] = {}
    if not paths:
        return results

    if max_in_flight <= 0:
        max_in_flight = max(32, workers * 8)

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {}
        it = iter(paths)

        def submit_next() -> bool:
            try:
                p = next(it)
            except StopIteration:
                return False
            fut = ex.submit(_compute_phash, p)
            futures[fut] = p
            return True

        # 先填满窗口
        for _ in range(min(max_in_flight, len(paths))):
            if not submit_next():
                break

        with tqdm(total=len(paths)) as pbar:
            while futures:
                for fut in as_completed(list(futures.keys()), timeout=None):
                    p = futures.pop(fut)
                    hv = None
                    try:
                        hv = fut.result()
                    except Exception:
                        hv = None
                    results[p] = hv
                    pbar.update(1)
                    # 补充新任务保持窗口
                    submit_next()
                    # 这里 break 是为了让窗口补充更及时，减少一次性遍历 as_completed 列表的开销
                    break
    return results


def _delete_file_with_elevation_if_needed(path: str) -> bool:
    try:
        os.remove(path)
        return True
    except Exception:
        if not is_admin():
            print("没有足够的权限删除文件，请以管理员身份运行此脚本。")
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
            except Exception:
                pass
        else:
            print("即使以管理员身份运行，也无法删除文件。文件可能被系统或其他程序占用。")
        return False


def remove_duplicate_images(
    img_paths: List[str],
    *,
    cache_db: str = DEFAULT_CACHE_DB,
    workers: Optional[int] = None,
    max_in_flight: int = 0,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    以 phash 进行“视觉相似”去重：相同 phash 视为重复。
    返回 (扫描成功数, 删除数)
    """
    metas = [m for m in (_get_image_meta(p) for p in img_paths) if m is not None]
    if not metas:
        return (0, 0)

    algo = "phash"
    conn = sqlite3.connect(cache_db)
    try:
        _init_cache_db(conn)
        cached = _load_cached_hashes(conn, metas, algo)

        need_compute = [m for m in metas if m.path not in cached]
        need_paths = [m.path for m in need_compute]

        w = _pick_workers(workers)
        logger.info("总图片: %d, 命中缓存: %d, 需计算: %d, workers=%d, in_flight=%d",
                    len(metas), len(cached), len(need_paths), w,
                    (max_in_flight if max_in_flight > 0 else max(32, w * 8)))

        computed_map = _bounded_submit_phash(
            need_paths,
            workers=w,
            max_in_flight=max_in_flight,
        )

        # 写回缓存（只写成功的）
        upserts: List[Tuple[ImageMeta, str]] = []
        for m in need_compute:
            hv = computed_map.get(m.path)
            if hv:
                upserts.append((m, hv))
        if upserts:
            _upsert_cached_hashes(conn, algo, upserts)
            conn.commit()

        # 合并最终 hash 映射
        all_hashes: Dict[str, str] = dict(cached)
        for p, hv in computed_map.items():
            if hv:
                all_hashes[p] = hv

        # 去重：同 hash 保留第一张，其余删除
        first_by_hash: Dict[str, str] = {}
        duplicates: List[str] = []
        for m in metas:
            hv = all_hashes.get(m.path)
            if not hv:
                continue
            if hv in first_by_hash:
                duplicates.append(m.path)
            else:
                first_by_hash[hv] = m.path

        deleted = 0
        for p in duplicates:
            if dry_run:
                continue
            if _delete_file_with_elevation_if_needed(p):
                deleted += 1
        if dry_run:
            logger.info("dry-run: 发现重复 %d（未删除）", len(duplicates))
        else:
            logger.info("删除重复 %d", deleted)
        return (len(all_hashes), deleted)
    finally:
        conn.close()

# 使用装饰器
@timer_decorator
def main():
    # ========== 配置（在 VSCode 里直接改这里，然后运行） ==========
    folder_path_list = [
        r"F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\泉州市",
    ]
    workers = 0          # 并行进程数：0=自动(CPU-1)，>0 为指定数量
    in_flight = 0        # 在途任务数：0=自动，>0 可限制磁盘/内存压力
    cache_db = DEFAULT_CACHE_DB
    dry_run = False      # True=只统计重复不删除，False=真正删除

    # 根据配置得到实际参数
    if workers and workers > 0:
        w = workers
    else:
        w = None
    if in_flight > 0:
        max_in_flight = in_flight
    else:
        max_in_flight = 0

    accepted_formats = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")
    img_paths: List[str] = []
    for folder_path in folder_path_list:
        for root, _dirs, files in os.walk(folder_path):
            for file in files:
                lower = file.lower()
                if lower.endswith(accepted_formats):
                    img_paths.append(os.path.join(root, file))

    logger.info("收集到图片路径: %d", len(img_paths))
    remove_duplicate_images(
        img_paths,
        cache_db=cache_db,
        workers=w,
        max_in_flight=max_in_flight,
        dry_run=dry_run,
    )

if __name__ == '__main__':
    print('a01')
    main()





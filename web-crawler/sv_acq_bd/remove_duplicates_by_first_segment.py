# -*- coding: cp936 -*-
import json
import os
from pathlib import Path
from collections import defaultdict

import geopandas as gpd
import matplotlib.pyplot as plt

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"}


def get_image_files(folder_path):

    folder = Path(folder_path)
    if not folder.is_dir():
        return []
    return [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]


def remove_duplicates_by_first_segment(work_folder):

    work_folder = Path(work_folder)
    images = get_image_files(work_folder)
    if not images:
        return 0

    by_first = defaultdict(list)
    for f in images:
        stem = f.stem  # 不含扩展名的文件名
        parts = stem.split("_")
        first = parts[0] if parts else ""
        by_first[first].append((len(parts), f))
    print(len(images))
    deleted = 0
    for first_seg, candidates in by_first.items():
        if len(candidates) <= 1:
            continue

        candidates.sort(key=lambda x: (-x[0], str(x[1])))
        to_keep = candidates[0][1]
        for _, path in candidates[1:]:
            try:
                path.unlink()
                deleted += 1
                print(f"  已删除（元素较少）: {path.name}")
            except OSError as e:
                print(f"  删除失败: {path} -> {e}")
    return deleted


def process_sv_pan26_folders(root_folder):

    root = Path(root_folder)
    if not root.is_dir():
        print(f"错误：不是有效目录 {root_folder}")
        return

    total_deleted = 0
    for dirpath, dirnames, _ in os.walk(root):
        print(dirpath)
        print(dirnames)
        if "sv_pan26" in dirnames:
            work_dir = Path(dirpath) / "sv_pan26"
            print(f"处理工作目录: {work_dir}")
            n = remove_duplicates_by_first_segment(work_dir)
            total_deleted += n
            # 不再进入 sv_pan26 内部继续当作普通子目录遍历（已单独处理）
            dirnames.remove("sv_pan26")

    print(f"共删除 {total_deleted} 个重复图片文件。")
      
ROOT_FOLDER = r"H:\_50m_point\北京市"
if __name__ == "__main__":
    process_sv_pan26_folders(ROOT_FOLDER)

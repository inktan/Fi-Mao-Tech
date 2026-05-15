# -*- coding: utf-8 -*-
"""
读取指定目录下所有图片文件名，按 '_' 分割：
1. 第一元素相同的归为同一路段（一类）；
2. 在同类中统计第五个元素（索引 4）的出现次数；
3. 输出：该路段总点数、第五元素发生重复所涉及的点数、重复率。

重复判定：若某张图第五元素在该路段内出现次数 > 1，则该图计为「重复相关点」。
重复率 = 重复相关点数 / 总点数。
"""
from __future__ import annotations

import os
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_DIR = Path(r"E:\work\sv_tw\google_pan_top5_test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def collect_image_stems(folder: Path) -> list[str]:
    names: list[str] = []
    if not folder.is_dir():
        return names
    for _root, _dirs, files in os.walk(folder):
        for f in files:
            suf = Path(f).suffix.lower()
            if suf in IMAGE_SUFFIXES:
                names.append(Path(f).stem)
    return names


def parse_and_group(stems: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    """
    返回：路段 -> 该路段每张图第五个元素（若合法）；skipped 为无法解析的文件名（不含扩展名）。
    """
    fifth_by_segment: dict[str, list[str]] = defaultdict(list)
    skipped: list[str] = []

    for stem in stems:
        parts = stem.split("_")
        if len(parts) < 5:
            skipped.append(stem)
            continue
        seg = parts[0]
        fifth = parts[4]
        fifth_by_segment[seg].append(fifth)

    return dict(fifth_by_segment), skipped


def segment_stats(fifths: list[str]) -> tuple[int, int, float]:
    """
    总点数 N，第五元素出现次数>1 所涉及的图片数 R，重复率 R/N。
    """
    n = len(fifths)
    if n == 0:
        return 0, 0, 0.0
    freq = Counter(fifths)
    dup_keys = {k for k, c in freq.items() if c > 1}
    r = sum(freq[k] for k in dup_keys)
    rate = r / n
    return n, r, rate


def main() -> None:
    folder = IMAGE_DIR
    stems = collect_image_stems(folder)
    if not stems:
        print(f"目录下未发现图片：{folder}")
        return

    grouped, skipped = parse_and_group(stems)

    if skipped:
        print(f"警告：以下 {len(skipped)} 个文件名 '_' 分割后不足 5 段，已跳过：")
        for s in skipped[:20]:
            print(f"  {s}")
        if len(skipped) > 20:
            print(f"  ... 另有 {len(skipped) - 20} 个")

    print(f"扫描目录：{folder}")
    print(f"图片总数：{len(stems)}")
    print(f"路段数（第一元素种类）：{len(grouped)}")
    print("")

    # 按路段名排序输出
    for seg in sorted(grouped.keys(), key=lambda x: (len(str(x)), str(x))):
        fifths = grouped[seg]
        n, r, rate = segment_stats(fifths)
        u = len(set(fifths))
        print(f"路段（第一元素）={seg!r}")
        print(f"  总点数（图片数）: {n}")
        print(f"  第五元素不同取值数: {u}")
        print(f"  第五元素与其他点重复所涉点数: {r}")
        print(f"  重复率: {rate * 100:.2f}%")
        print("")

    # 汇总
    total_n = sum(len(v) for v in grouped.values())
    total_r = 0
    for fifths in grouped.values():
        _n, r, _ = segment_stats(fifths)
        total_r += r
    overall = (total_r / total_n) if total_n else 0.0
    print("—" * 40)
    print(f"全部路段合计 — 总点数: {total_n}，重复涉及点数: {total_r}，整体重复率: {overall * 100:.2f}%")


if __name__ == "__main__":
    main()

"""
遍历目录下 CSV：对两列数值求和，若和 > 阈值，则根据 id 列文件路径，
将路径中的 _fixed 替换为 _fixed_arch，并把该文件移动到新路径。
"""
from __future__ import annotations

import os
import shutil

import pandas as pd

# 根目录列表（递归扫描其下所有 .csv）
csv_path_list = [
    r"D:\work\work_zhoujunling",
]

accepted_formats = (".csv",)
# 求和后大于该值的行才会触发移动
THRESHOLD = 0.3
# id 列名（存放待移动文件的完整路径）
ID_COL = "id"
# 路径中需要替换的片段
OLD_TOKEN = "_fiexd"
NEW_TOKEN = "_fixed_arch"

# 参与求和的两列表头候选：按顺序匹配，使用第一组两列都存在的组合
SUM_COL_PAIRS = [
    ("wall", "building;edifice"),
]


def read_csv_flexible(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path)


def pick_sum_columns(df: pd.DataFrame) -> tuple[str, str]:
    cols = set(df.columns.astype(str))
    for a, b in SUM_COL_PAIRS:
        if a in cols and b in cols:
            return a, b
    raise KeyError(
        f"未找到可用的两列组合 {SUM_COL_PAIRS}，实际列名为: {list(df.columns)}"
    )


def collect_csv_paths(folders: list[str]) -> list[str]:
    out: list[str] = []
    for folder_path in folders:
        if not os.path.isdir(folder_path):
            print(f"[跳过] 目录不存在: {folder_path}")
            continue
        for root, _dirs, files in os.walk(folder_path):
            for name in files:
                if name.lower().endswith(accepted_formats):
                    out.append(os.path.join(root, name))
    return out


def main() -> None:
    csv_paths = collect_csv_paths(csv_path_list)
    csv_paths = [r'd:\work\work_zhoujunling\aomen_fiexd\sv_pan_02_ss_02.csv']
    if not csv_paths:
        print("未找到任何 CSV 文件。")
        return

    for csv_path in csv_paths:
        print(f"\n--- 处理: {csv_path}")
        try:
            df = read_csv_flexible(csv_path)
        except Exception as e:
            print(f"  读取失败: {e}")
            continue

        if ID_COL not in df.columns:
            print(f"  缺少列 {ID_COL!r}，跳过。列名: {list(df.columns)}")
            continue

        try:
            col_a, col_b = pick_sum_columns(df)
        except KeyError as e:
            print(f"  {e}")
            continue

        s_a = pd.to_numeric(df[col_a], errors="coerce").fillna(0)
        s_b = pd.to_numeric(df[col_b], errors="coerce").fillna(0)
        row_sum = s_a + s_b
        mask = row_sum > THRESHOLD
        sub = df.loc[mask, ID_COL].dropna()

        for raw in sub.astype(str):
            src = raw.strip()
            if not src:
                continue
            if OLD_TOKEN not in src:
                print(f"  [跳过] 路径中无 {OLD_TOKEN!r}: {src}")
                continue
            dst = src.replace(OLD_TOKEN, NEW_TOKEN, 1)
            if os.path.normpath(src) == os.path.normpath(dst):
                continue
            if not os.path.isfile(src):
                print(f"  [跳过] 源文件不存在: {src}")
                continue
            ddir = os.path.dirname(dst)
            if ddir:
                os.makedirs(ddir, exist_ok=True)
            if os.path.exists(dst):
                print(f"  [跳过] 目标已存在: {dst}")
                continue
            try:
                shutil.move(src, dst)
                print(f"  已移动: {src} -> {dst}")
            except OSError as e:
                print(f"  移动失败: {src} -> {dst}: {e}")


if __name__ == "__main__":
    main()

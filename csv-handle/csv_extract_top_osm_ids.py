"""
从 CSV 中按 osm_id 出现次数统计，取频次最高的前 5 个 osm_id，
导出这些 id 对应的全部行到新 CSV。
"""
from pathlib import Path

import pandas as pd

INPUT_CSV = Path(r"E:\work\sv_tw\test_network_10m_Optimized.csv")
OUTPUT_CSV = Path(r"E:\work\sv_tw\test_network_10m_Optimized_top5_osm_ids.csv")
TOP_N = 5
OSM_COL = "osm_id"


def main() -> None:
    if not INPUT_CSV.is_file():
        raise FileNotFoundError(f"找不到输入文件：{INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    col = OSM_COL
    if col not in df.columns:
        lower_map = {c.lower(): c for c in df.columns}
        if "osm_id" in lower_map:
            col = lower_map["osm_id"]
        else:
            raise ValueError(f"缺少 {OSM_COL} 列，当前列：{list(df.columns)}")

    counts = df[col].value_counts()
    top = counts.head(TOP_N)
    top_ids = top.index.tolist()

    filtered = df[df[col].isin(top_ids)]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"输入: {INPUT_CSV}  总行数: {len(df)}")
    print(f"频次前 {len(top)} 个 {OSM_COL} 及计数:")
    for oid, cnt in top.items():
        print(f"  {oid}: {cnt}")
    print(f"导出行数: {len(filtered)}")
    print(f"输出: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

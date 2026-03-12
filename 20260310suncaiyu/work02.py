# -*- coding: utf-8 -*-
"""
读取 output_by_road 下每个 CSV，将明度/彩度/协调度分别归一化到 0-10，
绘制横轴为点 ID、纵轴为数值、三条折线的图表，每个 CSV 保存一张图。
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_FOLDER = r"E:\work\work_suncaiyu\output_by_road"
CHARTS_OUTPUT_FOLDER = r"E:\work\work_suncaiyu\output_by_road_charts"  # 图表保存目录
COLUMNS = ["明度", "彩度", "协调度"]
VALUE_RANGE = (0, 10)
# 是否在折线峰值处画红色圆圈（类似参考图）
MARK_PEAKS = True


def normalize_to_range(series: pd.Series, low: float = 0, high: float = 10) -> pd.Series:
    """将一列数据 min-max 归一化到 [low, high]。常数列或全 NaN 返回中间值。"""
    out = pd.to_numeric(series, errors="coerce")
    valid = out.dropna()
    if valid.empty or valid.nunique() <= 1:
        return pd.Series([(low + high) / 2] * len(out), index=out.index)
    mn, mx = valid.min(), valid.max()
    if mx == mn:
        return pd.Series([(low + high) / 2] * len(out), index=out.index)
    return low + (out - mn) / (mx - mn) * (high - low)


def _local_max_indices(y: np.ndarray) -> np.ndarray:
    """返回局部最大值的索引（相邻三点中间最大）。"""
    n = len(y)
    if n < 3:
        return np.array([], dtype=int)
    idx = []
    for i in range(1, n - 1):
        if y[i] >= y[i - 1] and y[i] >= y[i + 1]:
            idx.append(i)
    return np.array(idx, dtype=int)


def plot_indicators(csv_path: str, out_path: str) -> None:
    """
    读取单个 CSV，对明度/彩度/协调度分别归一化到 0-10，绘制三条折线并保存。
    """
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f"CSV 缺少列 {missing}：{csv_path}")

    # 横轴：自动从 0, 1, 2, 3, ... 开始，按行顺序
    n = len(df)
    x = np.arange(n)

    # 通过列名获取明度、彩度、协调度，分别归一化到 0-10
    data = {name: normalize_to_range(df[name], *VALUE_RANGE) for name in COLUMNS}

    plt.close("all")
    fig, ax = plt.subplots(figsize=(14, 5))  # 加长画面
    ax.set_xlabel("点ID")
    ax.set_ylabel("数值")
    ax.set_ylim(VALUE_RANGE)
    ax.set_yticks(np.arange(VALUE_RANGE[0], VALUE_RANGE[1] + 1, 1))
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    # 三条折线：线条更细
    colors = ["#5B9BD5", "#70AD47", "#ED7D31"]  # 浅蓝、绿、橙
    for i, name in enumerate(COLUMNS):
        y = data[name].values
        ax.plot(x, y, color=colors[i], linewidth=1, label=name)
        if MARK_PEAKS:
            peak_idx = _local_max_indices(y)
            if len(peak_idx) > 0:
                ax.scatter(
                    x[peak_idx],
                    y[peak_idx],
                    color="red",
                    s=40,
                    zorder=5,
                    edgecolors="darkred",
                    linewidths=1,
                )

    # 图例放在图下方，一行显示
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=True)
    fig.tight_layout(rect=[0, 0.08, 1, 1])  # 底部留空给图例
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    folder = Path(OUTPUT_FOLDER)
    out_folder = Path(CHARTS_OUTPUT_FOLDER)
    if not folder.exists():
        print(f"目录不存在: {folder}")
        return
    out_folder.mkdir(parents=True, exist_ok=True)

    csv_files = list(folder.glob("*.csv"))
    if not csv_files:
        print(f"未在 {folder} 中找到 CSV 文件")
        return

    for csv_path in sorted(csv_files):
        base = csv_path.stem
        out_path = out_folder / f"{base}.png"
        try:
            plot_indicators(str(csv_path), str(out_path))
            print(f"已保存: {out_path}")
        except Exception as e:
            print(f"处理 {csv_path.name} 失败: {e}")

    print(f"共处理 {len(csv_files)} 个 CSV，图表保存在: {out_folder}")


if __name__ == "__main__":
    main()

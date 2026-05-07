from __future__ import annotations

from pathlib import Path
import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)


plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300


BRAND_COLORS = {
    "Apple": "#111111",
    "Samsung": "#1565C0",
    "Huawei": "#C62828",
    "Lenovo": "#6A1B9A",
    "Xiaomi": "#EF6C00",
    "Amazon": "#00838F",
    "Honor": "#2E7D32",
    "Oppo": "#43A047",
    "Others": "#B0BEC5",
    "Total": "#455A64",
}

KEY_BRANDS = ["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi", "Amazon", "Others"]


def quarter_key(period: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})Q([1-4])", str(period))
    if not match:
        raise ValueError(f"Unexpected quarter format: {period}")
    return int(match.group(1)), int(match.group(2))


def period_sort_values(series: pd.Series) -> list[str]:
    return sorted(series.dropna().unique().tolist(), key=quarter_key)


def parse_thickness(dimensions: str) -> float | None:
    if not isinstance(dimensions, str):
        return None
    parts = [p.strip() for p in dimensions.split("x")]
    if len(parts) != 3:
        return None
    try:
        return float(parts[2])
    except ValueError:
        return None


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = pd.read_csv(DATA_DIR / "tablet_models_2020_2025.csv")
    perf = pd.read_csv(DATA_DIR / "tablet_perf_2020_2025.csv")
    market = pd.read_csv(DATA_DIR / "tablet_market_2020_2025.csv")
    models["thickness_mm"] = models["dimensions_mm"].apply(parse_thickness)
    return models, perf, market


def merge_models_perf(models: pd.DataFrame, perf: pd.DataFrame) -> pd.DataFrame:
    merged = models.merge(perf, on="soc", how="left")
    merged["brand_color"] = merged["brand"].map(BRAND_COLORS).fillna("#607D8B")
    return merged


def style_axes(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_fig(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / name, bbox_inches="tight")
    plt.close(fig)


def plot_market_total(market: pd.DataFrame) -> None:
    total = market[market["brand"] == "Total"].copy()
    total["sort_key"] = total["market_period"].map(quarter_key)
    total = total.sort_values("sort_key")

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(total))
    y = total["shipments_k"] / 1000
    ax.plot(x, y, color=BRAND_COLORS["Total"], linewidth=2.8, marker="o")
    ax.fill_between(x, y, color="#CFD8DC", alpha=0.35)

    peak_idx = y.idxmax()
    low_idx = y.idxmin()
    peak_pos = total.index.get_loc(peak_idx)
    low_pos = total.index.get_loc(low_idx)

    ax.annotate(
        f"Peak: {total.loc[peak_idx, 'market_period']}\n{y.loc[peak_idx]:.2f}M",
        xy=(peak_pos, y.loc[peak_idx]),
        xytext=(peak_pos - 2, y.loc[peak_idx] + 4),
        arrowprops={"arrowstyle": "->", "color": "#455A64"},
        fontsize=10,
    )
    ax.annotate(
        f"Low: {total.loc[low_idx, 'market_period']}\n{y.loc[low_idx]:.2f}M",
        xy=(low_pos, y.loc[low_idx]),
        xytext=(low_pos + 1, y.loc[low_idx] + 3),
        arrowprops={"arrowstyle": "->", "color": "#455A64"},
        fontsize=10,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(total["market_period"], rotation=45, ha="right")
    style_axes(ax, "全球平板季度总出货量趋势（2020Q1-2025Q2）", ylabel="出货量（百万台）")
    save_fig(fig, "01_market_total_trend.png")


def plot_market_share_area(market: pd.DataFrame) -> None:
    subset = market[market["brand"].isin(KEY_BRANDS)].copy()
    pivot = subset.pivot(index="market_period", columns="brand", values="market_share_pct").fillna(0)
    pivot = pivot.loc[period_sort_values(pivot.index.to_series())]

    labels = [b for b in KEY_BRANDS if b in pivot.columns]
    colors = [BRAND_COLORS.get(b, "#90A4AE") for b in labels]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(pivot))
    ax.stackplot(x, [pivot[b].values for b in labels], labels=labels, colors=colors, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    ax.set_ylim(0, 100)
    style_axes(ax, "主要品牌市场份额堆叠面积图", ylabel="市场份额（%）")
    ax.legend(loc="upper left", ncol=4, frameon=False)
    save_fig(fig, "02_brand_market_share_area.png")


def plot_market_share_lines(market: pd.DataFrame) -> None:
    brands = ["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi"]
    subset = market[market["brand"].isin(brands)].copy()
    pivot = subset.pivot(index="market_period", columns="brand", values="market_share_pct").fillna(np.nan)
    pivot = pivot.loc[period_sort_values(pivot.index.to_series())]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(pivot))
    for brand in brands:
        if brand in pivot.columns:
            ax.plot(
                x,
                pivot[brand].values,
                linewidth=2.4,
                marker="o",
                label=brand,
                color=BRAND_COLORS.get(brand, "#607D8B"),
            )

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")
    style_axes(ax, "重点品牌市场份额变化（2020Q1-2025Q2）", ylabel="市场份额（%）")
    ax.legend(frameon=False, ncol=3)
    save_fig(fig, "03_brand_share_lines.png")


def plot_size_weight_perf_scatter(merged: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 7))
    for brand, group in merged.groupby("brand"):
        sizes = group["cpu_score_multi"].fillna(group["cpu_score_multi"].median()).fillna(2000) / 8
        ax.scatter(
            group["screen_size_in"],
            group["weight_g"],
            s=sizes,
            alpha=0.72,
            c=BRAND_COLORS.get(brand, "#607D8B"),
            edgecolors="white",
            linewidths=0.8,
            label=brand,
        )

    highlights = ["iPad Pro 11 (2024)", "Galaxy Tab S10 Ultra Wi-Fi", "MatePad Pro 13.2", "Pad 6S Pro 12.4"]
    for _, row in merged[merged["model"].isin(highlights)].iterrows():
        ax.annotate(
            row["model"],
            xy=(row["screen_size_in"], row["weight_g"]),
            xytext=(4, 6),
            textcoords="offset points",
            fontsize=9,
        )

    style_axes(ax, "屏幕尺寸-重量-性能气泡图", xlabel="屏幕尺寸（英寸）", ylabel="重量（g）")
    ax.legend(frameon=False, ncol=4, loc="upper left")
    save_fig(fig, "04_screen_weight_perf_scatter.png")


def plot_perf_ranking(merged: pd.DataFrame) -> None:
    ranked = merged.dropna(subset=["cpu_score_multi"]).copy()
    ranked = ranked.sort_values("cpu_score_multi", ascending=False).head(15)
    ranked["label"] = ranked["brand"] + " | " + ranked["model"]

    fig, ax = plt.subplots(figsize=(11.5, 7.5))
    y = np.arange(len(ranked))
    colors = ranked["brand"].map(BRAND_COLORS).fillna("#607D8B")
    ax.barh(y, ranked["cpu_score_multi"], color=colors, alpha=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(ranked["label"])
    ax.invert_yaxis()

    for idx, value in enumerate(ranked["cpu_score_multi"]):
        ax.text(value + 120, idx, f"{int(value)}", va="center", fontsize=9)

    style_axes(ax, "代表型号多核性能排名（Top 15）", xlabel="Geekbench 多核分数")
    save_fig(fig, "05_model_perf_ranking.png")


def plot_form_factor_trends(merged: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharex=False)

    ax1, ax2 = axes
    for brand, group in merged.groupby("brand"):
        yearly = group.groupby("release_year", as_index=False).agg(
            screen_size_in=("screen_size_in", "mean"),
            thickness_mm=("thickness_mm", "mean"),
        )
        ax1.plot(
            yearly["release_year"],
            yearly["screen_size_in"],
            marker="o",
            linewidth=2,
            color=BRAND_COLORS.get(brand, "#607D8B"),
            label=brand,
        )
        ax2.plot(
            yearly["release_year"],
            yearly["thickness_mm"],
            marker="o",
            linewidth=2,
            color=BRAND_COLORS.get(brand, "#607D8B"),
            label=brand,
        )

    style_axes(ax1, "屏幕尺寸演进", xlabel="发布年份", ylabel="平均屏幕尺寸（英寸）")
    style_axes(ax2, "厚度演进", xlabel="发布年份", ylabel="平均厚度（mm）")
    ax1.legend(frameon=False, ncol=2, fontsize=9, loc="upper left")
    save_fig(fig, "06_form_factor_trends.png")


def plot_display_type_structure(models: pd.DataFrame) -> None:
    display_map = {
        "IPS": "IPS",
        "OLED": "OLED",
        "AMOLED": "AMOLED",
        "Dynamic AMOLED 2X": "AMOLED",
    }
    chart = models.copy()
    chart["display_group"] = chart["display_type"].map(display_map).fillna("Other")
    pivot = pd.crosstab(chart["brand"], chart["display_group"])
    display_order = [d for d in ["IPS", "OLED", "AMOLED", "Other"] if d in pivot.columns]
    pivot = pivot[display_order]

    display_colors = {
        "IPS": "#90CAF9",
        "OLED": "#F06292",
        "AMOLED": "#7E57C2",
        "Other": "#BDBDBD",
    }

    fig, ax = plt.subplots(figsize=(11, 6))
    bottom = np.zeros(len(pivot))
    y = np.arange(len(pivot))
    for display in display_order:
        values = pivot[display].values
        ax.barh(y, values, left=bottom, color=display_colors[display], label=display, alpha=0.92)
        bottom += values

    ax.set_yticks(y)
    ax.set_yticklabels(pivot.index)
    style_axes(ax, "品牌显示技术结构图", xlabel="代表型号数量")
    ax.legend(frameon=False, ncol=4, loc="upper right")
    save_fig(fig, "07_display_type_structure.png")


def build_dashboard(market: pd.DataFrame, merged: pd.DataFrame, models: pd.DataFrame) -> None:
    total = market[market["brand"] == "Total"].copy()
    total["sort_key"] = total["market_period"].map(quarter_key)
    total = total.sort_values("sort_key")

    share = market[market["brand"].isin(["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi"])].copy()
    share_pivot = share.pivot(index="market_period", columns="brand", values="market_share_pct").fillna(np.nan)
    share_pivot = share_pivot.loc[period_sort_values(share_pivot.index.to_series())]

    top_perf = merged.dropna(subset=["cpu_score_multi"]).sort_values("cpu_score_multi", ascending=False).head(10)

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1], width_ratios=[1.05, 1])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    x_total = np.arange(len(total))
    ax1.plot(x_total, total["shipments_k"] / 1000, color=BRAND_COLORS["Total"], linewidth=2.6, marker="o")
    ax1.fill_between(x_total, total["shipments_k"] / 1000, color="#CFD8DC", alpha=0.35)
    ax1.set_xticks(x_total[::2])
    ax1.set_xticklabels(total["market_period"].iloc[::2], rotation=45, ha="right")
    style_axes(ax1, "全球平板季度总出货量", ylabel="百万台")

    x_share = np.arange(len(share_pivot))
    for brand in share_pivot.columns:
        ax2.plot(x_share, share_pivot[brand], label=brand, linewidth=2.2, color=BRAND_COLORS.get(brand, "#607D8B"))
    ax2.set_xticks(x_share[::2])
    ax2.set_xticklabels(share_pivot.index[::2], rotation=45, ha="right")
    style_axes(ax2, "重点品牌市场份额", ylabel="%")
    ax2.legend(frameon=False, ncol=3, fontsize=9)

    for brand, group in merged.groupby("brand"):
        sizes = group["cpu_score_multi"].fillna(2000) / 10
        ax3.scatter(
            group["screen_size_in"],
            group["weight_g"],
            s=sizes,
            c=BRAND_COLORS.get(brand, "#607D8B"),
            alpha=0.7,
            edgecolors="white",
            linewidths=0.8,
            label=brand,
        )
    style_axes(ax3, "屏幕尺寸-重量-性能", xlabel="英寸", ylabel="g")

    top_perf = top_perf.iloc[::-1]
    ax4.barh(
        np.arange(len(top_perf)),
        top_perf["cpu_score_multi"],
        color=top_perf["brand"].map(BRAND_COLORS).fillna("#607D8B"),
    )
    ax4.set_yticks(np.arange(len(top_perf)))
    ax4.set_yticklabels(top_perf["model"])
    style_axes(ax4, "代表型号多核性能 Top 10", xlabel="Geekbench 多核")

    fig.suptitle("2020-2025 年平板电脑市场与产品演进总览", fontsize=18, fontweight="bold", y=0.98)
    save_fig(fig, "00_tablet_dashboard_overview.png")


def main() -> None:
    models, perf, market = load_data()
    merged = merge_models_perf(models, perf)

    plot_market_total(market)
    plot_market_share_area(market)
    plot_market_share_lines(market)
    plot_size_weight_perf_scatter(merged)
    plot_perf_ranking(merged)
    plot_form_factor_trends(merged)
    plot_display_type_structure(models)
    build_dashboard(market, merged, models)

    print(f"Charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

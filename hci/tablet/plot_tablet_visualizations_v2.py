from __future__ import annotations

from pathlib import Path
import math
import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyArrowPatch
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler
import umap


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300

sns.set_theme(style="whitegrid")

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
}


def parse_dimensions(dimensions: str) -> tuple[float | None, float | None, float | None]:
    if not isinstance(dimensions, str):
        return None, None, None
    parts = [p.strip() for p in dimensions.split("x")]
    if len(parts) != 3:
        return None, None, None
    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except ValueError:
        return None, None, None


def quarter_key(period: str) -> tuple[int, int]:
    return int(period[:4]), int(period[-1])


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = pd.read_csv(DATA_DIR / "tablet_models_2020_2025.csv")
    perf = pd.read_csv(DATA_DIR / "tablet_perf_2020_2025.csv")
    market = pd.read_csv(DATA_DIR / "tablet_market_2020_2025.csv")

    dim_df = models["dimensions_mm"].apply(parse_dimensions).apply(pd.Series)
    dim_df.columns = ["height_mm", "width_mm", "thickness_mm"]
    models = pd.concat([models, dim_df], axis=1)
    merged = models.merge(perf, on="soc", how="left")
    return models, perf, market, merged


def build_feature_matrix(merged: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    df = merged.copy()
    df["feature_list"] = (
        df["feature_tags"]
        .fillna("")
        .apply(lambda x: [item.strip() for item in str(x).split(",") if item.strip()])
    )

    mlb = MultiLabelBinarizer()
    tag_matrix = pd.DataFrame(
        mlb.fit_transform(df["feature_list"]),
        columns=[f"tag_{c}" for c in mlb.classes_],
        index=df.index,
    )

    numeric_cols = [
        "release_year",
        "weight_g",
        "screen_size_in",
        "rear_camera_mp",
        "cpu_score_single",
        "cpu_score_multi",
        "thickness_mm",
    ]
    categorical_cols = ["display_type"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(sparse_output=False, handle_unknown="ignore"), categorical_cols),
        ]
    )

    base_matrix = preprocessor.fit_transform(df[numeric_cols + categorical_cols])
    full_matrix = np.hstack([base_matrix, tag_matrix.to_numpy(dtype=float)])
    return df, full_matrix


def compute_umap(df: pd.DataFrame, matrix: np.ndarray) -> pd.DataFrame:
    reducer = umap.UMAP(
        n_neighbors=7,
        min_dist=0.35,
        metric="euclidean",
        random_state=42,
    )
    coords = reducer.fit_transform(matrix)
    out = df.copy()
    out["umap_x"] = coords[:, 0]
    out["umap_y"] = coords[:, 1]
    return out


def add_premiumization_index(df: pd.DataFrame) -> pd.DataFrame:
    display_score_map = {
        "IPS": 0.0,
        "OLED": 0.75,
        "AMOLED": 1.0,
        "Dynamic AMOLED 2X": 1.0,
    }

    out = df.copy()
    out["display_score"] = out["display_type"].map(display_score_map).fillna(0.0)
    out["connectivity_score"] = (
        out["feature_tags"].fillna("").str.contains("Wi-Fi 6|Wi-Fi 7", regex=True).astype(int)
        + out["feature_tags"].fillna("").str.contains("USB-C", regex=False).astype(int)
        + out["feature_tags"].fillna("").str.contains("eSIM|5G", regex=True).astype(int)
    )
    out["thinness_score"] = -out["thickness_mm"]

    score_cols = [
        "cpu_score_multi",
        "display_score",
        "screen_size_in",
        "thinness_score",
        "connectivity_score",
    ]
    z = out[score_cols].apply(lambda s: (s - s.mean()) / s.std(ddof=0))
    out["premiumization_index"] = (
        0.35 * z["cpu_score_multi"]
        + 0.20 * z["display_score"]
        + 0.15 * z["screen_size_in"]
        + 0.15 * z["thinness_score"]
        + 0.15 * z["connectivity_score"]
    )
    return out


def compute_nearest_competitors(df: pd.DataFrame, matrix: np.ndarray) -> pd.DataFrame:
    nn = NearestNeighbors(n_neighbors=min(6, len(df)), metric="euclidean")
    nn.fit(matrix)
    distances, indices = nn.kneighbors(matrix)
    rows: list[dict] = []
    for i, (dist_row, idx_row) in enumerate(zip(distances, indices)):
        source_brand = df.iloc[i]["brand"]
        source_model = df.iloc[i]["model"]
        target_index = None
        target_distance = None
        for dist, idx in zip(dist_row[1:], idx_row[1:]):
            if df.iloc[idx]["brand"] != source_brand:
                target_index = idx
                target_distance = dist
                break
        if target_index is None:
            continue
        rows.append(
            {
                "source_brand": source_brand,
                "source_model": source_model,
                "target_brand": df.iloc[target_index]["brand"],
                "target_model": df.iloc[target_index]["model"],
                "distance": float(target_distance),
            }
        )
    return pd.DataFrame(rows)


def save_fig(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, bbox_inches="tight")
    plt.close(fig)


def plot_market_cycle_and_concentration(market: pd.DataFrame) -> None:
    total = market[market["brand"] == "Total"].copy().sort_values("market_period", key=lambda s: s.map(quarter_key))
    shares = market[~market["brand"].isin(["Total"])].copy()
    hhi = (
        shares.groupby("market_period", as_index=False)["market_share_pct"]
        .apply(lambda s: float(np.sum(np.square(s))))
        .rename(columns={"market_share_pct": "hhi"})
        .sort_values("market_period", key=lambda s: s.map(quarter_key))
    )

    fig, ax1 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(total))
    shipments_m = total["shipments_k"] / 1000

    ax1.plot(x, shipments_m, color="#263238", linewidth=2.8, marker="o")
    ax1.fill_between(x, shipments_m, color="#CFD8DC", alpha=0.3)
    ax1.set_ylabel("全球季度出货量（百万台）", color="#263238")
    ax1.tick_params(axis="y", labelcolor="#263238")
    ax1.set_xticks(x)
    ax1.set_xticklabels(total["market_period"], rotation=45, ha="right")
    ax1.set_title("图1  市场周期与集中度的双重演化", fontsize=15, fontweight="bold", pad=12)
    ax1.grid(axis="y", linestyle="--", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, hhi["hhi"], color="#C62828", linewidth=2.2, marker="s")
    ax2.set_ylabel("HHI 市场集中度指数", color="#C62828")
    ax2.tick_params(axis="y", labelcolor="#C62828")

    peak_idx = shipments_m.idxmax()
    low_idx = shipments_m.idxmin()
    ax1.annotate(
        f"疫情峰值\n{total.loc[peak_idx, 'market_period']}",
        xy=(total.index.get_loc(peak_idx), shipments_m.loc[peak_idx]),
        xytext=(2, shipments_m.loc[peak_idx] + 4),
        arrowprops={"arrowstyle": "->", "color": "#455A64"},
        fontsize=10,
    )
    ax1.annotate(
        f"调整低点\n{total.loc[low_idx, 'market_period']}",
        xy=(total.index.get_loc(low_idx), shipments_m.loc[low_idx]),
        xytext=(12, shipments_m.loc[low_idx] + 4),
        arrowprops={"arrowstyle": "->", "color": "#455A64"},
        fontsize=10,
    )
    save_fig(fig, "v2_01_market_cycle_hhi.png")


def plot_umap_embedding(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 8))
    for brand, group in df.groupby("brand"):
        ax.scatter(
            group["umap_x"],
            group["umap_y"],
            s=70 + (group["premiumization_index"] - group["premiumization_index"].min() + 0.2) * 55,
            c=BRAND_COLORS.get(brand, "#78909C"),
            alpha=0.82,
            edgecolors="white",
            linewidths=0.8,
            label=brand,
        )

    highlights = [
        "iPad Pro 11 (2024)",
        "Galaxy Tab S10 Ultra Wi-Fi",
        "MatePad Pro 13.2",
        "Pad 6S Pro 12.4",
        "Fire 7 (2022)",
    ]
    for _, row in df[df["model"].isin(highlights)].iterrows():
        ax.annotate(
            row["model"],
            xy=(row["umap_x"], row["umap_y"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
        )

    ax.set_title("图2  基于多维规格与性能特征的 UMAP 低维嵌入", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("UMAP 维度 1")
    ax.set_ylabel("UMAP 维度 2")
    ax.legend(frameon=False, ncol=4, fontsize=9, loc="upper right")
    ax.grid(alpha=0.2, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save_fig(fig, "v2_02_umap_embedding.png")


def plot_nearest_neighbor_map(df: pd.DataFrame, neighbors: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(df["umap_x"], df["umap_y"], s=45, c=df["brand"].map(BRAND_COLORS), alpha=0.55)

    strongest = neighbors.sort_values("distance").groupby("source_brand").head(2)
    seen_pairs = set()
    for _, row in strongest.iterrows():
        source = df[(df["brand"] == row["source_brand"]) & (df["model"] == row["source_model"])].iloc[0]
        target = df[(df["brand"] == row["target_brand"]) & (df["model"] == row["target_model"])].iloc[0]
        pair = tuple(sorted([f"{row['source_brand']}|{row['source_model']}", f"{row['target_brand']}|{row['target_model']}"]))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        arrow = FancyArrowPatch(
            (source["umap_x"], source["umap_y"]),
            (target["umap_x"], target["umap_y"]),
            arrowstyle="-",
            linewidth=1.4,
            color="#546E7A",
            alpha=0.75,
        )
        ax.add_patch(arrow)
        mid_x = (source["umap_x"] + target["umap_x"]) / 2
        mid_y = (source["umap_y"] + target["umap_y"]) / 2
        ax.text(mid_x, mid_y, f"{row['source_brand']} ↔ {row['target_brand']}", fontsize=8, color="#37474F")

    for _, row in df[df["brand"].isin(["Apple", "Samsung", "Huawei", "Xiaomi"])].groupby("brand").head(2).iterrows():
        ax.annotate(row["model"], (row["umap_x"], row["umap_y"]), xytext=(4, 5), textcoords="offset points", fontsize=8)

    ax.set_title("图3  跨品牌最近邻竞品匹配图", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("UMAP 维度 1")
    ax.set_ylabel("UMAP 维度 2")
    ax.grid(alpha=0.2, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save_fig(fig, "v2_03_nearest_neighbor_map.png")


def plot_premiumization_index(df: pd.DataFrame) -> None:
    yearly = (
        df.groupby(["brand", "release_year"], as_index=False)["premiumization_index"]
        .mean()
        .sort_values(["brand", "release_year"])
    )
    major = yearly[yearly["brand"].isin(["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi", "Oppo", "Honor"])]

    fig, ax = plt.subplots(figsize=(12, 6))
    for brand, group in major.groupby("brand"):
        ax.plot(
            group["release_year"],
            group["premiumization_index"],
            marker="o",
            linewidth=2.3,
            color=BRAND_COLORS.get(brand, "#78909C"),
            label=brand,
        )
    ax.axhline(0, color="#90A4AE", linewidth=1, linestyle="--")
    ax.set_title("图4  品牌高端化指数轨迹", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("发布年份")
    ax.set_ylabel("Premiumization Index（标准化复合指标）")
    ax.legend(frameon=False, ncol=4, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save_fig(fig, "v2_04_premiumization_index.png")


def plot_market_share_vs_premiumization(market: pd.DataFrame, df: pd.DataFrame) -> None:
    latest_market = market[(market["market_period"] == "2025Q2") & (~market["brand"].isin(["Others", "Total"]))].copy()
    annual_premium = df.groupby("brand", as_index=False)["premiumization_index"].mean()
    chart = latest_market.merge(annual_premium, on="brand", how="left")

    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(
        chart["premiumization_index"],
        chart["market_share_pct"],
        s=chart["shipments_k"] / 18,
        c=chart["brand"].map(BRAND_COLORS),
        alpha=0.82,
        edgecolors="white",
        linewidths=0.9,
    )
    for _, row in chart.iterrows():
        ax.annotate(row["brand"], (row["premiumization_index"], row["market_share_pct"]), xytext=(6, 6), textcoords="offset points", fontsize=10)

    ax.set_title("图5  高端化程度与市场份额的关系（2025Q2）", fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel("品牌平均高端化指数")
    ax.set_ylabel("2025Q2 市场份额（%）")
    ax.grid(alpha=0.25, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save_fig(fig, "v2_05_premiumization_vs_share.png")


def main() -> None:
    models, perf, market, merged = load_data()
    feature_df, feature_matrix = build_feature_matrix(merged)
    embedded = compute_umap(feature_df, feature_matrix)
    embedded = add_premiumization_index(embedded)
    neighbors = compute_nearest_competitors(embedded, feature_matrix)

    plot_market_cycle_and_concentration(market)
    plot_umap_embedding(embedded)
    plot_nearest_neighbor_map(embedded, neighbors)
    plot_premiumization_index(embedded)
    plot_market_share_vs_premiumization(market, embedded)

    neighbor_export = neighbors.sort_values(["source_brand", "distance"])
    neighbor_export.to_csv(DATA_DIR / "tablet_nearest_neighbors_v2.csv", index=False)
    embedded[
        [
            "brand",
            "model",
            "release_year",
            "screen_size_in",
            "weight_g",
            "thickness_mm",
            "display_type",
            "rear_camera_mp",
            "soc",
            "cpu_score_single",
            "cpu_score_multi",
            "premiumization_index",
            "umap_x",
            "umap_y",
        ]
    ].to_csv(DATA_DIR / "tablet_feature_space_v2.csv", index=False)

    print(f"Second-version charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler
import umap


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "visualizations"
OUT_DIR.mkdir(exist_ok=True)


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

FONT = "Microsoft YaHei"

pio.templates.default = "plotly_white"


def save_figure(fig: go.Figure, filename: str, width: int = 1400, height: int = 900) -> None:
    path = OUT_DIR / filename
    fig.write_image(str(path), width=width, height=height, scale=2)


def parse_thickness(dimensions: str) -> float | None:
    try:
        return float(str(dimensions).split("x")[2].strip())
    except Exception:
        return None


def quarter_key(period: str) -> tuple[int, int]:
    return int(period[:4]), int(period[-1])


def load_data():
    models = pd.read_csv(DATA_DIR / "tablet_models_2020_2025.csv")
    perf = pd.read_csv(DATA_DIR / "tablet_perf_2020_2025.csv")
    market = pd.read_csv(DATA_DIR / "tablet_market_2020_2025.csv")

    merged = models.merge(perf, on="soc", how="left")
    merged["thickness_mm"] = merged["dimensions_mm"].apply(parse_thickness)
    return models, perf, market, merged


def add_feature_engineering(merged: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    df = merged.copy()
    df["feature_list"] = (
        df["feature_tags"].fillna("").apply(lambda s: [x.strip() for x in str(s).split(",") if x.strip()])
    )

    mlb = MultiLabelBinarizer()
    tag_matrix = mlb.fit_transform(df["feature_list"])

    numeric_cols = [
        "release_year",
        "screen_size_in",
        "weight_g",
        "thickness_mm",
        "rear_camera_mp",
        "cpu_score_single",
        "cpu_score_multi",
    ]
    categorical_cols = ["display_type"]

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(sparse_output=False, handle_unknown="ignore"), categorical_cols),
        ]
    )
    matrix = pre.fit_transform(df[numeric_cols + categorical_cols])
    matrix = np.hstack([matrix, tag_matrix])

    reducer = umap.UMAP(n_neighbors=7, min_dist=0.3, metric="euclidean", random_state=42)
    coords = reducer.fit_transform(matrix)
    df["umap_x"] = coords[:, 0]
    df["umap_y"] = coords[:, 1]

    display_score = {
        "IPS": 0.0,
        "OLED": 0.8,
        "AMOLED": 1.0,
        "Dynamic AMOLED 2X": 1.0,
    }
    df["display_score"] = df["display_type"].map(display_score).fillna(0)
    df["connectivity_score"] = (
        df["feature_tags"].fillna("").str.contains("Wi-Fi 6|Wi-Fi 7", regex=True).astype(int)
        + df["feature_tags"].fillna("").str.contains("USB-C", regex=False).astype(int)
        + df["feature_tags"].fillna("").str.contains("eSIM|5G", regex=True).astype(int)
    )
    z = pd.DataFrame({
        "perf": (df["cpu_score_multi"] - df["cpu_score_multi"].mean()) / df["cpu_score_multi"].std(ddof=0),
        "display": (df["display_score"] - df["display_score"].mean()) / df["display_score"].std(ddof=0),
        "screen": (df["screen_size_in"] - df["screen_size_in"].mean()) / df["screen_size_in"].std(ddof=0),
        "thin": ((-df["thickness_mm"]) - (-df["thickness_mm"]).mean()) / (-df["thickness_mm"]).std(ddof=0),
        "conn": (df["connectivity_score"] - df["connectivity_score"].mean()) / df["connectivity_score"].std(ddof=0),
    })
    df["premiumization_index"] = 0.35 * z["perf"] + 0.20 * z["display"] + 0.15 * z["screen"] + 0.15 * z["thin"] + 0.15 * z["conn"]
    return df, matrix


def compute_neighbors(df: pd.DataFrame, matrix: np.ndarray) -> pd.DataFrame:
    nn = NearestNeighbors(n_neighbors=min(6, len(df)), metric="euclidean")
    nn.fit(matrix)
    distances, indices = nn.kneighbors(matrix)
    rows = []
    for i, (dist_row, idx_row) in enumerate(zip(distances, indices)):
        src_brand = df.iloc[i]["brand"]
        for dist, idx in zip(dist_row[1:], idx_row[1:]):
            if df.iloc[idx]["brand"] != src_brand:
                rows.append({
                    "source_brand": src_brand,
                    "source_model": df.iloc[i]["model"],
                    "target_brand": df.iloc[idx]["brand"],
                    "target_model": df.iloc[idx]["model"],
                    "distance": float(dist),
                })
                break
    return pd.DataFrame(rows)


def fig_market_cycle_hhi(market: pd.DataFrame) -> go.Figure:
    total = market[market["brand"] == "Total"].copy().sort_values("market_period", key=lambda s: s.map(quarter_key))
    shares = market[market["brand"] != "Total"].copy()
    hhi = (
        shares.groupby("market_period", as_index=False)["market_share_pct"]
        .apply(lambda s: float(np.sum(np.square(s))))
        .rename(columns={"market_share_pct": "hhi"})
        .sort_values("market_period", key=lambda s: s.map(quarter_key))
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=total["market_period"],
            y=total["shipments_k"] / 1000,
            mode="lines+markers",
            name="全球出货量",
            line=dict(color="#263238", width=4),
            marker=dict(size=8),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=hhi["market_period"],
            y=hhi["hhi"],
            mode="lines+markers",
            name="HHI集中度",
            line=dict(color="#C62828", width=3),
            marker=dict(size=7, symbol="diamond"),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="市场周期与集中度的双重演化",
        font=dict(family=FONT, size=18),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=70, r=70, t=90, b=80),
    )
    fig.update_xaxes(title_text="季度")
    fig.update_yaxes(title_text="全球季度出货量（百万台）", secondary_y=False)
    fig.update_yaxes(title_text="HHI 市场集中度指数", secondary_y=True)
    return fig


def fig_umap(df: pd.DataFrame) -> go.Figure:
    chart = df.copy()
    chart["bubble_size"] = chart["premiumization_index"] - chart["premiumization_index"].min() + 0.3
    fig = px.scatter(
        chart,
        x="umap_x",
        y="umap_y",
        color="brand",
        color_discrete_map=BRAND_COLORS,
        size="bubble_size",
        size_max=32,
        hover_data=["model", "display_type", "screen_size_in", "cpu_score_multi"],
        text="model",
    )
    fig.update_traces(
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(line=dict(color="white", width=1), opacity=0.82),
    )
    fig.update_layout(
        title="平板设备多维特征的 UMAP 嵌入空间",
        font=dict(family=FONT, size=18),
        margin=dict(l=60, r=40, t=90, b=60),
        legend_title_text="品牌",
    )
    return fig


def fig_neighbor_network(df: pd.DataFrame, neighbors: pd.DataFrame) -> go.Figure:
    top_links = neighbors.sort_values("distance").groupby("source_brand").head(2)
    fig = go.Figure()

    for _, row in top_links.iterrows():
        src = df[(df["brand"] == row["source_brand"]) & (df["model"] == row["source_model"])].iloc[0]
        tgt = df[(df["brand"] == row["target_brand"]) & (df["model"] == row["target_model"])].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[src["umap_x"], tgt["umap_x"]],
                y=[src["umap_y"], tgt["umap_y"]],
                mode="lines",
                line=dict(color="rgba(84,110,122,0.45)", width=2),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["umap_x"],
            y=df["umap_y"],
            mode="markers+text",
            text=df["brand"],
            textposition="top center",
            marker=dict(
                size=14,
                color=[BRAND_COLORS.get(b, "#78909C") for b in df["brand"]],
                line=dict(color="white", width=1.2),
                opacity=0.82,
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
            customdata=np.stack([df["brand"], df["model"]], axis=1),
            showlegend=False,
        )
    )

    fig.update_layout(
        title="跨品牌最近邻竞品关系图",
        font=dict(family=FONT, size=18),
        margin=dict(l=60, r=40, t=90, b=60),
        xaxis_title="UMAP 维度 1",
        yaxis_title="UMAP 维度 2",
    )
    return fig


def fig_premium_traj(df: pd.DataFrame) -> go.Figure:
    yearly = df.groupby(["brand", "release_year"], as_index=False)["premiumization_index"].mean()
    major = yearly[yearly["brand"].isin(["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi", "Oppo", "Honor"])]
    fig = px.line(
        major,
        x="release_year",
        y="premiumization_index",
        color="brand",
        color_discrete_map=BRAND_COLORS,
        markers=True,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=9))
    fig.update_layout(
        title="品牌高端化轨迹",
        font=dict(family=FONT, size=18),
        margin=dict(l=60, r=40, t=90, b=60),
        xaxis_title="发布年份",
        yaxis_title="Premiumization Index",
    )
    return fig


def fig_share_vs_premium(market: pd.DataFrame, df: pd.DataFrame) -> go.Figure:
    latest_market = market[(market["market_period"] == "2025Q2") & (~market["brand"].isin(["Others", "Total"]))].copy()
    brand_stats = df.groupby("brand", as_index=False)["premiumization_index"].mean()
    chart = latest_market.merge(brand_stats, on="brand", how="left")
    fig = px.scatter(
        chart,
        x="premiumization_index",
        y="market_share_pct",
        size="shipments_k",
        color="brand",
        color_discrete_map=BRAND_COLORS,
        text="brand",
        hover_data=["shipments_k"],
        size_max=60,
    )
    fig.update_traces(textposition="top center", marker=dict(line=dict(color="white", width=1.2), opacity=0.85))
    fig.update_layout(
        title="高端化程度与市场份额的关系",
        font=dict(family=FONT, size=18),
        margin=dict(l=60, r=40, t=90, b=60),
        xaxis_title="品牌平均高端化指数",
        yaxis_title="2025Q2 市场份额（%）",
        showlegend=False,
    )
    return fig


def fig_brand_profile_radar(df: pd.DataFrame) -> go.Figure:
    radar = df[df["brand"].isin(["Apple", "Samsung", "Huawei", "Xiaomi", "Lenovo"])].copy()
    summary = radar.groupby("brand", as_index=False).agg(
        screen=("screen_size_in", "mean"),
        thinness=("thickness_mm", lambda s: -s.mean()),
        performance=("cpu_score_multi", "mean"),
        camera=("rear_camera_mp", "mean"),
        premium=("premiumization_index", "mean"),
    )
    for col in ["screen", "thinness", "performance", "camera", "premium"]:
        summary[col] = (summary[col] - summary[col].min()) / (summary[col].max() - summary[col].min() + 1e-9)

    categories = ["screen", "thinness", "performance", "camera", "premium"]
    labels = {
        "screen": "屏幕尺度",
        "thinness": "轻薄程度",
        "performance": "性能强度",
        "camera": "影像配置",
        "premium": "高端化程度",
    }
    fig = go.Figure()
    for _, row in summary.iterrows():
        vals = [row[c] for c in categories]
        vals.append(vals[0])
        theta = [labels[c] for c in categories] + [labels[categories[0]]]
        fig.add_trace(
            go.Scatterpolar(
                r=vals,
                theta=theta,
                fill="toself",
                name=row["brand"],
                line=dict(color=BRAND_COLORS.get(row["brand"], "#78909C"), width=3),
                opacity=0.4,
            )
        )
    fig.update_layout(
        title="主要品牌产品画像雷达图",
        font=dict(family=FONT, size=18),
        margin=dict(l=60, r=60, t=90, b=40),
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    )
    return fig


def main():
    models, perf, market, merged = load_data()
    feature_df, matrix = add_feature_engineering(merged)
    neighbors = compute_neighbors(feature_df, matrix)

    feature_df[
        [
            "brand", "model", "release_year", "screen_size_in", "weight_g", "thickness_mm",
            "display_type", "rear_camera_mp", "soc", "cpu_score_single", "cpu_score_multi",
            "premiumization_index", "umap_x", "umap_y"
        ]
    ].to_csv(DATA_DIR / "tablet_feature_space_final.csv", index=False)
    neighbors.to_csv(DATA_DIR / "tablet_nearest_neighbors_final.csv", index=False)

    figs = [
        (fig_market_cycle_hhi(market), "final_01_market_cycle_hhi.png"),
        (fig_umap(feature_df), "final_02_umap_feature_space.png"),
        (fig_neighbor_network(feature_df, neighbors), "final_03_neighbor_network.png"),
        (fig_premium_traj(feature_df), "final_04_premiumization_trajectory.png"),
        (fig_share_vs_premium(market, feature_df), "final_05_share_vs_premium.png"),
        (fig_brand_profile_radar(feature_df), "final_06_brand_profile_radar.png"),
    ]
    for fig, name in figs:
        save_figure(fig, name)

    print(f"Final visualization suite saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()

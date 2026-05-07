from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "tablet_market_2020_2025.csv"
OUTPUT_DIR = ROOT / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "tablet_market_shipments_race.gif"


plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


BRAND_COLORS = {
    "Apple": "#111111",
    "Samsung": "#1565C0",
    "Huawei": "#C62828",
    "Lenovo": "#6A1B9A",
    "Xiaomi": "#EF6C00",
    "Amazon": "#00838F",
}


def quarter_key(period: str) -> tuple[int, int]:
    year = int(period[:4])
    quarter = int(period[-1])
    return year, quarter


def load_market_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[~df["brand"].isin(["Others", "Total"])].copy()

    # Keep the six brand series that actually form the market race.
    brands = ["Apple", "Samsung", "Huawei", "Lenovo", "Xiaomi", "Amazon"]
    periods = sorted(df["market_period"].unique(), key=quarter_key)

    pivot = (
        df[df["brand"].isin(brands)]
        .pivot(index="market_period", columns="brand", values="shipments_k")
        .reindex(periods)
    )

    # Brands like Xiaomi appear later; keep earlier quarters at zero for animation continuity.
    pivot = pivot.fillna(0)
    return pivot


def interpolate_frames(pivot: pd.DataFrame, frames_per_step: int = 14) -> tuple[list[str], np.ndarray]:
    periods = pivot.index.tolist()
    values = pivot.to_numpy(dtype=float)

    frame_labels: list[str] = []
    all_frames: list[np.ndarray] = []

    for i in range(len(periods) - 1):
        start = values[i]
        end = values[i + 1]
        for t in range(frames_per_step):
            alpha = t / frames_per_step
            all_frames.append(start * (1 - alpha) + end * alpha)
            frame_labels.append(periods[i])

    all_frames.append(values[-1])
    frame_labels.append(periods[-1])
    return frame_labels, np.vstack(all_frames)


def render_race() -> Path:
    pivot = load_market_data()
    brands = pivot.columns.tolist()
    frame_labels, frames = interpolate_frames(pivot)

    fig, ax = plt.subplots(figsize=(12, 7))
    max_value = frames.max() * 1.12

    def draw_frame(frame_index: int) -> None:
        ax.clear()
        values = frames[frame_index]
        order = np.argsort(values)
        ranked_brands = [brands[i] for i in order]
        ranked_values = values[order]
        colors = [BRAND_COLORS.get(b, "#78909C") for b in ranked_brands]

        ax.barh(ranked_brands, ranked_values, color=colors, alpha=0.92)

        for y, (brand, value) in enumerate(zip(ranked_brands, ranked_values)):
            ax.text(value + max_value * 0.01, y, f"{value / 1000:.2f}M", va="center", fontsize=11)

        ax.set_xlim(0, max_value)
        ax.set_xlabel("季度出货量（百万台）", fontsize=12)
        ax.set_title("2020-2025 全球平板品牌季度出货量动态排名赛跑图", fontsize=18, fontweight="bold", pad=16)
        ax.text(
            0.98,
            0.10,
            frame_labels[frame_index],
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=28,
            color="#263238",
            fontweight="bold",
        )
        ax.text(
            0.98,
            0.04,
            "Source: Canalys Newsroom",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="#607D8B",
        )
        ax.grid(axis="x", linestyle="--", alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", labelsize=11)
        ax.tick_params(axis="x", labelsize=10)

    animation = FuncAnimation(fig, draw_frame, frames=len(frames), interval=120, repeat=True)
    animation.save(OUTPUT_PATH, writer=PillowWriter(fps=10))
    plt.close(fig)
    return OUTPUT_PATH


if __name__ == "__main__":
    output = render_race()
    print(f"Saved animation to: {output}")

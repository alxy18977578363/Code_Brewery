from pathlib import Path

import numpy as np
import pandas as pd

from script.data_loader import load_datasets
from script.data_processor import preprocess_dataframe


class OverviewService:
    """Overview page business logic."""

    DATASET_DIR = Path(__file__).resolve().parents[2] / "dataset"
    BIN_WIDTH = 0.3

    @classmethod
    def _load_processed_dataset(cls):
        """Load and preprocess dataset by reusing the script package."""
        raw_df, _ = load_datasets(data_dir=cls.DATASET_DIR, verbose=False)
        return preprocess_dataframe(raw_df)

    @classmethod
    def _compute_histograms(cls, df: pd.DataFrame, group_col: str) -> dict:
        rating_min = float(df["rating"].min())
        rating_max = float(df["rating"].max())
        bins = np.arange(
            np.floor(rating_min / cls.BIN_WIDTH) * cls.BIN_WIDTH,
            rating_max + cls.BIN_WIDTH + 0.001,
            cls.BIN_WIDTH,
        )
        bin_labels = [f"{b:.1f}-{b + cls.BIN_WIDTH:.1f}" for b in bins[:-1]]
        order = df[group_col].value_counts().index.tolist()

        groups = {}
        for group_name, group_df in df.groupby(group_col):
            counts, _ = np.histogram(group_df["rating"].dropna(), bins=bins)
            groups[group_name] = counts.tolist()

        return {
            "bin_labels": bin_labels,
            "group_order": order,
            "groups": groups,
        }

    @classmethod
    def get_overview_payload(cls) -> list[dict]:
        dataframe = cls._load_processed_dataset().copy()
        return dataframe.to_dict(orient="records")

    @classmethod
    def get_segment_histograms(cls) -> dict:
        df = cls._load_processed_dataset().copy()
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df["market_segment"] = df["market_segment"].fillna("Unknown")
        df = df.dropna(subset=["rating"])
        return cls._compute_histograms(df, "market_segment")

    @classmethod
    def get_area_histograms(cls) -> dict:
        df = cls._load_processed_dataset().copy()
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df["area"] = df["area"].fillna("Unknown")
        df = df.dropna(subset=["rating"])
        return cls._compute_histograms(df, "area")
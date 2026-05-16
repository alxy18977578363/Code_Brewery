import re

import numpy as np
import pandas as pd

from app.services.overview_service import OverviewService

LOCAL_DISH_PATTERN = r"filter coffee|pongal|dosa|idli|vada|sambar|rasam|curd rice|biryani"


class MarketSegmentRatingService:
    """Market segment vs rating analysis service."""

    @classmethod
    def _load_dataframe(cls) -> pd.DataFrame:
        dataframe = pd.DataFrame(OverviewService.get_overview_payload()).copy()
        dataframe["rating"] = pd.to_numeric(dataframe["rating"], errors="coerce")
        dataframe["market_segment"] = dataframe["market_segment"].fillna("Unknown").astype(str)
        dataframe["features"] = dataframe["features"].fillna("").astype(str)
        return dataframe.dropna(subset=["rating"]).reset_index(drop=True)

    @classmethod
    def _explode_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in df.iterrows():
            tokens = [t.strip() for t in row["features"].split(",") if t.strip()]
            for token in tokens:
                rows.append({
                    "market_segment": row["market_segment"],
                    "rating": row["rating"],
                    "feature": token,
                })
        return pd.DataFrame(rows)

    @classmethod
    def _explode_tokens(cls, df: pd.DataFrame, col: str, token_name: str) -> pd.DataFrame:
        rows = []
        for _, row in df.iterrows():
            tokens = [t.strip() for t in str(row[col]).split(",") if t.strip()]
            for token in tokens:
                rows.append({
                    "market_segment": row["market_segment"],
                    "rating": row["rating"],
                    token_name: token,
                })
        return pd.DataFrame(rows)

    @classmethod
    def get_payload(cls) -> dict:
        df = cls._load_dataframe()

        # --- 1. Ridgeline data (rating distribution per segment) ---
        rating_min = max(0, df["rating"].min() - 0.05)
        bins = np.linspace(rating_min, 5.0, 48)
        centers = ((bins[:-1] + bins[1:]) / 2).tolist()
        kernel = np.array([1, 2, 3, 4, 3, 2, 1], dtype=float)
        kernel /= kernel.sum()

        ridgeline_records = []
        for seg, vals in df.groupby("market_segment")["rating"]:
            hist, _ = np.histogram(vals, bins=bins, density=True)
            smooth = np.convolve(hist, kernel, mode="same")
            if smooth.max() > 0:
                smooth = smooth / smooth.max() * 0.72
            ridgeline_records.append({
                "segment": seg,
                "count": int(len(vals)),
                "median": float(vals.median()),
                "densities": smooth.tolist(),
            })

        # --- 2. Grouped bar data (rating band counts per segment) ---
        rating_band_order = ["fragile", "developing", "solid", "strong", "elite"]
        band_bins = [-np.inf, 2.9, 3.4, 3.8, 4.2, np.inf]
        df["rating_band"] = pd.cut(df["rating"], bins=band_bins, labels=rating_band_order)

        grouped = (
            df.groupby(["market_segment", "rating_band"], observed=False)
            .size()
            .reset_index(name="count")
        )
        grouped["rating_band"] = pd.Categorical(grouped["rating_band"], categories=rating_band_order, ordered=True)
        grouped = grouped.sort_values(["market_segment", "rating_band"])

        segment_order = df["market_segment"].value_counts().index.tolist()

        grouped_records = []
        for _, row in grouped.iterrows():
            grouped_records.append({
                "segment": row["market_segment"],
                "band": row["rating_band"],
                "count": int(row["count"]),
            })

        # --- 3. Heatmap data (feature adoption % per segment) ---
        feature_long = cls._explode_features(df)
        top_features = feature_long["feature"].value_counts().head(16).index.tolist()
        segment_counts = df["market_segment"].value_counts()

        feature_matrix = pd.crosstab(feature_long["market_segment"], feature_long["feature"])
        feature_share = feature_matrix.reindex(segment_order)[top_features].div(segment_counts, axis=0).fillna(0)

        heatmap_records = []
        for seg in feature_share.index:
            for feat in feature_share.columns:
                val = feature_share.loc[seg, feat]
                heatmap_records.append({
                    "segment": seg,
                    "feature": feat,
                    "share": round(float(val), 4),
                })

        # --- 4. Cuisine top 18 ---
        cuisine_long = cls._explode_tokens(df, "cuisine", "cuisine")
        cuisine_stats = (
            cuisine_long.groupby("cuisine")
            .agg(outlets=("cuisine", "size"), avg_rating=("rating", "mean"))
            .query("outlets >= 18")
            .sort_values("outlets", ascending=False)
            .head(18)
            .sort_values("outlets")
        )
        cuisine_records = []
        for name, row in cuisine_stats.iterrows():
            is_local = bool(re.search(LOCAL_DISH_PATTERN, name, re.IGNORECASE))
            cuisine_records.append({
                "cuisine": name,
                "outlets": int(row["outlets"]),
                "avg_rating": round(float(row["avg_rating"]), 4),
                "is_local": is_local,
            })

        # --- 5. Dish top 20 ---
        dish_long = cls._explode_tokens(df, "top_dishes", "dish")
        dish_stats = (
            dish_long.groupby("dish")
            .agg(outlets=("dish", "size"), avg_rating=("rating", "mean"))
            .query("outlets >= 20")
            .sort_values("outlets", ascending=False)
            .head(20)
            .sort_values("outlets")
        )
        dish_records = []
        for name, row in dish_stats.iterrows():
            is_local = bool(re.search(LOCAL_DISH_PATTERN, name, re.IGNORECASE))
            dish_records.append({
                "dish": name,
                "outlets": int(row["outlets"]),
                "avg_rating": round(float(row["avg_rating"]), 4),
                "is_local": is_local,
            })

        return {
            "meta": {
                "total": len(df),
                "segments": segment_order,
                "segment_counts": {s: int(segment_counts[s]) for s in segment_order},
            },
            "ridgeline": {
                "centers": centers,
                "records": ridgeline_records,
            },
            "grouped_bar": {
                "segments": segment_order,
                "bands": rating_band_order,
                "records": grouped_records,
            },
            "heatmap": {
                "segments": feature_share.index.tolist(),
                "features": top_features,
                "records": heatmap_records,
            },
            "cuisine_top": cuisine_records,
            "dish_top": dish_records,
        }

import pandas as pd

from app.services.overview_service import OverviewService


class SpatialService:
    """Area-level analytics for stacked bars and choropleth-style maps."""

    TOP_AREA_COUNT = 24

    @classmethod
    def _load_dataframe(cls) -> pd.DataFrame:
        dataframe = pd.DataFrame(OverviewService.get_overview_payload()).copy()
        dataframe["rating"] = pd.to_numeric(dataframe["rating"], errors="coerce")
        dataframe["latitude"] = pd.to_numeric(dataframe["latitude"], errors="coerce")
        dataframe["longitude"] = pd.to_numeric(dataframe["longitude"], errors="coerce")
        dataframe["area"] = dataframe["area"].fillna("Unknown").astype(str).str.strip()
        dataframe["rating_band"] = dataframe["rating_band"].fillna("unknown").astype(str)
        return dataframe.dropna(subset=["rating", "latitude", "longitude"]).reset_index(drop=True)

    @classmethod
    def get_area_dashboard_payload(cls) -> dict:
        dataframe = cls._load_dataframe()

        rating_band_order = ["fragile", "developing", "solid", "strong", "elite"]
        area_summary = (
            dataframe.groupby("area", as_index=False)
            .agg(
                restaurant_count=("restaurant_id", "count"),
                average_rating=("rating", "mean"),
                latitude=("latitude", "mean"),
                longitude=("longitude", "mean"),
            )
            .sort_values(["restaurant_count", "average_rating"], ascending=[False, False])
            .reset_index(drop=True)
        )

        stacked = (
            dataframe.groupby(["area", "rating_band"], as_index=False)
            .agg(restaurant_count=("restaurant_id", "count"))
        )

        stacked["rating_band"] = pd.Categorical(
            stacked["rating_band"],
            categories=rating_band_order,
            ordered=True,
        )
        stacked = stacked.sort_values(["area", "rating_band"]).reset_index(drop=True)

        top_areas = area_summary.head(cls.TOP_AREA_COUNT)["area"].tolist()
        stacked_top = stacked[stacked["area"].isin(top_areas)].copy()
        violin_records = (
            dataframe[dataframe["area"].isin(top_areas)][["area", "rating", "rating_band", "restaurant_id"]]
            .sort_values(["area", "rating"])
            .reset_index(drop=True)
        )
        area_summary_top = area_summary[area_summary["area"].isin(top_areas)].copy()

        all_area_summary = area_summary.copy()
        return {
            "meta": {
                "total_restaurants": int(len(dataframe)),
                "total_areas": int(area_summary["area"].nunique()),
                "top_area_count": len(top_areas),
            },
            "area_summary": area_summary.assign(
                average_rating=area_summary["average_rating"].round(4)
            ).to_dict(orient="records"),
            "area_summary_top": area_summary_top.assign(
                average_rating=area_summary_top["average_rating"].round(4)
            ).to_dict(orient="records"),
            "rating_band_stack": stacked_top.to_dict(orient="records"),
            "violin_records": violin_records.to_dict(orient="records"),
            "rating_band_order": rating_band_order,
            "quadrant": cls._build_quadrant_payload(all_area_summary),
        }

    @classmethod
    def _build_quadrant_payload(cls, area_summary: pd.DataFrame) -> dict:
        median_count = float(area_summary["restaurant_count"].median())
        median_rating = float(area_summary["average_rating"].median())

        def _quadrant(row):
            high_count = row["restaurant_count"] >= median_count
            high_rating = row["average_rating"] >= median_rating
            if high_count and high_rating:
                return "High Supply / High Rating"
            if not high_count and high_rating:
                return "Low Supply / High Rating"
            if high_count and not high_rating:
                return "High Supply / Low Rating"
            return "Low Supply / Low Rating"

        df = area_summary.copy()
        df["quadrant"] = df.apply(_quadrant, axis=1)

        quadrant_labels = {
            "High Supply / High Rating": "Mature & Quality",
            "Low Supply / High Rating": "Hidden Gem / Potential",
            "High Supply / Low Rating": "Competitive & Volatile",
            "Low Supply / Low Rating": "Underdeveloped",
        }

        records = []
        for _, row in df.iterrows():
            records.append({
                "area": row["area"],
                "restaurant_count": int(row["restaurant_count"]),
                "average_rating": round(float(row["average_rating"]), 4),
                "quadrant": quadrant_labels[row["quadrant"]],
            })

        return {
            "median_count": round(median_count, 2),
            "median_rating": round(median_rating, 4),
            "records": records,
        }

    @classmethod
    def get_spatial_analysis_payload(cls) -> dict:
        return cls.get_area_dashboard_payload()

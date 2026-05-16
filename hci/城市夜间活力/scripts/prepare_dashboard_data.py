"""
Prepare aggregated data for the night economy dashboard.
Output: dashboard/data.js
"""

import json
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/synthetic/shanghai_night_orders.csv")
OUT_PATH = Path("dashboard/data.js")

HOUR_ORDER = [18, 19, 20, 21, 22, 23, 0, 1, 2]
WEEKEND_DOW = {4, 5, 6}  # Fri, Sat, Sun


def to_js(obj) -> str:
    payload = json.dumps(obj, ensure_ascii=False)
    return f"window.DASHBOARD_DATA = {payload};\n"


def main() -> None:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", parse_dates=["order_time"])
    df["order_amount"] = df["order_amount"].astype(float)
    df["rating"] = df["rating"].astype(float)
    df["hour"] = df["order_time"].dt.hour
    df["is_weekend"] = df["order_time"].dt.dayofweek.isin(WEEKEND_DOW)

    kpi = {
        "totalOrders": int(len(df)),
        "totalRevenue": float(df["order_amount"].sum()),
        "avgOrder": float(df["order_amount"].mean()),
        "avgRating": float(df["rating"].mean()),
    }

    # Top districts by revenue
    district_revenue = (
        df.groupby("district")["order_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
    )
    district_revenue_list = [
        {"name": name, "value": float(val)}
        for name, val in district_revenue.items()
    ]

    # Hourly avg order amount: weekday vs weekend
    hourly = (
        df.groupby(["hour", "is_weekend"])["order_amount"]
        .mean()
        .unstack(fill_value=0.0)
        .reindex(HOUR_ORDER)
    )
    weekday_series = [float(x) for x in hourly.get(False, pd.Series()).fillna(0.0)]
    weekend_series = [float(x) for x in hourly.get(True, pd.Series()).fillna(0.0)]

    # Category share
    category_share = (
        df.groupby("category_lv1")["order_amount"].sum().sort_values(ascending=False)
    )
    category_share_list = [
        {"name": name, "value": float(val)}
        for name, val in category_share.items()
    ]

    # Hourly stacked revenue by category
    category_hourly = (
        df.groupby(["hour", "category_lv1"])["order_amount"]
        .sum()
        .unstack(fill_value=0.0)
        .reindex(HOUR_ORDER)
    )
    category_series = {
        cat: [float(v) for v in category_hourly[cat].tolist()]
        for cat in category_hourly.columns
    }

    # Scatter sample: amount vs rating by category
    sample_size = min(900, len(df))
    scatter_df = df.sample(n=sample_size, random_state=7)
    scatter_points = [
        {
            "amount": float(row.order_amount),
            "rating": float(row.rating),
            "category": row.category_lv1,
        }
        for row in scatter_df.itertuples(index=False)
    ]

    # Map heat: aggregate by POI and keep top points
    poi_agg = (
        df.groupby(["poi_id", "poi_name", "lng", "lat"])["order_amount"]
        .sum()
        .reset_index()
        .sort_values("order_amount", ascending=False)
        .head(200)
    )
    map_heat = [
        {
            "name": row.poi_name,
            "value": [float(row.lng), float(row.lat), float(row.order_amount)],
        }
        for row in poi_agg.itertuples(index=False)
    ]

    # Chart-map data: [lng, lat, order_count, order_amount]
    grid = (
        df.assign(
            lng_cell=(df["lng"] * 100).round(2),
            lat_cell=(df["lat"] * 100).round(2),
        )
        .groupby(["lng_cell", "lat_cell"])
        .agg(order_count=("order_id", "count"), order_amount=("order_amount", "sum"))
        .reset_index()
        .sort_values("order_count", ascending=False)
        .head(600)
    )
    chart_map = [
        [float(row.lng_cell), float(row.lat_cell), int(row.order_count), float(row.order_amount)]
        for row in grid.itertuples(index=False)
    ]

    data = {
        "meta": {
            "title": "上海夜间消费活力大屏",
            "generatedFrom": str(DATA_PATH),
        },
        "hours": HOUR_ORDER,
        "kpi": kpi,
        "districtRevenue": district_revenue_list,
        "hourlyAvg": {
            "weekday": weekday_series,
            "weekend": weekend_series,
        },
        "categoryShare": category_share_list,
        "categoryHourly": category_series,
        "scatter": scatter_points,
        "mapHeat": map_heat,
        "chartMap": chart_map,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(to_js(data), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

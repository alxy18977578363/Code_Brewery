"""
Prediction Analysis Service
ML-based restaurant rating prediction with cached training and analysis payloads.
"""

import re
import time

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer

from app.services.overview_service import OverviewService

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    XGBRegressor = None
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    HAS_LGB = True
except ImportError:
    LGBMRegressor = None
    HAS_LGB = False

RANDOM_STATE = 42
TARGET = "rating"


class PredictionAnalysisService:
    """ML rating prediction analysis with in-memory caching."""

    _cache = None

    @classmethod
    def get_payload(cls) -> dict:
        if cls._cache is not None:
            return cls._cache
        cls._cache = cls._compute_payload()
        return cls._cache

    @classmethod
    def _load_dataframe(cls) -> pd.DataFrame:
        dataframe = pd.DataFrame(OverviewService.get_overview_payload()).copy()
        dataframe["rating"] = pd.to_numeric(dataframe["rating"], errors="coerce")
        dataframe["market_segment"] = dataframe["market_segment"].fillna("Unknown").astype(str)
        dataframe["area"] = dataframe["area"].fillna("Unknown").astype(str)
        dataframe["features"] = dataframe["features"].fillna("").astype(str)
        dataframe["cuisine"] = dataframe["cuisine"].fillna("").astype(str)
        dataframe["top_dishes"] = dataframe["top_dishes"].fillna("").astype(str)
        dataframe["latitude"] = pd.to_numeric(dataframe["latitude"], errors="coerce")
        dataframe["longitude"] = pd.to_numeric(dataframe["longitude"], errors="coerce")
        return dataframe.dropna(subset=["rating"]).reset_index(drop=True)

    @classmethod
    def _token_text(cls, value):
        if pd.isna(value):
            return ""
        tokens = []
        for item in str(value).split(","):
            item = item.strip().lower()
            if item:
                tokens.append(re.sub(r"\s+", "_", item))
        return " ".join(tokens)

    @classmethod
    def _token_count(cls, value):
        if pd.isna(value):
            return 0
        return len([item for item in str(value).split(",") if item.strip()])

    @classmethod
    def _engineer_features(cls, df):
        out = df.copy()
        for col in ["cuisine", "features", "top_dishes"]:
            out[f"{col}_tokens"] = out[col].map(cls._token_text)
            out[f"{col}_count"] = out[col].map(cls._token_count)

        name_counts = out["restaurant"].value_counts()
        out["same_name_outlets"] = out["restaurant"].map(name_counts).astype(int)
        out["is_multi_outlet_name"] = out["same_name_outlets"].gt(1).astype(int)

        lat0 = out["latitude"].median()
        lon0 = out["longitude"].median()
        out["lat_offset"] = out["latitude"] - lat0
        out["lon_offset"] = out["longitude"] - lon0
        out["distance_to_city_median_km"] = np.sqrt(
            (out["lat_offset"] * 111.0) ** 2 + (out["lon_offset"] * 102.0) ** 2
        )
        return out

    @classmethod
    def _make_preprocessor(cls, sparse_output=True):
        categorical_cols = ["market_segment", "area"]
        numeric_cols = [
            "latitude", "longitude", "lat_offset", "lon_offset",
            "distance_to_city_median_km",
            "same_name_outlets", "is_multi_outlet_name",
            "cuisine_count", "features_count", "top_dishes_count",
        ]

        def select_text_column(col):
            return FunctionTransformer(
                lambda data: data[col].fillna("").astype(str), validate=False
            )

        def make_one_hot():
            try:
                return OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=sparse_output)
            except TypeError:
                return OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse=sparse_output)

        return ColumnTransformer(
            transformers=[
                ("cat", make_one_hot(), categorical_cols),
                ("num", Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]), numeric_cols),
                ("cuisine", Pipeline([
                    ("select", select_text_column("cuisine_tokens")),
                    ("vec", CountVectorizer(
                        token_pattern=r"(?u)\b\w[\w_]+\b",
                        max_features=100, binary=True
                    )),
                ]), ["cuisine_tokens"]),
                ("service", Pipeline([
                    ("select", select_text_column("features_tokens")),
                    ("vec", CountVectorizer(
                        token_pattern=r"(?u)\b\w[\w_]+\b",
                        max_features=90, binary=True
                    )),
                ]), ["features_tokens"]),
                ("dish", Pipeline([
                    ("select", select_text_column("top_dishes_tokens")),
                    ("vec", TfidfVectorizer(
                        token_pattern=r"(?u)\b\w[\w_]+\b",
                        max_features=350, min_df=3, sublinear_tf=True
                    )),
                ]), ["top_dishes_tokens"]),
            ],
            sparse_threshold=1.0 if sparse_output else 0.0,
            verbose_feature_names_out=True,
        )

    @classmethod
    def _make_pipeline(cls, model, sparse_output=True):
        return Pipeline([
            ("preprocess", cls._make_preprocessor(sparse_output=sparse_output)),
            ("model", model),
        ])

    @classmethod
    def _compute_payload(cls) -> dict:
        t_start = time.time()

        # --- Data Loading & Feature Engineering ---
        df = cls._load_dataframe()
        model_df = cls._engineer_features(df)

        feature_cols = [
            "market_segment", "area",
            "latitude", "longitude", "lat_offset", "lon_offset", "distance_to_city_median_km",
            "same_name_outlets", "is_multi_outlet_name",
            "cuisine_count", "features_count", "top_dishes_count",
            "cuisine_tokens", "features_tokens", "top_dishes_tokens",
        ]
        X = model_df[feature_cols].copy()
        y = model_df[TARGET].copy()
        groups = model_df["restaurant"].copy()

        # --- Feature Audit ---
        feature_blocks = [
            {"block": "market segment", "count": 1,
             "cols": [f"{model_df['market_segment'].nunique()} segment labels"]},
            {"block": "area", "count": 1,
             "cols": [f"{model_df['area'].nunique()} area labels"]},
            {"block": "numeric geography/footprint", "count": 10,
             "cols": ["lat", "lon", "offsets", "distance", "chain footprint", "token counts"]},
            {"block": "cuisine tokens", "count": 1,
             "cols": [f"{model_df['cuisine_tokens'].str.split().explode().nunique()} unique tags"]},
            {"block": "service feature tokens", "count": 1,
             "cols": [f"{model_df['features_tokens'].str.split().explode().nunique()} unique tags"]},
            {"block": "dish tokens", "count": 1,
             "cols": [f"{model_df['top_dishes_tokens'].str.split().explode().nunique()} unique tags"]},
        ]

        # --- Split ---
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=RANDOM_STATE)
        train_idx, test_idx = next(splitter.split(X, y, groups=groups))

        X_train, X_test = X.iloc[train_idx].copy(), X.iloc[test_idx].copy()
        y_train, y_test = y.iloc[train_idx].copy(), y.iloc[test_idx].copy()
        groups_train = groups.iloc[train_idx].copy()

        split_audit = {
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "train_unique_names": int(groups_train.nunique()),
            "test_unique_names": int(groups.iloc[test_idx].nunique()),
            "train_mean": round(float(y_train.mean()), 4),
            "test_mean": round(float(y_test.mean()), 4),
        }

        # --- Model Training ---
        model_specs = [
            ("Ridge", Ridge(alpha=10.0, random_state=RANDOM_STATE), True),
            ("ElasticNet", ElasticNet(alpha=0.006, l1_ratio=0.15, max_iter=9000, random_state=RANDOM_STATE), True),
            ("RandomForest", RandomForestRegressor(n_estimators=130, min_samples_leaf=5, max_features=0.60, random_state=RANDOM_STATE, n_jobs=-1), False),
            ("HistGradientBoosting", HistGradientBoostingRegressor(max_iter=180, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=0.05, random_state=RANDOM_STATE), False),
        ]
        if HAS_XGB:
            model_specs.append(
                ("XGBoost", XGBRegressor(
                    n_estimators=320, max_depth=3, learning_rate=0.04,
                    subsample=0.8, colsample_bytree=0.7, reg_lambda=1.8,
                    objective="reg:squarederror", tree_method="hist",
                    random_state=RANDOM_STATE, n_jobs=-1, verbosity=0
                ), False)
            )
        if HAS_LGB:
            model_specs.append(
                ("LightGBM", LGBMRegressor(
                    n_estimators=260, learning_rate=0.04, num_leaves=31,
                    min_child_samples=35, subsample=0.9, colsample_bytree=0.85,
                    random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1
                ), False)
            )

        fitted_models = {}
        leaderboard_rows = []

        # Baseline
        baseline = DummyRegressor(strategy="mean")
        baseline.fit(X_train, y_train)
        baseline_pred = baseline.predict(X_test)
        leaderboard_rows.append({
            "model": "MeanBaseline",
            "mae_train": None,
            "mae_test": round(float(mean_absolute_error(y_test, baseline_pred)), 4),
            "rmse_test": round(float(np.sqrt(mean_squared_error(y_test, baseline_pred))), 4),
            "r2_test": round(float(r2_score(y_test, baseline_pred)), 4),
            "is_best": False,
        })
        fitted_models["MeanBaseline"] = baseline

        available_models = []
        for name, estimator, sparse in model_specs:
            pipeline = cls._make_pipeline(estimator, sparse_output=sparse)
            pipeline.fit(X_train, y_train)

            train_pred = pipeline.predict(X_train)
            test_pred = pipeline.predict(X_test)
            mae_train = float(mean_absolute_error(y_train, train_pred))
            mae_test = float(mean_absolute_error(y_test, test_pred))
            rmse_test = float(np.sqrt(mean_squared_error(y_test, test_pred)))
            r2_test = float(r2_score(y_test, test_pred))

            fitted_models[name] = pipeline
            available_models.append(name)
            leaderboard_rows.append({
                "model": name,
                "mae_train": round(mae_train, 4),
                "mae_test": round(mae_test, 4),
                "rmse_test": round(rmse_test, 4),
                "r2_test": round(r2_test, 4),
                "is_best": False,
            })

        # Sort and pick best
        test_rows = [r for r in leaderboard_rows if r["model"] != "MeanBaseline"]
        if test_rows:
            best_row = min(test_rows, key=lambda r: r["mae_test"])
            best_row["is_best"] = True
            best_name = best_row["model"]
        else:
            best_name = "MeanBaseline"

        best_model = fitted_models[best_name]
        test_pred = best_model.predict(X_test)

        # --- Residual Anatomy ---
        test_meta = model_df.iloc[test_idx][["restaurant", "market_segment", "area", "rating", "same_name_outlets"]].copy()
        test_meta["prediction"] = np.clip(test_pred, 0, 5)
        test_meta["residual"] = test_meta["rating"] - test_meta["prediction"]
        test_meta["abs_error"] = test_meta["residual"].abs()

        # Hexbin (2D histogram)
        hex_n = 40
        x_edges = np.linspace(0, 5, hex_n + 1)
        y_edges = np.linspace(0, 5, hex_n + 1)
        hex_counts, _, _ = np.histogram2d(
            test_meta["rating"].values, test_meta["prediction"].values,
            bins=[x_edges, y_edges]
        )

        # Residual histogram
        res_bins = np.linspace(-1.6, 1.6, 50)
        res_counts, res_edges = np.histogram(test_meta["residual"].values, bins=res_bins)

        residual_anatomy = {
            "hexbin": {
                "x_edges": [round(float(e), 3) for e in x_edges],
                "y_edges": [round(float(e), 3) for e in y_edges],
                "counts": hex_counts.astype(int).tolist(),
            },
            "histogram": {
                "bin_edges": [round(float(e), 3) for e in res_edges],
                "counts": res_counts.astype(int).tolist(),
            },
            "best_model": best_name,
        }

        # --- Error by Segment ---
        seg_err = (
            test_meta.groupby("market_segment")
            .agg(rows=("rating", "size"), mae=("abs_error", "mean"),
                 bias=("residual", "mean"))
            .sort_values("mae", ascending=False)
        )
        error_by_segment = [
            {"segment": seg, "mae": round(float(r.mae), 4),
             "bias": round(float(r.bias), 4), "count": int(r.rows)}
            for seg, r in seg_err.iterrows()
        ]

        # --- Error by Area (top 20) ---
        area_err = (
            test_meta.groupby("area")
            .agg(rows=("rating", "size"), mae=("abs_error", "mean"),
                 bias=("residual", "mean"))
            .query("rows >= 18")
            .sort_values("mae", ascending=False)
            .head(20)
        )
        error_by_area = [
            {"area": area, "mae": round(float(r.mae), 4),
             "bias": round(float(r.bias), 4), "count": int(r.rows)}
            for area, r in area_err.iterrows()
        ]

        # --- Permutation Importance ---
        perm_sample_size = min(1800, len(X_test))
        perm_X = X_test.sample(perm_sample_size, random_state=RANDOM_STATE)
        perm_y = y_test.loc[perm_X.index]
        perm = permutation_importance(
            best_model, perm_X, perm_y,
            scoring="neg_mean_absolute_error",
            n_repeats=6, random_state=RANDOM_STATE, n_jobs=1,
        )
        perm_df = (
            pd.DataFrame({
                "feature": X_test.columns,
                "importance_mean": perm.importances_mean,
                "importance_std": perm.importances_std,
            })
            .sort_values("importance_mean", ascending=False)
            .head(14)
        )
        permutation_importance_data = [
            {"feature": row.feature, "importance_mean": round(float(row.importance_mean), 4),
             "importance_std": round(float(row.importance_std), 4)}
            for _, row in perm_df.iterrows()
        ]

        # --- Ridge Coefficients ---
        ridge_pipe = fitted_models.get("Ridge")
        if ridge_pipe is None:
            ridge_pipe = cls._make_pipeline(Ridge(alpha=10.0, random_state=RANDOM_STATE), sparse_output=True)
            ridge_pipe.fit(X_train, y_train)

        try:
            preprocessor = ridge_pipe.named_steps["preprocess"]
            cat_encoder = preprocessor.named_transformers_["cat"]
            cat_names = list(cat_encoder.get_feature_names_out(["market_segment", "area"]))
            num_names = [f"num__{c}" for c in [
                "latitude", "longitude", "lat_offset", "lon_offset",
                "distance_to_city_median_km",
                "same_name_outlets", "is_multi_outlet_name",
                "cuisine_count", "features_count", "top_dishes_count",
            ]]
            text_names = []
            for bname, prefix in [("cuisine", "cuisine"), ("service", "service"), ("dish", "dish")]:
                vec = preprocessor.named_transformers_[bname].named_steps["vec"]
                text_names.extend([f"{prefix}__{t}" for t in vec.get_feature_names_out()])
            feature_names = np.array(cat_names + num_names + text_names, dtype=object)
        except Exception:
            feature_names = np.array([f"feature_{i}" for i in range(1000)])

        ridge_coefs = np.asarray(ridge_pipe.named_steps["model"].coef_).ravel()
        if len(feature_names) != len(ridge_coefs):
            feature_names = np.array([f"feature_{i}" for i in range(len(ridge_coefs))])

        coef_df = pd.DataFrame({"feature": feature_names, "coefficient": ridge_coefs})
        coef_df = coef_df.loc[coef_df["coefficient"].abs().gt(1e-8)].copy()

        def tidy(name):
            for prefix in ["cat__market_segment_", "cat__area_", "num__", "cuisine__", "service__", "dish__"]:
                name = name.replace(prefix, "")
            for suf in ["features_tokens__", "cuisine_tokens__", "top_dishes_tokens__"]:
                name = name.replace(suf, "")
            return name.replace("_", " ")

        coef_df["label"] = coef_df["feature"].map(tidy)

        positive = coef_df.nlargest(14, "coefficient").sort_values("coefficient")
        negative = coef_df.nsmallest(14, "coefficient").sort_values("coefficient", ascending=False)

        ridge_coefficients = {
            "positive": [{"feature": r.label, "coefficient": round(float(r.coefficient), 4)} for _, r in positive.iterrows()],
            "negative": [{"feature": r.label, "coefficient": round(float(r.coefficient), 4)} for _, r in negative.iterrows()],
        }

        # --- Partial Dependence ---
        pdp_sample = X_test.sample(min(1500, len(X_test)), random_state=RANDOM_STATE).copy()

        def numeric_pdp(feature, values):
            means = []
            for v in values:
                temp = pdp_sample.copy()
                temp[feature] = v
                means.append(float(np.mean(best_model.predict(temp))))
            return {"x_values": [round(float(v), 4) for v in values],
                    "y_values": [round(float(m), 4) for m in means]}

        same_name_grid = np.array(sorted(set(
            np.clip(np.round(np.quantile(model_df["same_name_outlets"], np.linspace(0, 1, 11))).astype(int), 1,
                    model_df["same_name_outlets"].max())
        )))
        distance_grid = np.quantile(model_df["distance_to_city_median_km"], np.linspace(0.03, 0.97, 18))
        dish_count_grid = np.array(sorted(model_df["top_dishes_count"].dropna().unique()))

        pdp_brand = numeric_pdp("same_name_outlets", same_name_grid)
        pdp_distance = numeric_pdp("distance_to_city_median_km", distance_grid)
        pdp_dish = numeric_pdp("top_dishes_count", dish_count_grid)

        # Segment PD
        seg_values = model_df["market_segment"].value_counts().index.tolist()
        seg_pd_rows = []
        for seg in seg_values:
            temp = pdp_sample.copy()
            temp["market_segment"] = seg
            seg_pd_rows.append({"segment": seg, "prediction": round(float(np.mean(best_model.predict(temp))), 4)})
        seg_pd_rows.sort(key=lambda r: r["prediction"])

        partial_dependence_data = {
            "brand_footprint": pdp_brand,
            "location_distance": pdp_distance,
            "menu_description": pdp_dish,
            "segment_partial": seg_pd_rows,
        }

        # --- Worst Misses ---
        worst = (
            test_meta.sort_values("abs_error", ascending=False)
            .head(18)
            [["restaurant", "market_segment", "area", "rating", "prediction", "residual", "abs_error"]]
            .reset_index(drop=True)
        )
        worst_misses = [
            {"restaurant": r.restaurant, "segment": r.market_segment, "area": r.area,
             "actual": round(float(r.rating), 1), "predicted": round(float(r.prediction), 3),
             "residual": round(float(r.residual), 3), "abs_error": round(float(r.abs_error), 3)}
            for _, r in worst.iterrows()
        ]

        elapsed = round(time.time() - t_start, 1)
        print(f"PredictionAnalysisService: payload computed in {elapsed}s")

        return {
            "meta": {
                "n_total": int(len(model_df)),
                "n_train": int(len(X_train)),
                "n_test": int(len(X_test)),
                "n_features": int(X.shape[1]),
                "feature_blocks": feature_blocks,
                "available_models": available_models,
                "elapsed_seconds": elapsed,
            },
            "split_audit": split_audit,
            "leaderboard": leaderboard_rows,
            "residual_anatomy": residual_anatomy,
            "error_by_segment": error_by_segment,
            "error_by_area": error_by_area,
            "permutation_importance": permutation_importance_data,
            "ridge_coefficients": ridge_coefficients,
            "partial_dependence": partial_dependence_data,
            "worst_misses": worst_misses,
        }

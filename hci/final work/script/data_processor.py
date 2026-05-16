

"""
Chennai Restaurant Dataset - Data Processor Module
数据处理模块：规范化、清洁、特征工程
"""

import numpy as np
import pandas as pd

try:
    from .utils import normalize_columns, explode_attribute
    from .config import EXPECTED_COLUMNS, RATING_BINS, RATING_LABELS
except ImportError:
    from utils import normalize_columns, explode_attribute
    from config import EXPECTED_COLUMNS, RATING_BINS, RATING_LABELS


def preprocess_dataframe(raw_df, add_features=True):
    """
    预处理原始数据框：规范化列名、添加衍生特征
    
    Parameters
    ----------
    raw_df : pd.DataFrame
        原始数据框
    add_features : bool
        是否添加衍生特征
    
    Returns
    -------
    pd.DataFrame
        已处理的数据框
    """
    # 步骤1: 规范化列名
    df = normalize_columns(raw_df)
    
    # 步骤2: 验证必需列
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"❌ 缺失必需列: {missing_cols}")
    
    # 步骤3: 选择并排序列
    df = df[EXPECTED_COLUMNS].copy()
    
    # 步骤4: 添加ID和衍生特征
    if add_features:
        df = add_derived_features(df)
    
    return df


def add_derived_features(df):
    """
    添加衍生特征列
    
    Parameters
    ----------
    df : pd.DataFrame
        已规范化的数据框
    
    Returns
    -------
    pd.DataFrame
        添加了以下新列的数据框：
        - restaurant_id: 唯一标识符
        - rating_band: 评分等级 (fragile/developing/solid/strong/elite)
        - same_name_outlets: 同名出现次数
        - is_multi_outlet_name: 是否有多个同名出现
    
    Examples
    --------
    >>> df = add_derived_features(df)
    >>> df[['restaurant', 'rating_band', 'same_name_outlets']].head()
    """
    df = df.copy()
    
    # 1. 添加唯一ID
    df["restaurant_id"] = np.arange(1, len(df) + 1)
    
    # 2. 创建评分分段 (rating_band)
    df["rating_band"] = pd.cut(
        df["rating"],
        bins=RATING_BINS,
        labels=RATING_LABELS,
    )
    
    # 3. 计算同名出现次数
    name_counts = df["restaurant"].value_counts()
    df["same_name_outlets"] = df["restaurant"].map(name_counts)
    
    # 4. 标记多出口品牌
    df["is_multi_outlet_name"] = df["same_name_outlets"] > 1
    
    return df


def get_quality_metrics(df):
    """
    生成数据质量指标汇总
    
    Parameters
    ----------
    df : pd.DataFrame
        已处理的数据框
    
    Returns
    -------
    pd.DataFrame
        包含关键指标的汇总表
    
    Examples
    --------
    >>> metrics = get_quality_metrics(df)
    >>> print(metrics)
    """
    metrics = pd.DataFrame({
        "metric": [
            "总餐厅数",
            "唯一餐厅名称",
            "市场细分数",
            "覆盖区域数",
            "评分最小值",
            "评分中位数",
            "评分均值",
            "评分最大值",
            "纬度范围",
            "经度范围",
            "缺失评分数",
        ],
        "value": [
            f"{len(df):,}",
            f"{df['restaurant'].nunique():,}",
            f"{df['market_segment'].nunique():,}",
            f"{df['area'].nunique():,}",
            f"{df['rating'].min():.1f}",
            f"{df['rating'].median():.1f}",
            f"{df['rating'].mean():.2f}",
            f"{df['rating'].max():.1f}",
            f"{df['latitude'].min():.4f} 至 {df['latitude'].max():.4f}",
            f"{df['longitude'].min():.4f} 至 {df['longitude'].max():.4f}",
            f"{df['rating'].isna().sum():,}",
        ],
    })
    return metrics


def create_long_format_data(df):
    """
    创建长格式数据集 - 用于多维分析
    
    Parameters
    ----------
    df : pd.DataFrame
        已处理的数据框
    
    Returns
    -------
    dict
        包含三个长格式数据集的字典：
        - "cuisine": 菜系 (每行一个菜系标签)
        - "feature": 特色 (每行一个服务特色)
        - "dish": 菜品 (每行一个顶级菜品)
    
    Examples
    --------
    >>> long_data = create_long_format_data(df)
    >>> print(f"菜系行数: {len(long_data['cuisine']):,}")
    >>> print(f"特色行数: {len(long_data['feature']):,}")
    >>> print(f"菜品行数: {len(long_data['dish']):,}")
    """
    cuisine_long = explode_attribute(df, "cuisine", "cuisine")
    feature_long = explode_attribute(df, "features", "feature")
    dish_long = explode_attribute(df, "top_dishes", "dish")
    
    return {
        "cuisine": cuisine_long,
        "feature": feature_long,
        "dish": dish_long,
    }


def get_attribute_summary(long_format_data):
    """
    生成多值属性的摘要统计
    
    Parameters
    ----------
    long_format_data : dict
        由create_long_format_data返回的字典
    
    Returns
    -------
    pd.DataFrame
        属性摘要表
    
    Examples
    --------
    >>> summary = get_attribute_summary(long_data)
    >>> print(summary)
    """
    cuisine_long = long_format_data["cuisine"]
    feature_long = long_format_data["feature"]
    dish_long = long_format_data["dish"]
    
    n_total_restaurants = len(set(cuisine_long["restaurant_id"]))
    
    summary = pd.DataFrame({
        "attribute": ["cuisine (菜系)", "service feature (服务特色)", "top dish (顶级菜品)"],
        "total_tokens": [
            len(cuisine_long),
            len(feature_long),
            len(dish_long),
        ],
        "unique_tokens": [
            cuisine_long["cuisine"].nunique(),
            feature_long["feature"].nunique(),
            dish_long["dish"].nunique(),
        ],
        "avg_tokens_per_restaurant": [
            len(cuisine_long) / n_total_restaurants,
            len(feature_long) / n_total_restaurants,
            len(dish_long) / n_total_restaurants,
        ],
    })
    
    return summary


def filter_dataframe(df, market_segment=None, area=None, rating_min=None, rating_max=None):
    """
    按多个条件过滤数据框
    
    Parameters
    ----------
    df : pd.DataFrame
        源数据框
    market_segment : str or list, optional
        市场细分过滤
    area : str or list, optional
        地区过滤
    rating_min : float, optional
        最小评分阈值
    rating_max : float, optional
        最大评分阈值
    
    Returns
    -------
    pd.DataFrame
        已过滤的数据框
    
    Examples
    --------
    >>> filtered = filter_dataframe(df, market_segment="Restaurant", rating_min=3.5)
    >>> print(f"过滤后: {len(filtered):,} 行")
    """
    result = df.copy()
    
    if market_segment is not None:
        if isinstance(market_segment, str):
            market_segment = [market_segment]
        result = result[result["market_segment"].isin(market_segment)]
    
    if area is not None:
        if isinstance(area, str):
            area = [area]
        result = result[result["area"].isin(area)]
    
    if rating_min is not None:
        result = result[result["rating"] >= rating_min]
    
    if rating_max is not None:
        result = result[result["rating"] <= rating_max]
    
    return result


if __name__ == "__main__":
    # 快速测试
    try:
        from .data_loader import load_datasets
    except ImportError:
        from data_loader import load_datasets

    raw, _ = load_datasets(verbose=False)
    df = preprocess_dataframe(raw)
    print("✓ 数据预处理成功")
    print(get_quality_metrics(df))

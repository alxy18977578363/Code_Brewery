"""
Chennai Restaurant Dataset - Utility Functions Module
工具函数模块：通用的绘图、数据处理工具函数
"""

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from .config import PALETTE
except ImportError:
    from config import PALETTE

# ============================================================================
# 绘图工具函数
# ============================================================================

def clean_axis(ax, grid_axis="x"):
    """
    清洁坐标轴外观 - 移除边框和刻度线
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        要清洁的坐标轴
    grid_axis : str
        显示网格的轴 ('x', 'y', 'both')
    
    Returns
    -------
    matplotlib.axes.Axes
        修改后的坐标轴
    """
    ax.grid(True, axis=grid_axis)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)
    return ax


def add_panel_title(ax, title, subtitle=None, x=0.0, y=1.115, subtitle_gap=0.075):
    """
    在图表上方添加标题和副标题
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        目标坐标轴
    title : str
        主标题
    subtitle : str, optional
        副标题
    x : float
        水平位置 (0-1)
    y : float
        垂直位置 (相对于轴高度)
    subtitle_gap : float
        副标题与主标题的垂直间距
    """
    ax.text(
        x, y, title, transform=ax.transAxes, ha="left", va="bottom",
        fontsize=15, fontweight="bold", color=PALETTE["ink"], clip_on=False
    )
    if subtitle:
        ax.text(
            x, y - subtitle_gap, subtitle, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10, color=PALETTE["muted"], clip_on=False, wrap=True
        )


def label_bar_ends(ax, values, fmt="{:.0f}", xpad=0.01, color=None):
    """
    在条形图末端添加数值标签
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        条形图所在的坐标轴 (水平条形)
    values : list or array
        每条条形的数值
    fmt : str
        标签格式化字符串
    xpad : float
        标签到条形末端的水平间距
    color : str, optional
        标签颜色
    """
    if len(values) == 0:
        return
    xmax = max(values) if max(values) else 1
    for y, value in enumerate(values):
        ax.text(
            value + xmax * xpad, y, fmt.format(value), 
            va="center", ha="left", fontsize=9, 
            color=color or PALETTE["muted"]
        )


# ============================================================================
# 数据处理工具函数
# ============================================================================

def split_tokens(series):
    """
    将逗号分隔的文本字段拆分为单个令牌
    
    Parameters
    ----------
    series : pd.Series
        包含逗号分隔值的Series
    
    Returns
    -------
    pd.Series
        展开后的单个令牌Series，保留原始索引
    
    Examples
    --------
    >>> s = pd.Series(["Chinese, North Indian", "Biryani"])
    >>> split_tokens(s)
    0    Chinese
    0    North Indian
    1    Biryani
    dtype: object
    """
    return (
        series.fillna("")
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .replace("", np.nan)
        .dropna()
    )


def entropy_from_counts(row):
    """
    计算Shannon熵 - 衡量多样性指数 (0=单一, 1=完全多样)
    
    Parameters
    ----------
    row : pd.Series
        包含计数值的Series
    
    Returns
    -------
    float
        归一化后的Shannon熵 (0-1)
    
    Examples
    --------
    >>> row = pd.Series([100, 50, 25, 25])  # 高多样性
    >>> entropy_from_counts(row)  # 接近1
    
    >>> row = pd.Series([1000, 1, 1, 1])  # 低多样性
    >>> entropy_from_counts(row)  # 接近0
    """
    counts = row[row > 0].astype(float)
    if counts.empty:
        return 0.0
    p = counts / counts.sum()
    return float(-(p * np.log(p)).sum() / np.log(len(row)))


def normalize_columns(frame):
    """
    规范化数据框列名 - 转为小写、下划线分隔、去除特殊字符
    
    Parameters
    ----------
    frame : pd.DataFrame
        原始数据框
    
    Returns
    -------
    pd.DataFrame
        列名已规范化的数据框
    
    Examples
    --------
    >>> df = pd.DataFrame({"Name Of Restaurant": [1], "Area Location": [2]})
    >>> normalize_columns(df).columns.tolist()
    ['name_of_restaurant', 'area_location']
    """
    out = frame.copy()
    out.columns = (
        out.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^0-9a-z]+", "_", regex=True)
        .str.strip("_")
    )
    out = out.rename(columns={
        "features_category": "features",
        "area_location": "area",
        "name_of_restaurant": "restaurant",
        "dining_rating": "rating",
    })
    return out


def explode_attribute(frame, source_col, token_name):
    """
    将多值属性列展开为长格式 (用于菜系、特色、菜品分析)
    
    Parameters
    ----------
    frame : pd.DataFrame
        包含多值列的数据框
    source_col : str
        要展开的列名 (e.g., "cuisine", "features")
    token_name : str
        新列的名称 (e.g., "cuisine", "feature")
    
    Returns
    -------
    pd.DataFrame
        长格式的数据框，每行一个令牌
    
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     "restaurant_id": [1, 2],
    ...     "cuisine": ["Chinese, North Indian", "Biryani"]
    ... })
    >>> explode_attribute(df, "cuisine", "cuisine")
    #结果：3行，每个菜系一行
    """
    token_series = split_tokens(frame[source_col])
    base_cols = ["restaurant_id", "restaurant", "market_segment", "area", 
                 "rating", "latitude", "longitude"]
    base = frame.loc[token_series.index, base_cols].copy()
    base[token_name] = token_series.values
    return base.reset_index(drop=True)


def validate_rating_range(series, min_val=0.0, max_val=5.0):
    """
    验证评分是否在有效范围内
    
    Parameters
    ----------
    series : pd.Series
        评分Series
    min_val : float
        最小有效评分
    max_val : float
        最大有效评分
    
    Returns
    -------
    dict
        验证结果 {"is_valid": bool, "invalid_count": int, "invalid_values": list}
    """
    invalid = series[(series < min_val) | (series > max_val)]
    return {
        "is_valid": len(invalid) == 0,
        "invalid_count": len(invalid),
        "invalid_values": invalid.unique().tolist() if len(invalid) > 0 else []
    }


def validate_coordinates(lat_series, lon_series, lat_bounds=(12.6, 13.2), lon_bounds=(79.7, 80.3)):
    """
    验证坐标是否在Chennai地理边界内
    
    Parameters
    ----------
    lat_series : pd.Series
        纬度Series
    lon_series : pd.Series
        经度Series
    lat_bounds : tuple
        纬度范围 (min, max)
    lon_bounds : tuple
        经度范围 (min, max)
    
    Returns
    -------
    dict
        验证结果
    """
    valid_lat = (lat_series >= lat_bounds[0]) & (lat_series <= lat_bounds[1])
    valid_lon = (lon_series >= lon_bounds[0]) & (lon_series <= lon_bounds[1])
    valid_both = valid_lat & valid_lon
    
    return {
        "total": len(lat_series),
        "valid": valid_both.sum(),
        "invalid_latitude": (~valid_lat).sum(),
        "invalid_longitude": (~valid_lon).sum(),
    }


def detect_local_dishes(series, pattern):
    """
    检测本地菜品 (Chennai特色菜)
    
    Parameters
    ----------
    series : pd.Series
        菜品名称Series
    pattern : str
        正则表达式模式
    
    Returns
    -------
    pd.Series
        布尔Series，True表示本地菜品
    """
    return series.str.contains(pattern, case=False, regex=True, na=False)

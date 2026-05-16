"""
Chennai Restaurant Dataset - Visualizations Module
可视化模块：所有绘图函数
"""

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from config import (
    PALETTE, CHENNAI_CMAP, RATING_CMAP, 
    SEGMENT_COLORS, LOCAL_DISH_PATTERN, FIGURE_WIDTH_SINGLE, FIGURE_WIDTH_DOUBLE
)
from utils import clean_axis, add_panel_title, label_bar_ends, detect_local_dishes


def plot_scorecard(df, long_format_data):
    """
    绘制前厅服务评分卡 - 关键指标卡片 + 评分直方图
    
    Parameters
    ----------
    df : pd.DataFrame
        主数据框
    long_format_data : dict
        长格式数据
    
    Returns
    -------
    matplotlib.figure.Figure
        评分卡图表
    """
    cuisine_long = long_format_data["cuisine"]
    
    metrics = [
        ("Restaurants (餐厅)", f"{len(df):,}", "每一行都是唯一的Zomato URL"),
        ("Areas (区域)", f"{df['area'].nunique():,}", "社区级覆盖"),
        ("Segments (细分)", f"{df['market_segment'].nunique():,}", "餐厅、快餐等"),
        ("Cuisine Tags (菜系标签)", f"{cuisine_long['cuisine'].nunique():,}", "多标签菜系词汇"),
        ("Mean Rating (平均评分)", f"{df['rating'].mean():.2f}", "按出口行加权"),
        ("Multi-Outlet Names (多出口品牌)", f"{df['is_multi_outlet_name'].mean()*100:.1f}%", "同名出现多次"),
    ]
    
    fig = plt.figure(figsize=(15, 8), constrained_layout=True)
    gs = fig.add_gridspec(2, 6, height_ratios=[1.0, 2.0])
    
    # 绘制KPI卡片
    for i, (label, value, note) in enumerate(metrics):
        ax = fig.add_subplot(gs[0, i])
        ax.axis("off")
        card = FancyBboxPatch(
            (0.02, 0.08), 0.96, 0.84,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            facecolor="#fff5df", edgecolor=PALETTE["grid"], linewidth=1.0,
            transform=ax.transAxes,
        )
        ax.add_patch(card)
        ax.text(0.09, 0.68, label.upper(), transform=ax.transAxes, 
               fontsize=8.5, color=PALETTE["muted"], fontweight="bold")
        ax.text(0.09, 0.39, value, transform=ax.transAxes, 
               fontsize=22, color=PALETTE["ink"], fontweight="bold")
        ax.text(0.09, 0.18, note, transform=ax.transAxes, 
               fontsize=7.8, color=PALETTE["muted"], wrap=True)
    
    # 绘制评分直方图
    ax = fig.add_subplot(gs[1, :])
    bins = np.arange(0.0, 5.05, 0.1)
    counts, edges = np.histogram(df["rating"], bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    colors = RATING_CMAP((centers - centers.min()) / (centers.max() - centers.min()))
    
    ax.bar(centers, counts, width=0.075, color=colors, edgecolor=PALETTE["paper"], linewidth=0.7)
    ax.axvline(df["rating"].median(), color=PALETTE["ink"], lw=1.6, ls="--")
    ax.text(df["rating"].median() + 0.03, counts.max() * 0.92, 
           f"median {df['rating'].median():.1f}", color=PALETTE["ink"], fontsize=10)
    
    ax.set_xlabel("Dining rating")
    ax.set_ylabel("Restaurant count")
    ax.set_xlim(0, 5)
    add_panel_title(ax, "评分集中在日常优质等级", 
                   "主文件是完整的，因此无需缺失值填充就可读取分布")
    clean_axis(ax, "y")
    
    return fig


def plot_segment_analysis(analyzer):
    """
    绘制市场细分分析 - 规模对比 + 规模与质量气泡图
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        细分市场分析图表
    """
    segment_stats = analyzer.segment_analysis()
    mean_rating = analyzer.df["rating"].mean()
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1.05, 1.15]})
    
    # 左图：按规模排序的条形图
    plot_stats = segment_stats.sort_values("outlets")
    bar_colors = [PALETTE["leaf"] if seg == "Restaurant" else 
                  PALETTE["turmeric"] if seg == "Fast Food" else 
                  PALETTE["marina"] for seg in plot_stats.index]
    
    axes[0].barh(plot_stats.index, plot_stats["outlets"], color=bar_colors, alpha=0.92)
    label_bar_ends(axes[0], plot_stats["outlets"].tolist(), "{:,.0f}")
    axes[0].set_xlabel("Outlet count")
    add_panel_title(axes[0], "按细分市场的出口规模", "餐厅和快餐行是市场的主要支撑")
    clean_axis(axes[0], "x")
    
    # 右图：气泡图
    sizes = np.sqrt(segment_stats["outlets"]) * 24
    scatter = axes[1].scatter(
        segment_stats["outlets"], segment_stats["avg_rating"],
        s=sizes, c=segment_stats["chain_share"], cmap=CHENNAI_CMAP,
        edgecolor=PALETTE["ink"], linewidth=0.8, alpha=0.9,
    )
    
    for seg, row in segment_stats.iterrows():
        axes[1].annotate(seg, (row["outlets"], row["avg_rating"]), 
                        xytext=(7, 5), textcoords="offset points", fontsize=9)
    
    axes[1].axhline(mean_rating, color=PALETTE["muted"], lw=1.1, ls="--")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Outlet count, log scale")
    axes[1].set_ylabel("Mean dining rating")
    add_panel_title(axes[1], "规模不等同于好评", 
                   "气泡面积=出口数；颜色=同名出口占比")
    clean_axis(axes[1], "both")
    
    cbar = fig.colorbar(scatter, ax=axes[1], fraction=0.04, pad=0.02)
    cbar.set_label("same-name outlet share")
    
    return fig


def plot_rating_ridgelines(analyzer):
    """
    绘制评分脊线图 - 按细分市场的评分分布
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        脊线图
    """
    rating_by_segment = analyzer.rating_by_segment()
    df = analyzer.df
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bins = np.linspace(max(0, df["rating"].min() - 0.05), 5.0, 48)
    centers = (bins[:-1] + bins[1:]) / 2
    kernel = np.array([1, 2, 3, 4, 3, 2, 1], dtype=float)
    kernel /= kernel.sum()
    
    for i, (seg, vals) in enumerate(rating_by_segment.items()):
        hist, _ = np.histogram(vals, bins=bins, density=True)
        smooth = np.convolve(hist, kernel, mode="same")
        if smooth.max() > 0:
            smooth = smooth / smooth.max() * 0.72
        
        baseline = i * 0.86
        color = RATING_CMAP((np.median(vals) - df["rating"].min()) / 
                           (df["rating"].max() - df["rating"].min()))
        
        ax.fill_between(centers, baseline, baseline + smooth, color=color, alpha=0.76, lw=0)
        ax.plot(centers, baseline + smooth, color=PALETTE["ink"], lw=0.7, alpha=0.5)
        ax.plot([np.median(vals), np.median(vals)], [baseline, baseline + 0.18], 
               color=PALETTE["ink"], lw=1.6)
        ax.text(0.12, baseline + 0.18, f"{seg}  n={len(vals):,}", 
               ha="left", va="center", fontsize=9.5, color=PALETTE["ink"])
    
    ax.set_yticks([])
    ax.set_xlim(0, 5.02)
    ax.set_xlabel("Dining rating")
    add_panel_title(ax, "细分市场评分脊线", 
                   "竖线标记每个细分市场的中位数；填充区域显示平滑的评分分布")
    clean_axis(ax, "x")
    
    return fig


def plot_cuisine_and_dishes(analyzer):
    """
    绘制菜系和菜品分析
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        菜系和菜品分析图表
    """
    cuisine_stats = analyzer.cuisine_analysis(min_outlets=18)
    dish_stats = analyzer.dish_analysis(min_outlets=20)
    top_cuisines = cuisine_stats.head(18).sort_values("outlets")
    top_dishes = dish_stats.head(20).sort_values("outlets")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [1.1, 1.0]})
    
    # 左图：菜系
    colors = [PALETTE["leaf"] if c in ["South Indian", "Biryani", "Chettinad"] 
              else PALETTE["turmeric"] for c in top_cuisines.index]
    axes[0].barh(top_cuisines.index, top_cuisines["outlets"], color=colors, alpha=0.92)
    label_bar_ends(axes[0], top_cuisines["outlets"].tolist(), "{:,.0f}")
    
    ax2 = axes[0].twiny()
    ax2.scatter(top_cuisines["avg_rating"], np.arange(len(top_cuisines)), 
               color=PALETTE["rose"], s=38, zorder=5, edgecolor=PALETTE["ink"], linewidth=0.5)
    ax2.set_xlim(3.0, max(4.5, top_cuisines["avg_rating"].max() + 0.1))
    ax2.set_xlabel("Mean rating dot", color=PALETTE["rose"])
    ax2.tick_params(axis="x", colors=PALETTE["rose"], length=0)
    ax2.grid(False)
    
    axes[0].set_xlabel("Tagged outlets")
    add_panel_title(axes[0], "菜系词汇覆盖范围", 
                   "条形=出口覆盖；玫瑰点=该菜系的平均评分")
    clean_axis(axes[0], "x")
    
    # 右图：菜品
    local_pattern = re.compile(LOCAL_DISH_PATTERN, flags=re.I)
    for y, (dish, row) in enumerate(top_dishes.iterrows()):
        is_local = bool(local_pattern.search(dish))
        color = PALETTE["sambar"] if is_local else PALETTE["marina"]
        axes[1].hlines(y, 0, row["outlets"], color=color, lw=4, alpha=0.70)
        axes[1].scatter(row["outlets"], y, s=85, color=color, 
                       edgecolor=PALETTE["ink"], linewidth=0.7, zorder=3)
    
    axes[1].set_yticks(np.arange(len(top_dishes)))
    axes[1].set_yticklabels(top_dishes.index)
    axes[1].set_xlabel("Tagged outlets")
    add_panel_title(axes[1], "菜品记忆", 
                   "土黄色标记强Chennai/南印度本地菜品术语")
    clean_axis(axes[1], "x")
    
    return fig


def plot_feature_heatmap(analyzer):
    """
    绘制服务特色热力图 - 按细分市场的特色采用率
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        特色热力图
    """
    top_features = analyzer.feature_long["feature"].value_counts().head(16).index.tolist()
    segment_counts = analyzer.df["market_segment"].value_counts()
    segment_order = analyzer.segment_analysis().index.tolist()
    
    feature_matrix = pd.crosstab(analyzer.feature_long["market_segment"], 
                                  analyzer.feature_long["feature"])
    feature_share = feature_matrix.reindex(segment_order)[top_features].div(segment_counts, axis=0).fillna(0)
    
    fig, ax = plt.subplots(figsize=(16.0, 8.8))
    fig.subplots_adjust(left=0.15, right=0.91, bottom=0.31, top=0.78)
    
    im = ax.imshow(feature_share.values, cmap=CHENNAI_CMAP, vmin=0, 
                   vmax=max(0.85, feature_share.values.max()))
    
    ax.set_xticks(np.arange(len(top_features)))
    ax.set_xticklabels(top_features, rotation=43, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(feature_share.index)))
    ax.set_yticklabels(feature_share.index)
    
    for i in range(feature_share.shape[0]):
        for j in range(feature_share.shape[1]):
            val = feature_share.iloc[i, j]
            if val >= 0.22:
                text_color = "#fff7e6" if val > 0.55 else PALETTE["ink"]
                ax.text(j, i, f"{val:.0%}", ha="center", va="center", 
                       fontsize=8.2, color=text_color, fontweight="bold")
    
    ax.set_xlabel("")
    ax.set_ylabel("")
    add_panel_title(ax, "按细分市场的服务特色采用", 
                   "单元格值=特色提及数÷该细分市场总出口数", y=1.16, subtitle_gap=0.085)
    ax.grid(False)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cbar.set_label("segment adoption share")
    
    return fig


def plot_area_analysis(analyzer):
    """
    绘制地区分析 - 高密度地区 + 地区机会地图
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        地区分析图表
    """
    area_stats = analyzer.area_analysis()
    df = analyzer.df
    top_areas = area_stats.head(24).sort_values("outlets")
    area_focus = area_stats.query("outlets >= 25").copy()
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [1.0, 1.1]})
    
    # 左图：高密度地区
    area_colors = CHENNAI_CMAP((top_areas["avg_rating"] - df["rating"].min()) / 
                               (df["rating"].max() - df["rating"].min()))
    axes[0].barh(top_areas.index, top_areas["outlets"], color=area_colors, 
                edgecolor=PALETTE["paper"], linewidth=0.5)
    label_bar_ends(axes[0], top_areas["outlets"].tolist(), "{:,.0f}")
    axes[0].set_xlabel("Outlet count")
    add_panel_title(axes[0], "最高密度地区", "条形颜色跟随每个地区的平均评分")
    clean_axis(axes[0], "x")
    
    # 右图：机会地图
    sc = axes[1].scatter(
        area_focus["outlets"], area_focus["avg_rating"],
        s=np.sqrt(area_focus["outlets"]) * 21,
        c=area_focus["segment_diversity"], cmap=RATING_CMAP,
        edgecolor=PALETTE["ink"], linewidth=0.5, alpha=0.88,
    )
    
    axes[1].axhline(df["rating"].mean(), color=PALETTE["muted"], lw=1, ls="--")
    axes[1].axvline(area_focus["outlets"].median(), color=PALETTE["muted"], lw=1, ls="--")
    
    for area, row in area_focus.sort_values(["outlets", "avg_rating"], ascending=False).head(10).iterrows():
        axes[1].annotate(area, (row["outlets"], row["avg_rating"]), 
                        xytext=(5, 5), textcoords="offset points", fontsize=8.5)
    
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Outlet count, log scale")
    axes[1].set_ylabel("Mean rating")
    add_panel_title(axes[1], "地区机会地图", 
                   "颜色=细分市场多样性；气泡越大=餐厅供应越密集")
    clean_axis(axes[1], "both")
    
    cbar = fig.colorbar(sc, ax=axes[1], fraction=0.035, pad=0.02)
    cbar.set_label("segment diversity")
    
    return fig


def plot_spatial_distribution(analyzer):
    """
    绘制地理空间分布 - 餐厅密度热力图 + 平均评分地表
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        地理空间图表
    """
    geo = analyzer.geo_distribution()
    area_stats = analyzer.area_analysis().head(9)
    
    fig, axes = plt.subplots(1, 2, figsize=(16.5, 8.2))
    fig.subplots_adjust(left=0.06, right=0.93, bottom=0.12, top=0.76, wspace=0.20)
    
    for ax in axes:
        ax.set_facecolor(PALETTE["charcoal"])
        ax.grid(False)
        ax.spines[["top", "right", "left", "bottom"]].set_color("#40342d")
        ax.tick_params(colors="#b9aa98", labelsize=8)
        ax.set_xlabel("Longitude", color="#cdbda7")
        ax.set_ylabel("Latitude", color="#cdbda7")
    
    # 左图：餐厅密度
    hb1 = axes[0].hexbin(
        geo["longitude"], geo["latitude"], gridsize=48, mincnt=1,
        cmap=CHENNAI_CMAP, linewidths=0.05, edgecolors="#1f1b18",
    )
    axes[0].scatter(geo["longitude"], geo["latitude"], s=1.5, color="#fff6dc", alpha=0.035)
    add_panel_title(axes[0], "餐厅行密度", 
                   "十六进制强度计数出口；EDA初期无需底图", y=1.18, subtitle_gap=0.085)
    cb1 = fig.colorbar(hb1, ax=axes[0], fraction=0.035, pad=0.02)
    cb1.set_label("outlets per hex")
    
    # 右图：平均评分地表
    hb2 = axes[1].hexbin(
        geo["longitude"], geo["latitude"], C=geo["rating"], reduce_C_function=np.mean,
        gridsize=48, mincnt=3, cmap=RATING_CMAP, vmin=3.0, vmax=4.4,
        linewidths=0.05, edgecolors="#1f1b18",
    )
    add_panel_title(axes[1], "平均评分地表", 
                   "十六进制需至少3个出口以减少单行噪声", y=1.18, subtitle_gap=0.085)
    cb2 = fig.colorbar(hb2, ax=axes[1], fraction=0.035, pad=0.02)
    cb2.set_label("mean rating")
    
    # 标注顶级地区
    for ax in axes:
        for area, row in area_stats.iterrows():
            ax.text(row["longitude"], row["latitude"], area, fontsize=7.6, 
                   color="#fff4cf", ha="center", va="center", alpha=0.86)
    
    return fig


def plot_chain_footprints(analyzer):
    """
    绘制链状品牌足迹 - 具有多个出口的餐厅品牌
    
    Parameters
    ----------
    analyzer : RestaurantAnalyzer
        分析器实例
    
    Returns
    -------
    matplotlib.figure.Figure
        品牌足迹图表
    """
    chain_stats = analyzer.chain_analysis(min_outlets=10)
    top_chains = chain_stats.head(20).sort_values("outlets")
    df = analyzer.df
    
    fig, ax = plt.subplots(figsize=(12.5, 8))
    colors = RATING_CMAP((top_chains["avg_rating"] - df["rating"].min()) / 
                         (df["rating"].max() - df["rating"].min()))
    
    ax.barh(top_chains.index, top_chains["outlets"], color=colors, 
           edgecolor=PALETTE["paper"], linewidth=0.5)
    
    for y, (name, row) in enumerate(top_chains.iterrows()):
        ax.text(row["outlets"] + 1.0, y, 
               f"{row['outlets']:.0f} outlets | {row['areas']:.0f} areas | {row['avg_rating']:.2f} avg", 
               va="center", fontsize=8.5, color=PALETTE["muted"])
    
    ax.set_xlabel("Rows sharing the same restaurant name")
    add_panel_title(ax, "最大同名品牌足迹", 
                   "将这些视为品牌足迹特征，但在将其称为连锁店之前要验证")
    clean_axis(ax, "x")
    
    return fig

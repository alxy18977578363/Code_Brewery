"""
Chennai Restaurant Dataset - Configuration Module
配置模块：定义调色板、matplotlib设置和常数
"""

import matplotlib as mpl
import numpy as np

# ============================================================================
# 调色板定义 - 印度美食主题
# ============================================================================
PALETTE = {
    "paper": "#fffaf0",        # 暖色笔记本背景
    "ink": "#2b2522",          # 咖啡墨水（深色文字）
    "muted": "#766b60",        # 烘烤芝麻色（次要文字）
    "grid": "#e4d5c2",         # 石锅饼线（网格线）
    "leaf": "#2f6b45",         # 香蕉叶（深绿）
    "leaf_light": "#8cb369",   # 浅叶绿
    "turmeric": "#d89a24",     # 姜黄色（金色）
    "sambar": "#b85c38",       # 番茄粉（棕色）
    "rose": "#d9718c",         # 玫瑰牛奶
    "marina": "#1e6f8c",       # 海蓝
    "steel": "#596c76",        # 钢铁灰
    "cream": "#f6ecd8",        # 奶油色
    "charcoal": "#1f1b18",     # 木炭色
}

# ============================================================================
# 自定义色阶图 - 用于热力图和评分可视化
# ============================================================================
CHENNAI_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "chennai_spice",
    [PALETTE["cream"], "#f1c46b", PALETTE["turmeric"], PALETTE["sambar"], "#6d2f20", PALETTE["charcoal"]],
)

RATING_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "rating_leaf_gold",
    ["#7a2e22", PALETTE["sambar"], PALETTE["turmeric"], PALETTE["leaf_light"], PALETTE["leaf"]],
)

# ============================================================================
# Matplotlib 全局配置
# ============================================================================
def configure_matplotlib():
    """配置所有matplotlib图表的全局样式"""
    mpl.rcParams.update({
        "figure.facecolor": PALETTE["paper"],
        "axes.facecolor": PALETTE["paper"],
        "savefig.facecolor": PALETTE["paper"],
        "axes.edgecolor": PALETTE["grid"],
        "axes.labelcolor": PALETTE["ink"],
        "xtick.color": PALETTE["muted"],
        "ytick.color": PALETTE["muted"],
        "text.color": PALETTE["ink"],
        "font.family": "SimHei",
        "font.size": 10.5,
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
        "axes.titlepad": 14,
        "axes.grid": True,
        "grid.color": PALETTE["grid"],
        "grid.linewidth": 0.8,
        "grid.alpha": 0.55,
        "legend.frameon": False,
    })

# ============================================================================
# 数据分析常数
# ============================================================================
EXPECTED_COLUMNS = [
    "restaurant", "features", "market_segment", "cuisine", 
    "top_dishes", "address", "area", "latitude", "longitude", 
    "zomato_url", "rating"
]

# 评分分段定义
RATING_BINS = [-np.inf, 2.9, 3.4, 3.8, 4.2, np.inf]
RATING_LABELS = ["fragile", "developing", "solid", "strong", "elite"]

# 本地菜系词汇 (用于识别Chennai特色菜)
LOCAL_DISH_PATTERN = r"filter coffee|pongal|dosa|idli|vada|sambar|rasam|curd rice|biryani"

# ============================================================================
# 数据验证常数
# ============================================================================
MIN_RATING = 0.0
MAX_RATING = 5.0
MIN_CUISINES_TO_SHOW = 30
MIN_DISHES_TO_SHOW = 40
MIN_CHAIN_SIZE = 10
MIN_AREA_SIZE = 25

# ============================================================================
# 可视化参数
# ============================================================================
FIGURE_WIDTH_SINGLE = 14
FIGURE_WIDTH_DOUBLE = 16
FIGURE_HEIGHT_BASE = 8

# 颜色映射 - 按市场细分
SEGMENT_COLORS = {
    "Restaurant": "#2f6b45",      # 叶绿
    "Fast Food": "#d89a24",        # 姜黄
    "Cloud Kitchen": "#1e6f8c",   # 海蓝
    "Hotel": "#b85c38",            # 棕色
    "Cafe": "#d9718c",             # 玫瑰
    "Bakery & Sweet Shop": "#766b60",  # 芝麻
    "Bar": "#596c76",              # 钢铁
    "Ice Cream Parlour": "#8cb369", # 浅绿
}

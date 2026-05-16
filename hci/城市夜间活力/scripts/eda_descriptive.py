"""
上海夜间消费热度 —— 描述性统计分析
输出：
  data/synthetic/figs/  ← 所有图表 PNG（300 dpi）
  data/synthetic/eda_descriptive_report.md  ← 统计摘要文字报告
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── 全局样式 ──────────────────────────────────────────────
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "STHeiti"]
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["figure.dpi"] = 150
matplotlib.rcParams["savefig.dpi"] = 300
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False

PALETTE_CAT  = {"餐饮": "#F4845F", "娱乐": "#7B68EE", "零售": "#5BA4CF"}
PALETTE_DIST = sns.color_palette("muted", 10)
FIG_DIR = "data/synthetic/figs"
os.makedirs(FIG_DIR, exist_ok=True)

# ── 读取数据 ──────────────────────────────────────────────
print("读取数据…")
csv_path = "data/synthetic/shanghai_night_orders.csv"
try:
    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        parse_dates=["order_time"],
    )
except UnicodeDecodeError:
    df = pd.read_csv(
        csv_path,
        encoding="gbk",
        parse_dates=["order_time"],
    )
df["order_amount"] = df["order_amount"].astype(float)
df["rating"]       = df["rating"].astype(float)
df["hour"]         = df["order_time"].dt.hour
df["date"]         = df["order_time"].dt.date
df["hour_ts"]      = df["order_time"].dt.floor("h")
df["weekday"]      = df["order_time"].dt.dayofweek          # 0=周一
df["is_weekend"]   = df["weekday"].isin([4, 5, 6]).astype(int)
df["is_night_core"] = df["hour"].isin([22, 23, 0, 1, 2]).astype(int)
df["poi_name_clean"] = (
    df["poi_name"]
    .str.replace(r"\（.*?\）", "", regex=True)
    .str.replace(r"\(.*?\)", "", regex=True)
    .str.strip()
)

# 统一小时排序（夜间从18时到次日2时）
HOUR_ORDER = [18, 19, 20, 21, 22, 23, 0, 1, 2]
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

print(f"共 {len(df):,} 条记录，{df['poi_id'].nunique()} 个 POI，"
      f"{df['date'].nunique()} 天")


# ════════════════════════════════════════════════════════════
# 0. 核心统计量汇总（写入报告，也打印到控制台）
# ════════════════════════════════════════════════════════════
def fmt_num(x):
    return f"{x:,.2f}" if isinstance(x, float) else f"{x:,}"

stat = df["order_amount"].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99])
rating_stat = df["rating"].describe(percentiles=[0.25, 0.5, 0.75])

report_lines = [
    "# 上海夜间消费热度 — 描述性统计报告\n",
    "## 一、数据集概况\n",
    f"- 订单总量：**{len(df):,}** 条",
    f"- 时间范围：{df['order_time'].min().date()} 至 {df['order_time'].max().date()}（{df['date'].nunique()} 天）",
    f"- POI 数量：{df['poi_id'].nunique()} 个，覆盖 {df['district'].nunique()} 个区",
    f"- 品类：{sorted(df['category_lv1'].unique())}",
    "",
    "## 二、订单金额统计\n",
    f"| 指标 | 数值（元） |",
    f"|------|-----------|",
    f"| 均值 | {stat['mean']:.2f} |",
    f"| 中位数 | {stat['50%']:.2f} |",
    f"| 标准差 | {stat['std']:.2f} |",
    f"| 1% 分位 | {stat['1%']:.2f} |",
    f"| 25% 分位 | {stat['25%']:.2f} |",
    f"| 75% 分位 | {stat['75%']:.2f} |",
    f"| 99% 分位 | {stat['99%']:.2f} |",
    f"| 最大值 | {stat['max']:.2f} |",
    "",
    "## 三、评分统计\n",
    f"| 指标 | 数值 |",
    f"|------|------|",
    f"| 均值 | {rating_stat['mean']:.2f} |",
    f"| 中位数 | {rating_stat['50%']:.2f} |",
    f"| 标准差 | {rating_stat['std']:.2f} |",
    "",
]

# 分品类统计, 到时候可以制作一个饼图
cat_stat = df.groupby("category_lv1")["order_amount"].agg(
    订单量="count", 总消费="sum", 均值="mean", 中位数="median", 标准差="std"
).round(2)
cat_stat["总消费占比(%)"] = (cat_stat["总消费"] / cat_stat["总消费"].sum() * 100).round(1)
report_lines += [
    "## 四、分品类统计\n",
    cat_stat.to_markdown(),
    "",
]

# 分区逐小时消费额（时间序列）
district_hourly = (
    df.groupby(["hour_ts", "district"], as_index=False)["order_amount"]
    .sum()
    .rename(columns={"order_amount": "revenue"})
)
district_hourly_pivot = (
    district_hourly.pivot(index="hour_ts", columns="district", values="revenue")
    .fillna(0)
    .sort_index()
)
district_hourly_path = "data/synthetic/district_hourly_revenue.csv"
district_hourly_pivot.to_csv(district_hourly_path, encoding="utf-8-sig")

report_lines += [
    "## 五、分区逐小时消费额时间序列\n",
    f"- 已生成 CSV：`{district_hourly_path}`（每小时一行，区县为列）",
    "- 预览：",
    district_hourly_pivot.head(12).to_markdown(),
    "",
]

# POI 名称词频统计
poi_word_freq = (
    df["poi_name_clean"]
    .value_counts()
    .rename_axis("poi_name")
    .reset_index(name="count")
)
poi_word_freq_path = "data/synthetic/poi_name_word_freq.csv"
poi_word_freq.to_csv(poi_word_freq_path, index=False, encoding="utf-8-sig")

report_lines += [
    "## 六、POI 名称词频\n",
    f"- 已生成 CSV：`{poi_word_freq_path}`（括号内容已去除）",
    "- TOP20 预览：",
    poi_word_freq.head(20).to_markdown(index=False),
    "",
]

print("\n".join(report_lines[:20]))

# ════════════════════════════════════════════════════════════
# 图1：订单金额分布（直方图 + KDE + 箱线图）
# ════════════════════════════════════════════════════════════
print("图1：订单金额分布…")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("图1  订单金额分布", fontsize=14, fontweight="bold", y=1.01)

# 1a：直方图 + KDE（截断到 500 元以内，更清晰）
ax = axes[0]
sub = df[df["order_amount"] <= 500]["order_amount"]
ax.hist(sub, bins=60, color="#5BA4CF", edgecolor="white", linewidth=0.4, alpha=0.85)
ax2 = ax.twinx()
sub.plot.kde(ax=ax2, color="#E85D5D", linewidth=2)
ax2.set_ylabel("概率密度", fontsize=10, color="#E85D5D")
ax2.tick_params(axis="y", colors="#E85D5D")
ax2.set_ylim(bottom=0)
ax.set_xlabel("订单金额（元）", fontsize=11)
ax.set_ylabel("订单数", fontsize=11)
ax.set_title("金额分布直方图（≤500元，占99%+）", fontsize=11)
# 标注均值/中位数
ax.axvline(stat["mean"],   color="#F4845F", linestyle="--", linewidth=1.5, label=f"均值 {stat['mean']:.1f}")
ax.axvline(stat["50%"], color="#7B68EE", linestyle=":",  linewidth=1.5, label=f"中位数 {stat['50%']:.1f}")
ax.legend(fontsize=9)

# 1b：分品类箱线图
ax = axes[1]
order = ["餐饮", "娱乐", "零售"]
sub2 = df[df["order_amount"] <= 600]
for i, cat in enumerate(order):
    d = sub2[sub2["category_lv1"] == cat]["order_amount"]
    ax.boxplot(d, positions=[i], widths=0.5, patch_artist=True,
               boxprops=dict(facecolor=PALETTE_CAT[cat], alpha=0.7),
               medianprops=dict(color="black", linewidth=2),
               flierprops=dict(marker=".", markersize=2, alpha=0.3),
               whiskerprops=dict(linewidth=1.2),
               capprops=dict(linewidth=1.2))
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(order, fontsize=11)
ax.set_ylabel("订单金额（元）", fontsize=11)
ax.set_title("分品类金额箱线图", fontsize=11)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig01_amount_distribution.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图2：夜间时段订单量与消费额走势（折线图）
# ════════════════════════════════════════════════════════════
print("图2：时段走势…")
hourly = df.groupby("hour").agg(
    订单量=("order_id", "count"),
    消费额均值=("order_amount", "mean"),
    消费额总量=("order_amount", "sum"),
).reindex(HOUR_ORDER)

fig, ax1 = plt.subplots(figsize=(11, 5))
ax2 = ax1.twinx()

x = range(len(HOUR_ORDER))
hour_labels = [str(h) + ":00" for h in HOUR_ORDER]

ax1.bar(x, hourly["订单量"], color="#5BA4CF", alpha=0.6, width=0.6, label="订单量（条）")
ax2.plot(x, hourly["消费额均值"], color="#F4845F", linewidth=2.5,
         marker="o", markersize=6, label="客单价（均值，元）")

ax1.set_xticks(x)
ax1.set_xticklabels(hour_labels, fontsize=10)
ax1.set_xlabel("时段", fontsize=11)
ax1.set_ylabel("订单量（条）", fontsize=11, color="#5BA4CF")
ax1.tick_params(axis="y", colors="#5BA4CF")
ax2.set_ylabel("客单价（元）", fontsize=11, color="#F4845F")
ax2.tick_params(axis="y", colors="#F4845F")

# 夜间核心时段底色
core_x = [HOUR_ORDER.index(h) for h in [22, 23, 0, 1, 2]]
for xi in core_x:
    ax1.axvspan(xi - 0.4, xi + 0.4, color="#FFF3CD", alpha=0.25, zorder=0)
ax1.text(HOUR_ORDER.index(22), hourly["订单量"].max() * 1.02, "夜间核心时段",
         fontsize=9, color="#B8860B")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)
ax1.set_title("图2  夜间各时段订单量与客单价分布", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig02_hourly_trend.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图3：分品类时段订单量对比（折线图）
# ════════════════════════════════════════════════════════════
print("图3：分品类时段对比…")
hourly_cat = df.groupby(["hour", "category_lv1"]).size().unstack(fill_value=0).reindex(HOUR_ORDER)

fig, ax = plt.subplots(figsize=(11, 5))
for cat, color in PALETTE_CAT.items():
    if cat in hourly_cat.columns:
        ax.plot(range(len(HOUR_ORDER)), hourly_cat[cat],
                marker="o", linewidth=2.2, markersize=6,
                color=color, label=cat)
ax.set_xticks(range(len(HOUR_ORDER)))
ax.set_xticklabels([str(h) + ":00" for h in HOUR_ORDER], fontsize=10)
ax.set_ylabel("订单量（条）", fontsize=11)
ax.set_xlabel("时段", fontsize=11)
ax.legend(fontsize=11)
ax.set_title("图3  各品类夜间时段订单量走势对比", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig03_category_hourly.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图4：各区订单量与消费总额（双轴条形图）
# ════════════════════════════════════════════════════════════
print("图4：各区统计…")
dist_agg = df.groupby("district").agg(
    订单量=("order_id", "count"),
    消费总额=("order_amount", "sum"),
).sort_values("消费总额", ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
y = range(len(dist_agg))
bars = ax.barh(y, dist_agg["消费总额"] / 1e4, color=PALETTE_DIST, alpha=0.85, height=0.55)
ax.set_yticks(y)
ax.set_yticklabels(dist_agg.index, fontsize=11)
ax.set_xlabel("消费总额（万元）", fontsize=11)
ax.set_title("图4  各区30日夜间消费总额排名", fontsize=13, fontweight="bold")

# 标注订单量
for bar, (_, row) in zip(bars, dist_agg.iterrows()):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{int(row['订单量']):,}单", va="center", fontsize=9, color="#444")

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig04_district_revenue.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图5：工作日 vs 周末 各时段订单量对比
# ════════════════════════════════════════════════════════════
print("图5：工作日 vs 周末…")
hourly_week = df.groupby(["hour", "is_weekend"]).size().unstack(fill_value=0).reindex(HOUR_ORDER)
hourly_week.columns = ["工作日", "周末"]

fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(HOUR_ORDER))
w = 0.35
ax.bar(x - w/2, hourly_week["工作日"], width=w, color="#5BA4CF", alpha=0.8, label="工作日")
ax.bar(x + w/2, hourly_week["周末"],   width=w, color="#F4845F", alpha=0.8, label="周末")
ax.set_xticks(x)
ax.set_xticklabels([str(h) + ":00" for h in HOUR_ORDER], fontsize=10)
ax.set_ylabel("订单量（条）", fontsize=11)
ax.set_xlabel("时段", fontsize=11)
ax.legend(fontsize=11)
ax.set_title("图5  工作日与周末各时段订单量对比", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig05_weekday_vs_weekend.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图6：支付方式占比（饼图 + 品类堆叠条）
# ════════════════════════════════════════════════════════════
print("图6：支付方式…")
pay_counts = df["payment_type"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("图6  支付方式分布", fontsize=13, fontweight="bold")

# 6a 饼图
ax = axes[0]
colors_pie = ["#5BA4CF", "#F4845F", "#7B68EE", "#5CB85C", "#F0AD4E", "#D9534F"]
wedges, texts, autotexts = ax.pie(
    pay_counts, labels=pay_counts.index,
    autopct="%1.1f%%", startangle=140,
    colors=colors_pie, pctdistance=0.82,
    wedgeprops=dict(linewidth=1, edgecolor="white")
)
for at in autotexts:
    at.set_fontsize(9)
ax.set_title("总体支付方式占比", fontsize=11)

# 6b 分品类支付偏好（百分比堆叠）
ax = axes[1]
pay_cat = df.groupby(["category_lv1", "payment_type"]).size().unstack(fill_value=0)
pay_cat_pct = pay_cat.div(pay_cat.sum(axis=1), axis=0) * 100
pay_cat_pct.plot(kind="bar", stacked=True, ax=ax,
                 color=colors_pie[:len(pay_cat_pct.columns)], alpha=0.85,
                 edgecolor="white", linewidth=0.4)
ax.set_xticklabels(pay_cat_pct.index, rotation=0, fontsize=11)
ax.set_ylabel("占比（%）", fontsize=11)
ax.set_title("分品类支付方式偏好", fontsize=11)
ax.legend(loc="lower right", fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig06_payment.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图7：评分分布（直方图 + 分品类小提琴图）
# ════════════════════════════════════════════════════════════
print("图7：评分分布…")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("图7  用户评分分布", fontsize=13, fontweight="bold")

# 7a 评分直方图
ax = axes[0]
bins = np.arange(1.0, 5.6, 0.1)
ax.hist(df["rating"], bins=bins, color="#7B68EE", edgecolor="white", linewidth=0.3, alpha=0.85)
ax.axvline(df["rating"].mean(), color="#E85D5D", linestyle="--", linewidth=2,
           label=f"均值 {df['rating'].mean():.2f}")
ax.set_xlabel("评分", fontsize=11)
ax.set_ylabel("订单数", fontsize=11)
ax.set_title("评分频率直方图", fontsize=11)
ax.legend(fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 7b 分品类小提琴图
ax = axes[1]
cats_order = ["餐饮", "娱乐", "零售"]
parts = ax.violinplot(
    [df[df["category_lv1"] == c]["rating"].values for c in cats_order],
    positions=[1, 2, 3], showmedians=True, showextrema=True
)
for i, (pc, cat) in enumerate(zip(parts["bodies"], cats_order)):
    pc.set_facecolor(PALETTE_CAT[cat])
    pc.set_alpha(0.7)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(cats_order, fontsize=11)
ax.set_ylabel("评分", fontsize=11)
ax.set_title("分品类评分小提琴图", fontsize=11)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig07_rating_distribution.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图8：二级品类订单量排行（横向条形）
# ════════════════════════════════════════════════════════════
print("图8：二级品类排行…")
cat2_agg = df.groupby(["category_lv2", "category_lv1"]).agg(
    订单量=("order_id", "count"),
    均值=("order_amount", "mean"),
).reset_index().sort_values("订单量", ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))
colors_bar = [PALETTE_CAT[c] for c in cat2_agg["category_lv1"]]
ax.barh(range(len(cat2_agg)), cat2_agg["订单量"],
        color=colors_bar, alpha=0.82, height=0.65)
ax.set_yticks(range(len(cat2_agg)))
ax.set_yticklabels(cat2_agg["category_lv2"], fontsize=10)
ax.set_xlabel("订单量（条）", fontsize=11)
ax.set_title("图8  各二级品类订单量排行", fontsize=13, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 标注客单价
for i, (_, row) in enumerate(cat2_agg.iterrows()):
    ax.text(row["订单量"] + 50, i, f"均值{row['均值']:.0f}元",
            va="center", fontsize=8.5, color="#555")

# 品类图例
from matplotlib.patches import Patch
legend_els = [Patch(facecolor=v, alpha=0.8, label=k) for k, v in PALETTE_CAT.items()]
ax.legend(handles=legend_els, fontsize=10, loc="lower right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig08_category2_rank.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图9：30天日订单量与消费趋势（折线）
# ════════════════════════════════════════════════════════════
print("图9：30天趋势…")
daily = df.groupby("date").agg(
    订单量=("order_id", "count"),
    消费额=("order_amount", "sum"),
).reset_index()
daily["date"] = pd.to_datetime(daily["date"])
daily["weekday_label"] = daily["date"].dt.dayofweek.map(lambda x: WEEKDAY_CN[x])

fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()

ax1.fill_between(daily["date"], daily["订单量"], alpha=0.25, color="#5BA4CF")
ax1.plot(daily["date"], daily["订单量"], color="#5BA4CF", linewidth=2, label="日订单量")
ax2.plot(daily["date"], daily["消费额"] / 1e4, color="#F4845F",
         linewidth=2, linestyle="--", label="日消费额（万元）")

# 标记周末
for _, row in daily.iterrows():
    if row["weekday_label"] in ["周六", "周日"]:
        ax1.axvspan(row["date"] - pd.Timedelta(hours=12),
                    row["date"] + pd.Timedelta(hours=12),
                    color="#FFF3CD", alpha=0.35, zorder=0)

ax1.set_xlabel("日期", fontsize=11)
ax1.set_ylabel("日订单量（条）", fontsize=11, color="#5BA4CF")
ax1.tick_params(axis="y", colors="#5BA4CF")
ax2.set_ylabel("日消费额（万元）", fontsize=11, color="#F4845F")
ax2.tick_params(axis="y", colors="#F4845F")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10)
ax1.set_title("图9  30天日订单量与消费额走势（黄色背景=周末）",
              fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig09_daily_trend.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 图10：订单金额 × 评分散点（抽样5000条，颜色=品类）
# ════════════════════════════════════════════════════════════
print("图10：金额-评分散点…")
sample = df[df["order_amount"] <= 500].sample(5000, random_state=42)

fig, ax = plt.subplots(figsize=(10, 6))
for cat, color in PALETTE_CAT.items():
    sub = sample[sample["category_lv1"] == cat]
    ax.scatter(sub["rating"], sub["order_amount"],
               color=color, alpha=0.28, s=18, label=cat, linewidths=0)

# 各品类回归线
for cat, color in PALETTE_CAT.items():
    sub = sample[sample["category_lv1"] == cat]
    z = np.polyfit(sub["rating"], sub["order_amount"], 1)
    p = np.poly1d(z)
    xs = np.linspace(sub["rating"].min(), sub["rating"].max(), 100)
    ax.plot(xs, p(xs), color=color, linewidth=2, linestyle="--")

ax.set_xlabel("用户评分", fontsize=11)
ax.set_ylabel("订单金额（元）", fontsize=11)
ax.set_title("图10  用户评分与订单金额关系（抽样5000条，虚线为各品类回归线）",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/fig10_rating_vs_amount.png", bbox_inches="tight")
plt.close()

# ════════════════════════════════════════════════════════════
# 写出报告
# ════════════════════════════════════════════════════════════
# 补充分品类时段峰值结论
peak_hour_cat = {}
for cat in ["餐饮", "娱乐", "零售"]:
    sub = df[df["category_lv1"] == cat].groupby("hour").size().reindex(HOUR_ORDER)
    peak_hour_cat[cat] = HOUR_ORDER[sub.argmax()]

weekend_avg = df[df["is_weekend"] == 1].groupby("date")["order_id"].count().mean()
workday_avg = df[df["is_weekend"] == 0].groupby("date")["order_id"].count().mean()
weekend_lift = (weekend_avg - workday_avg) / workday_avg * 100

report_lines += [
    "## 六、关键结论\n",
    f"- **峰值时段**：整体订单峰值出现在 **{HOUR_ORDER[hourly['订单量'].argmax()]}:00**",
    f"- **分品类峰值**：餐饮 {peak_hour_cat['餐饮']}:00，娱乐 {peak_hour_cat['娱乐']}:00，零售 {peak_hour_cat['零售']}:00",
    f"- **周末效应**：周末日均订单量比工作日高 **{weekend_lift:.1f}%**",
    f"- **区域差异**：消费总额最高区为 **{dist_agg.index[-1]}**，最低区为 **{dist_agg.index[0]}**",
    f"- **客单价**：娱乐品类客单价（{df[df['category_lv1']=='娱乐']['order_amount'].mean():.1f}元）> "
    f"餐饮（{df[df['category_lv1']=='餐饮']['order_amount'].mean():.1f}元）> "
    f"零售（{df[df['category_lv1']=='零售']['order_amount'].mean():.1f}元）",
    "",
    "## 七、图表索引\n",
    "| 编号 | 文件名 | 内容 |",
    "|------|--------|------|",
    "| 图1 | fig01_amount_distribution.png | 订单金额直方图+箱线图 |",
    "| 图2 | fig02_hourly_trend.png | 时段订单量与客单价双轴折线 |",
    "| 图3 | fig03_category_hourly.png | 分品类时段走势对比 |",
    "| 图4 | fig04_district_revenue.png | 各区消费总额排名 |",
    "| 图5 | fig05_weekday_vs_weekend.png | 工作日vs周末时段对比 |",
    "| 图6 | fig06_payment.png | 支付方式占比 |",
    "| 图7 | fig07_rating_distribution.png | 评分分布直方图+小提琴图 |",
    "| 图8 | fig08_category2_rank.png | 二级品类订单排行 |",
    "| 图9 | fig09_daily_trend.png | 30天日趋势 |",
    "| 图10 | fig10_rating_vs_amount.png | 评分-金额散点+回归线 |",
]

report_path = "data/synthetic/eda_descriptive_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n全部完成！")
print(f"  图表目录：{FIG_DIR}/")
print(f"  统计报告：{report_path}")

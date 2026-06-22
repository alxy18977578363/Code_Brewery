# -*- coding: utf-8 -*-
"""生成报告用图表 PNG（数据全部来自真实运行）。"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if Path(fp).exists():
        font_manager.fontManager.addfont(fp)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=fp).get_name()]
        break
plt.rcParams["axes.unicode_minus"] = False

EVAL = Path(__file__).resolve().parent
OUT = EVAL / "_figs"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, GREEN, RED, GREY = "#2563eb", "#f59e0b", "#10b981", "#ef4444", "#64748b"

# 1) 抽取对比（compare.py --llm 真实结果）
fields = ["方法\nmethods", "数据集\ndatasets", "指标\nmetrics", "结论\nconclusion"]
rule = [0.795, 0.650, 0.650, 0.806]
llm = [0.186, 0.917, 0.861, 0.819]
x = range(len(fields))
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar([i - 0.2 for i in x], rule, 0.4, label="规则法 (jieba+词典)", color=BLUE)
ax.bar([i + 0.2 for i in x], llm, 0.4, label="LLM 法 (DeepSeek)", color=ORANGE)
ax.set_xticks(list(x)); ax.set_xticklabels(fields)
ax.set_ylabel("F1 / 命中率"); ax.set_ylim(0, 1.05)
ax.set_title("信息抽取：规则法 vs LLM 法（12 条标注样本）")
for i, (r, l) in enumerate(zip(rule, llm)):
    ax.text(i - 0.2, r + 0.02, f"{r:.2f}", ha="center", fontsize=8)
    ax.text(i + 0.2, l + 0.02, f"{l:.2f}", ha="center", fontsize=8)
ax.legend(); fig.tight_layout(); fig.savefig(OUT / "extract_compare.png", dpi=150); plt.close(fig)

# 2) 相关性重排消融（同一组 8 个主流 CS/AI 主题，真实）
stages = ["关闭相关性重排\n(基线)", "开启 IDF\n相关性重排"]
micro = [0.672, 0.710]
fig, ax = plt.subplots(figsize=(5.6, 4))
bars = ax.bar(stages, micro, color=[ORANGE, GREEN], width=0.5)
ax.axhline(0.85, ls="--", color=GREY); ax.text(1.4, 0.86, "目标线 85%", color=GREY, fontsize=9, ha="right")
ax.set_ylabel("主题准确率 (微平均)"); ax.set_ylim(0, 1.0)
ax.set_title("相关性重排消融实验（8 个主流 CS/AI 主题）")
for b, v in zip(bars, micro):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.1%}", ha="center", fontsize=11)
fig.tight_layout(); fig.savefig(OUT / "topic_ablation.png", dpi=150); plt.close(fig)

# 3) 各 CS/AI 主题准确率（真实）
d = json.load(open(EVAL / "_topic_cs.json", encoding="utf-8"))
labels = [r["topic"] for r in d]
accs = [r["acc"] for r in d]
order = sorted(range(len(accs)), key=lambda i: accs[i])
labels = [labels[i] for i in order]; accs = [accs[i] for i in order]
fig, ax = plt.subplots(figsize=(8.5, 4.5))
colors = [GREEN if a >= 0.75 else (ORANGE if a >= 0.55 else RED) for a in accs]
bars = ax.barh(labels, accs, color=colors)
ax.axvline(0.85, ls="--", color=GREY)
ax.set_xlabel("主题准确率"); ax.set_xlim(0, 1.0)
ax.set_title("各主流 CS/AI 主题检索准确率（独立 LLM 裁判，每主题 8 篇）")
for b, v in zip(bars, accs):
    ax.text(v + 0.01, b.get_y() + b.get_height() / 2, f"{v:.0%}", va="center", fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "topic_per.png", dpi=150); plt.close(fig)

# 4) 年份趋势（真实 pipeline run）
run = json.load(open(EVAL / "_pipeline_run.json", encoding="utf-8"))
yt = sorted(run["year_trend"], key=lambda z: int(z[0]))
years = [str(y) for y, _ in yt]; counts = [c for _, c in yt]
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(years, counts, marker="o", color=BLUE, linewidth=2)
ax.set_xlabel("年份"); ax.set_ylabel("论文数")
ax.set_title("「检索增强生成」检索结果年份分布")
ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig(OUT / "year_trend.png", dpi=150); plt.close(fig)

print("charts saved to", OUT)

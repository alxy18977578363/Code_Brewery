"""验证中文主题 → 英文翻译 → arXiv/S2 检索 → 按引用排序 的全链路。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import retrieve
from src.retrieval.translator import translate_query

topic = "大语言模型"
print(f"原始主题：{topic}")
print(f"翻译结果：{translate_query(topic)}")
print()
print("--- 检索 8 篇（min_citations=50 优先核心论文）---")
papers = retrieve(topic, max_results=8, year_from=2020, year_to=2025, min_citations=50)
for i, p in enumerate(papers, 1):
    print(f"  [{i}] ({p.source}/{p.year}) {p.title[:90]}")
    print(f"       venue: {p.venue}")

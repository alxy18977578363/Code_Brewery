"""主题聚类 + 年份趋势。

实现：jieba 分词 → TF-IDF → KMeans。
- 不引入 sentence-transformers（体量大，对一周项目过重），课程报告里可以把"换成 sbert 中文模型"列为未来工作
- 自动选 k：根据样本数给经验值，再用簇内代表关键词当主题标签
"""
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import jieba
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from src.models import Paper, StructuredRecord


def _tokenize(text: str) -> List[str]:
    chinese = sum(1 for c in text if "一" <= c <= "鿿")
    if chinese > 20:
        return [w for w in jieba.cut(text) if len(w.strip()) > 1]
    return [w for w in text.lower().split() if len(w) > 2]


def _pick_k(n: int) -> int:
    if n < 4:
        return 1
    if n < 8:
        return 2
    if n < 15:
        return 3
    if n < 30:
        return 4
    return 5


def cluster_papers(
    papers: List[Paper],
    records: List[StructuredRecord],
    *,
    n_clusters: Optional[int] = None,
) -> Dict:
    """返回 {clusters: [{label, paper_ids, top_terms}], assignments: {paper_id: cluster_idx}}"""
    if not papers:
        return {"clusters": [], "assignments": {}}

    texts = []
    for p in papers:
        texts.append(" ".join(_tokenize(f"{p.title} {p.abstract}")))

    k = n_clusters or _pick_k(len(papers))
    if k <= 1 or len(papers) < 2:
        return {
            "clusters": [{
                "label": "全部文献",
                "paper_ids": [p.paper_id for p in papers],
                "top_terms": _top_terms_from_records(records),
            }],
            "assignments": {p.paper_id: 0 for p in papers},
        }

    vec = TfidfVectorizer(max_features=2000, token_pattern=r"(?u)\b\w+\b")
    X = vec.fit_transform(texts)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    feature_names = np.array(vec.get_feature_names_out())
    clusters: List[dict] = []
    by_cluster: Dict[int, List[str]] = defaultdict(list)
    for pid, lab in zip([p.paper_id for p in papers], labels):
        by_cluster[int(lab)].append(pid)

    for ci in range(k):
        pids = by_cluster.get(ci, [])
        if not pids:
            continue
        # 簇中心的高权重词当主题词
        center = km.cluster_centers_[ci]
        top_idx = center.argsort()[-6:][::-1]
        top_terms = [t for t in feature_names[top_idx].tolist() if t]
        # 优先用记录里的 methods/keywords 来描述主题
        record_terms = _top_terms_from_records(
            [r for r in records if r.paper_id in pids]
        )
        label = "、".join(record_terms[:3]) or "、".join(top_terms[:3]) or f"主题 {ci+1}"
        clusters.append({
            "label": label,
            "paper_ids": pids,
            "top_terms": top_terms,
        })

    assignments = {pid: int(lab) for pid, lab in zip([p.paper_id for p in papers], labels)}
    return {"clusters": clusters, "assignments": assignments}


def _top_terms_from_records(records: List[StructuredRecord], k: int = 8) -> List[str]:
    cnt: Counter = Counter()
    for r in records:
        cnt.update(r.methods)
        cnt.update(r.keywords)
    return [w for w, _ in cnt.most_common(k)]


def year_trend(papers: List[Paper]) -> List[Tuple[int, int]]:
    cnt: Counter = Counter()
    for p in papers:
        if p.year:
            cnt[p.year] += 1
    return sorted(cnt.items())


def trend_analysis(
    records: List[StructuredRecord],
    *,
    top_methods: int = 6,
    top_rank: int = 10,
    hot_top: int = 8,
    recent_span: int = 2,
) -> Dict:
    """基于抽取结果做"学术分析"，比单纯词云更有信息量。返回四块数据：

    - methods_over_time: 主流方法（按总频次取前 top_methods 个）逐年出现次数，画多折线
    - dataset_rank:      数据集出现频次排行 Top top_rank
    - metric_rank:       评价指标出现频次排行 Top top_rank
    - hot_methods:       近 recent_span 年的热点方法 Top hot_top

    频次按"论文计数"：同一篇论文里重复出现的同名方法只计一次（用 set 去重）。
    """
    method_cnt: Counter = Counter()
    dataset_cnt: Counter = Counter()
    metric_cnt: Counter = Counter()
    for r in records:
        method_cnt.update({m for m in r.methods if m})
        dataset_cnt.update({d for d in r.datasets if d})
        metric_cnt.update({x for x in r.metrics if x})

    years = sorted({r.year for r in records if r.year})

    # 主流方法逐年演变：取总频次最高的若干方法，统计它们在每个年份的论文数
    top_method_names = [m for m, _ in method_cnt.most_common(top_methods)]
    method_year: Dict[str, Counter] = {m: Counter() for m in top_method_names}
    for r in records:
        if not r.year:
            continue
        for m in {m for m in r.methods if m in method_year}:
            method_year[m][r.year] += 1
    methods_over_time = {
        "years": years,
        "series": [
            s for s in (
                {"name": m, "counts": [method_year[m].get(y, 0) for y in years]}
                for m in top_method_names
            ) if sum(s["counts"]) > 0  # 跳过全为 0 的方法（其论文都缺年份），避免画出平直零线
        ],
    }

    dataset_rank = [{"name": d, "count": c} for d, c in dataset_cnt.most_common(top_rank)]
    metric_rank = [{"name": x, "count": c} for x, c in metric_cnt.most_common(top_rank)]

    # 近 recent_span 年热点方法：以数据中的最新年份为基准向前取窗口
    hot_methods: List[dict] = []
    recent_years: List[int] = []
    if years:
        cutoff = max(years) - (recent_span - 1)
        recent_years = [cutoff, max(years)]
        hot_cnt: Counter = Counter()
        for r in records:
            if r.year and r.year >= cutoff:
                hot_cnt.update({m for m in r.methods if m})
        hot_methods = [{"name": m, "count": c} for m, c in hot_cnt.most_common(hot_top)]

    return {
        "methods_over_time": methods_over_time,
        "dataset_rank": dataset_rank,
        "metric_rank": metric_rank,
        "hot_methods": hot_methods,
        "recent_years": recent_years,
    }

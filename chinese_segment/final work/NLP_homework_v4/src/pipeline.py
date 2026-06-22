"""把检索、抽取、聚类、综述串成一条 pipeline。

这就是"作业思路"里说的 agent 雏形——固定流程编排，每步输出可见。
报告里可以以此为基础讨论"如何升级为可自主决策的版本"（例如让 LLM 决定是否扩大检索）。
"""
import logging
import math
import re
import time
import concurrent.futures
from collections import Counter
from typing import Callable, Dict, List, Optional

from src.clustering import cluster_papers, year_trend, trend_analysis
from src.extraction import LLMExtractor, RuleBasedExtractor
from src.extraction.base import BaseExtractor
from src.models import Paper, StructuredRecord
from src.retrieval import dedup_by_title, search_arxiv, search_semantic_scholar
from src.retrieval.translator import has_chinese, translate_query
from src.retrieval.enricher import enrich_papers, enrich_full_text_only
from src.review import generate_review

logger = logging.getLogger(__name__)

# 主题准确率的关键：检索 API 按宽松词面相关性返回，常把"词碰巧相同但主题不符"的论文
# 混进来（如搜"中文命名实体识别"却返回孟加拉语 NER）。这里做一道相关性重排过滤：
# 用 IDF 给查询词加权——区分度高的限定词（如 chinese）权重大，通用词（如 recognition）
# 权重小；论文必须覆盖足够的"高权重词"才算切题。这样能滤掉只命中通用词的离题论文。
# 只过滤真正的功能词。像 neural/network/model/learning 这类词是否有区分度，交给 IDF
# 自动判断（在结果池里普遍出现 → 权重自然低），不再硬编码删除，否则 "graph neural
# network" 会被删到只剩 "graph" 而无法重排。
_RERANK_STOP = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "via",
    "using", "based", "towards", "from", "by", "at", "as", "is", "are",
}


def _query_terms(query: str) -> List[str]:
    terms, seen = [], set()
    for t in re.split(r"[^a-z0-9]+", query.lower()):
        if len(t) >= 3 and t not in _RERANK_STOP and t not in seen:
            seen.add(t)
            terms.append(t)
    return terms


def _rerank_by_relevance(papers: List[Paper], query: str, *, threshold: float = 0.34,
                         keep_min: int = 3) -> List[Paper]:
    """按 IDF 加权的查询词覆盖度对检索结果重排并过滤离题论文。

    评分：score(p) = Σ_{词∈查询∩论文} idf(词) · 字段权重(标题=2, 摘要=1)，
    再除以查询全部词的 idf 总质量，得到 0~1 的"重要词覆盖率"。
    覆盖率 < threshold 视为离题剔除；但至少保留 keep_min 篇（按分数高的留），避免空结果。
    查询词过少（如纯通用词）时不过滤，避免误伤。
    """
    terms = _query_terms(query)
    if len(terms) < 2 or not papers:
        return papers

    n = len(papers)
    docs = [f"{p.title} {p.title} {p.abstract}".lower() for p in papers]  # 标题计两次≈加权
    title_low = [p.title.lower() for p in papers]
    # 文档频率 → IDF
    df = {t: sum(1 for d in docs if t in d) for t in terms}
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in terms}
    total_mass = sum(idf.values()) or 1.0

    scored = []
    for p, d, tl in zip(papers, docs, title_low):
        s = 0.0
        for t in terms:
            if t in d:
                s += idf[t] * (2.0 if t in tl else 1.0)
        # 分母用 2×总质量（假设全部命中且都在标题时为满分），归一到 0~1 附近
        scored.append((p, s / (total_mass * 1.5)))

    scored.sort(key=lambda x: x[1], reverse=True)
    kept = [p for p, sc in scored if sc >= threshold]
    if len(kept) < keep_min:
        kept = [p for p, _ in scored[:keep_min]]
    dropped = n - len(kept)
    if dropped:
        logger.info("相关性重排：从 %d 篇中剔除 %d 篇离题论文（阈值 %.2f）", n, dropped, threshold)
    return kept


def _get_extractor(method: str) -> BaseExtractor:
    if method == "llm":
        return LLMExtractor()
    return RuleBasedExtractor()


def retrieve(
    topic: str,
    *,
    max_results: int = 12,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sources: Optional[List[str]] = None,
    min_citations: int = 10,
) -> List[Paper]:
    """检索流程：
    1. 若主题含中文，先翻译成英文检索词（arXiv 不认中文）
    2. arXiv 只用英文查询；S2 同时用中英文两路查询
    3. S2 按引用数排序过滤低质量论文，但近 2 年的新论文豁免引用门槛
       （否则前沿工作会因引用未攒够被整体排除）
    4. 跨源去重
    """
    sources = sources or ["arxiv", "semantic_scholar"]
    per_source = max(max_results, 5)
    found: List[Paper] = []

    en_query = translate_query(topic) if has_chinese(topic) else topic

    if "arxiv" in sources:
        try:
            found += search_arxiv(en_query, max_results=per_source, year_from=year_from, year_to=year_to)
        except Exception as e:
            logger.warning("arXiv 检索失败：%s", e)

    if "semantic_scholar" in sources:
        # 英文查询：优先核心论文
        try:
            found += search_semantic_scholar(
                en_query, max_results=per_source,
                year_from=year_from, year_to=year_to,
                min_citations=min_citations,
            )
        except Exception as e:
            logger.warning("Semantic Scholar 英文检索失败：%s", e)
        # 若原查询是中文，再补一次中文查询（找中文综述类论文，不设引用门槛）
        if has_chinese(topic) and topic != en_query:
            try:
                found += search_semantic_scholar(
                    topic, max_results=max(per_source // 2, 3),
                    year_from=year_from, year_to=year_to,
                )
            except Exception as e:
                logger.warning("Semantic Scholar 中文检索失败：%s", e)

    deduped = dedup_by_title(found)
    # 相关性重排过滤：剔除"词面相同但主题不符"的离题论文，提升主题准确率
    reranked = _rerank_by_relevance(deduped, en_query)
    return reranked[:max_results]


def extract_all(
    papers: List[Paper],
    method: str = "rule",
    *,
    progress: Optional[Callable[[int, int], None]] = None,
) -> List[StructuredRecord]:
    extractor = _get_extractor(method)
    if method == "llm":
        out = [None] * len(papers)
        completed = 0
        from config import DEEPSEEK_API_KEYS
        workers = min(20, 5 * max(1, len(DEEPSEEK_API_KEYS)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_idx = {executor.submit(extractor.extract, p): i for i, p in enumerate(papers)}
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                out[idx] = future.result()
                completed += 1
                if progress:
                    progress(completed, len(papers))
        return out
    else:
        out = []
        for i, p in enumerate(papers, 1):
            out.append(extractor.extract(p))
            if progress:
                progress(i, len(papers))
        return out


def keyword_cloud(records: List[StructuredRecord], top: int = 50) -> List[dict]:
    cnt: Counter = Counter()
    for r in records:
        cnt.update(r.keywords)
        cnt.update(r.methods)
    return [{"text": w, "weight": c} for w, c in cnt.most_common(top) if w]


def run_full_pipeline(
    topic: str,
    *,
    max_results: int = 12,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    method: str = "rule",
    deep_read: bool = False,
) -> Dict:
    log: List[str] = []
    t0 = time.time()

    def stage(msg: str):
        log.append(f"[{time.time() - t0:.1f}s] {msg}")
        logger.info(msg)

    stage(f"开始：主题=「{topic}」, 方法={method}, 最大{max_results}篇")

    if has_chinese(topic):
        en = translate_query(topic)
        stage(f"中文主题已翻译为英文检索词：「{en}」")

    pool_size = max_results * 3
    papers = retrieve(topic, max_results=pool_size, year_from=year_from, year_to=year_to)
    stage(f"初筛检索完成：共 {len(papers)} 篇候选文献")

    # 并发补充代码链接和图片（此时不抓取全文，节省时间）
    papers = enrich_papers(papers, fetch_full=False)
    
    # 按 GitHub Stars 降序排序，如果有 Stars 就会排到最前面
    papers.sort(key=lambda p: p.github_stars, reverse=True)
    
    # 截断取前 max_results 篇
    papers = papers[:max_results]
    stage(f"按 Github Stars 排序并截断至 {len(papers)} 篇（最高 Star：{papers[0].github_stars if papers else 0}）")

    if deep_read:
        stage("正在并发获取排名前列文献的全文用于精读...")
        enrich_full_text_only(papers)
        stage("全文获取完成")

    records = extract_all(papers, method=method)
    stage(f"抽取完成：{len(records)} 条结构化记录（{method}）")

    clusters = cluster_papers(papers, records)
    stage(f"聚类完成：{len(clusters['clusters'])} 个主题")

    trend = year_trend(papers)
    cloud = keyword_cloud(records)
    analytics = trend_analysis(records)

    review = generate_review(papers, records, clusters)
    stage(f"综述完成：{'降级版' if review['fallback'] else 'LLM 版'}，"
          f"有效引用 {len(review['citations_used'])} 个，越界引用 {len(review['hallucinated_citations'])} 个，"
          f"疑似张冠李戴 {len(review.get('unsupported_claims', []))} 处")
    stage(f"演进图时间校验：修正 {len(review.get('mermaid_time_issues', []))} 处时间错误")

    return {
        "topic": topic,
        "method": method,
        "papers": [p.to_dict() for p in papers],
        "records": [r.to_dict() for r in records],
        "clusters": clusters,
        "year_trend": trend,
        "keyword_cloud": cloud,
        "analytics": analytics,
        "review": review,
        "log": log,
    }

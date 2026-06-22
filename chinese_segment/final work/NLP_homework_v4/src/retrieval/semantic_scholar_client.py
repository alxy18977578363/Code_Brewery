"""Semantic Scholar Graph API 客户端。返回 JSON。"""
import datetime
from typing import List, Optional

import requests

from config import SEMANTIC_SCHOLAR_API_KEY
from src.models import Paper

S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "paperId,title,abstract,authors,year,venue,url,citationCount,influentialCitationCount"

_NO_PROXY = {"http": "", "https": ""}


def search_semantic_scholar(
    query: str,
    *,
    max_results: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_citations: int = 0,
    recent_grace_years: int = 2,
    timeout: int = 30,
) -> List[Paper]:
    # 多取一些再按引用次数挑高质量
    params = {
        "query": query,
        "limit": min(max(max_results * 4, 20), 100),
        "fields": FIELDS,
    }
    if year_from or year_to:
        lo = year_from or ""
        hi = year_to or ""
        params["year"] = f"{lo}-{hi}"
    # 注意：不再用服务端 minCitationCount 硬过滤。它会把近一两年还没攒够引用的
    # 新论文整体排除，导致"前沿综述"拿不到最新工作。改为下方客户端"近年豁免"软过滤。

    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    import os
    proxies = None if os.getenv("USE_PROXY_FOR_RETRIEVAL") == "1" else _NO_PROXY
    resp = requests.get(S2_API, params=params, headers=headers, timeout=timeout, proxies=proxies)
    if resp.status_code == 429:
        return []
    resp.raise_for_status()

    raw_items = []
    for item in resp.json().get("data", []):
        abstract = item.get("abstract") or ""
        if not abstract:
            continue
        raw_items.append(item)

    # 引用门槛的"近年豁免"软过滤：
    #   旧论文需引用 >= min_citations 才保留（过滤低质量长尾）；
    #   近 recent_grace_years 年内的新论文一律豁免（引用还没攒够，但可能是前沿工作）。
    if min_citations > 0:
        recent_cutoff = datetime.date.today().year - recent_grace_years
        kept = [
            it for it in raw_items
            if (it.get("citationCount") or 0) >= min_citations
            or (it.get("year") or 0) >= recent_cutoff
        ]
        # 若全被滤掉（例如冷门主题），回退为不过滤，保证有结果可展示
        raw_items = kept or raw_items

    # 排序：引用数降序优先核心论文，但把近年新论文的"等效引用"抬到至少 min_citations，
    # 避免最新工作被排到末尾后在截断时丢失。
    recent_cutoff = datetime.date.today().year - recent_grace_years

    def _rank_key(it):
        cc = it.get("citationCount") or 0
        icc = it.get("influentialCitationCount") or 0
        is_recent = (it.get("year") or 0) >= recent_cutoff
        eff = max(cc, min_citations) if is_recent else cc
        return (eff, icc, cc)

    raw_items.sort(key=_rank_key, reverse=True)

    papers: List[Paper] = []
    for item in raw_items[:max_results]:
        cc = item.get("citationCount") or 0
        venue = item.get("venue") or ""
        venue_str = f"{venue} · 引用 {cc}" if venue else f"引用 {cc}"
        papers.append(
            Paper(
                paper_id=f"s2:{item['paperId']}",
                title=(item.get("title") or "").strip(),
                abstract=item["abstract"].strip(),
                authors=[a.get("name", "") for a in item.get("authors", [])],
                year=item.get("year"),
                venue=venue_str,
                url=item.get("url") or "",
                source="semantic_scholar",
            )
        )
    return papers

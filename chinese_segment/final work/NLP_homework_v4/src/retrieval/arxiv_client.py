"""arXiv API 客户端。返回 Atom XML，用 feedparser 解析。"""
from typing import List, Optional

import feedparser
import requests

from src.models import Paper

ARXIV_API = "http://export.arxiv.org/api/query"

# arXiv / S2 是公网学术 API，国内可直连。若用户机器上有本地代理（V2ray/Clash 等），
# 走代理反而会触发 503/超时。默认绕过代理，可通过环境变量 USE_PROXY_FOR_RETRIEVAL=1 强制走代理。
_NO_PROXY = {"http": "", "https": ""}


def search_arxiv(
    query: str,
    *,
    max_results: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    timeout: int = 30,
) -> List[Paper]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    import os
    proxies = None if os.getenv("USE_PROXY_FOR_RETRIEVAL") == "1" else _NO_PROXY
    resp = requests.get(ARXIV_API, params=params, timeout=timeout, proxies=proxies)
    resp.raise_for_status()

    feed = feedparser.parse(resp.text)
    papers: List[Paper] = []
    for entry in feed.entries:
        year = None
        if getattr(entry, "published_parsed", None):
            year = entry.published_parsed.tm_year
        if year_from and year and year < year_from:
            continue
        if year_to and year and year > year_to:
            continue

        paper_id = entry.id.split("/")[-1] if hasattr(entry, "id") else entry.link
        papers.append(
            Paper(
                paper_id=f"arxiv:{paper_id}",
                title=(entry.title or "").replace("\n", " ").strip(),
                abstract=(entry.summary or "").replace("\n", " ").strip(),
                authors=[a.name for a in getattr(entry, "authors", [])],
                year=year,
                venue="arXiv",
                url=entry.link,
                source="arxiv",
            )
        )
    return papers

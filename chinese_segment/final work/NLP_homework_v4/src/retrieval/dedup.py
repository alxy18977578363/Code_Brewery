"""按归一化标题跨源去重。"""
import re
from typing import List

from src.models import Paper

_NORM = re.compile(r"[\s\W_]+", re.UNICODE)


def _norm_title(t: str) -> str:
    return _NORM.sub("", t.lower())


def dedup_by_title(papers: List[Paper]) -> List[Paper]:
    seen = set()
    out: List[Paper] = []
    for p in papers:
        key = _norm_title(p.title)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out

from .arxiv_client import search_arxiv
from .semantic_scholar_client import search_semantic_scholar
from .dedup import dedup_by_title

__all__ = ["search_arxiv", "search_semantic_scholar", "dedup_by_title"]

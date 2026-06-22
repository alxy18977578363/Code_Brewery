"""验证 arXiv / Semantic Scholar 网络可达性。"""
import os
import sys

import requests

print("HTTP_PROXY =", os.environ.get("HTTP_PROXY"))
print("HTTPS_PROXY =", os.environ.get("HTTPS_PROXY"))
print()

print("--- arXiv ---")
try:
    r = requests.get(
        "http://export.arxiv.org/api/query",
        params={"search_query": "all:BERT", "max_results": 3},
        timeout=20,
    )
    print("status:", r.status_code, "bytes:", len(r.text))
    print("head:", r.text[:200].replace("\n", " "))
except Exception as e:
    print("error:", type(e).__name__, e)

print()
print("--- Semantic Scholar ---")
try:
    r = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": "BERT", "limit": 3, "fields": "title,year"},
        timeout=20,
    )
    print("status:", r.status_code)
    print("body:", r.text[:300])
except Exception as e:
    print("error:", type(e).__name__, e)

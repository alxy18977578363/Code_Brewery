"""绕过代理测试。"""
import requests

print("--- arXiv 直连（不走代理）---")
try:
    r = requests.get(
        "http://export.arxiv.org/api/query",
        params={"search_query": "all:BERT", "max_results": 3},
        timeout=30,
        proxies={"http": "", "https": ""},
    )
    print("status:", r.status_code, "bytes:", len(r.text))
except Exception as e:
    print("error:", type(e).__name__, e)

print()
print("--- arXiv 走代理（http 不升级）---")
try:
    r = requests.get(
        "http://export.arxiv.org/api/query",
        params={"search_query": "all:BERT", "max_results": 3},
        timeout=30,
    )
    print("status:", r.status_code, "bytes:", len(r.text))
except Exception as e:
    print("error:", type(e).__name__, e)

"""读取最近一次 pipeline 输出并打印摘要。"""
import json
import sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/Users/33432/AppData/Local/Temp/pipeline_out.json")
d = json.loads(p.read_text(encoding="utf-8"))

print("papers:", len(d.get("papers", [])))
print("records:", len(d.get("records", [])))
print("clusters:", len(d.get("clusters", {}).get("clusters", [])))
print("cloud size:", len(d.get("keyword_cloud", [])))
print("year_trend:", d.get("year_trend"))
print("review fallback:", d.get("review", {}).get("fallback"))
print("--- log ---")
for x in d.get("log", []):
    print(" ", x)

ps = d.get("papers", [])
if ps:
    print("\n--- first 3 papers ---")
    for p in ps[:3]:
        print(f"  [{p['source']}/{p.get('year')}] {p['title'][:80]}")

rs = d.get("records", [])
if rs:
    r = rs[0]
    print(f"\n--- first record extraction ---")
    print(f"  methods:    {r.get('methods', [])[:6]}")
    print(f"  datasets:   {r.get('datasets', [])}")
    print(f"  metrics:    {r.get('metrics', [])}")
    print(f"  keywords:   {r.get('keywords', [])[:6]}")
    print(f"  conclusion: {(r.get('conclusion', '') or '')[:120]}")

cls = d.get("clusters", {}).get("clusters", [])
if cls:
    print(f"\n--- clusters ---")
    for i, c in enumerate(cls):
        print(f"  [{i+1}] {c.get('label')}  ({len(c.get('paper_ids', []))} papers)")
        print(f"      terms: {c.get('top_terms', [])[:6]}")

print("\nerror:", d.get("error", "(none)"))

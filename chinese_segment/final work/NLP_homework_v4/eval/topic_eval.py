"""论文主题相关性（主题准确率）评测。

对应作业性能要求：**论文主题准确率不低于 85%**。

口径
----
对每个测试主题跑一次检索，逐篇判定返回的论文是否真的与主题相关，
    主题准确率 = 相关论文数 / 返回论文总数
再对所有主题求平均，与 85% 的及格线比较。

两种判定方式
-----------
- 规则判定（默认，无需 key）：把主题（中文先翻成英文检索词）切成关键词，
  与论文"标题 + 摘要"做词重叠，命中足够多的关键词即判为相关。
- LLM 判定（--llm，需配置 DEEPSEEK_API_KEY）：让 DeepSeek 逐篇回答"是否属于该主题"。
  更接近人工标注，**写报告建议用这一种作为正式数据**，规则判定作为无 key 时的快速自检。

用法
----
    python eval/topic_eval.py                 # 规则判定，默认主题集
    python eval/topic_eval.py --llm           # LLM 判定
    python eval/topic_eval.py --llm --rank    # 写报告推荐：LLM 判定 + 产品口径取数
    python eval/topic_eval.py --max 10        # 每个主题取前 10 篇
    python eval/topic_eval.py --topics "大语言模型 思维链推理" "knowledge graph embedding"

--rank：按产品真实口径取数（检索 3 倍候选 → 补全代码/Star → 按 Star 降序 → 截断），
即用户在页面上实际看到的论文集合；不加则用原始检索结果（更快，偏保守）。
"""
import argparse
import concurrent.futures
import io
import re
import sys
from pathlib import Path
from typing import List

# Windows 控制台默认 GBK，强制 UTF-8 输出避免中文乱码
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import llm_available  # noqa: E402
from src.models import Paper  # noqa: E402
from src.pipeline import retrieve  # noqa: E402
from src.retrieval.enricher import enrich_papers  # noqa: E402
from src.retrieval.translator import has_chinese, translate_query  # noqa: E402

PASS_LINE = 0.85

# 默认主题集：覆盖中英文、奠基工作与前沿方向，贴近课程 NLP 场景
DEFAULT_TOPICS = [
    "大语言模型 思维链推理",
    "检索增强生成",
    "中文命名实体识别",
    "对比学习 句向量",
    "retrieval augmented generation",
]

# 英文停用词 + 检索常见无区分度词，避免它们被当成主题关键词
_STOP = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "with", "via",
    "using", "based", "model", "models", "method", "methods", "approach", "learning",
    "deep", "neural", "network", "networks", "system", "task", "tasks", "study",
}


def _topic_terms(topic: str) -> List[str]:
    """把主题转成英文关键词列表（中文主题先翻译，与检索时同一套词）。"""
    en = translate_query(topic) if has_chinese(topic) else topic
    terms = [t for t in re.split(r"[^A-Za-z0-9]+", en.lower()) if len(t) >= 3 and t not in _STOP]
    # 去重保序
    seen, out = set(), []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def rule_relevant(terms: List[str], paper: Paper) -> bool:
    """规则判定：论文标题+摘要命中的主题关键词数达到阈值即判相关。

    阈值取 max(1, ceil(关键词数 * 0.4))——主题往往是多词组合，
    命中近一半核心词就足以认定切题；只命中一个泛词不算。
    """
    if not terms:
        return True
    text = f"{paper.title} {paper.abstract}".lower()
    hits = sum(1 for t in terms if t in text)
    need = max(1, (len(terms) * 2 + 4) // 5)  # ceil(n*0.4)
    return hits >= need


_LLM_SYS = (
    "你是学术检索相关性判别器。给定一个研究主题和一篇论文的标题与摘要，"
    "判断这篇论文是否确实属于该主题（而非仅有个别词碰巧相同）。"
    "只输出一个字符：相关输出 1，不相关输出 0，不要任何解释。"
)


def llm_relevant(topic: str, paper: Paper) -> bool:
    from src.llm.deepseek_client import chat, DeepSeekError
    user = (
        f"研究主题：{topic}\n\n"
        f"论文标题：{paper.title}\n"
        f"论文摘要：{paper.abstract[:1200]}\n\n"
        "这篇论文是否属于该主题？只回 1 或 0。"
    )
    try:
        out = chat(
            [{"role": "system", "content": _LLM_SYS}, {"role": "user", "content": user}],
            temperature=0.0, max_tokens=128,  # 部分模型需先消耗推理 token 才吐出结果，给足额度
        )
    except DeepSeekError:
        return False  # 判别失败按不相关计，宁可低估不虚高
    digits = re.findall(r"[01]", out)
    return bool(digits) and digits[-1] == "1"  # 取最终给出的判定（1=相关）


def _ranked_retrieve(topic: str, max_results: int) -> List[Paper]:
    """复刻 run_full_pipeline 的取数口径：3 倍候选 → 补全代码/Star → 按 Star 降序 → 截断。

    这才是用户在页面上真正看到的论文集合，比原始检索更贴近"产品主题准确率"。
    """
    pool = retrieve(topic, max_results=max_results * 3)
    pool = enrich_papers(pool, fetch_full=False)
    pool.sort(key=lambda p: p.github_stars, reverse=True)
    return pool[:max_results]


def eval_topic(topic: str, *, use_llm: bool, max_results: int, rank: bool = False) -> dict:
    papers = _ranked_retrieve(topic, max_results) if rank else retrieve(topic, max_results=max_results)
    if not papers:
        return {"topic": topic, "n": 0, "relevant": 0, "acc": None, "details": []}

    if use_llm:
        flags = [False] * len(papers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            fut = {ex.submit(llm_relevant, topic, p): i for i, p in enumerate(papers)}
            for f in concurrent.futures.as_completed(fut):
                flags[fut[f]] = f.result()
    else:
        terms = _topic_terms(topic)
        flags = [rule_relevant(terms, p) for p in papers]

    rel = sum(flags)
    details = [(p.title[:60], ok) for p, ok in zip(papers, flags)]
    return {"topic": topic, "n": len(papers), "relevant": rel,
            "acc": rel / len(papers), "details": details}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="用 DeepSeek 逐篇判定相关性（更准，需 key）")
    ap.add_argument("--max", type=int, default=8, help="每个主题检索的论文数")
    ap.add_argument("--rank", action="store_true",
                    help="按产品口径取数（3 倍候选→补全代码/Star→按 Star 排序→截断），更贴近用户实际所见")
    ap.add_argument("--topics", nargs="*", help="自定义主题集，默认用内置 5 个")
    ap.add_argument("--verbose", action="store_true", help="打印每篇论文的判定结果")
    args = ap.parse_args()

    use_llm = args.llm
    if use_llm and not llm_available():
        print("[警告] 未配置 DEEPSEEK_API_KEY，自动改用规则判定")
        use_llm = False

    topics = args.topics or DEFAULT_TOPICS
    judge = "LLM 判定 (DeepSeek)" if use_llm else "规则判定 (关键词重叠)"
    source = "产品口径(Star 排序)" if args.rank else "原始检索"
    print(f"主题准确率评测 · {judge} · 取数={source} · 每主题取前 {args.max} 篇 · 及格线 {PASS_LINE:.0%}\n")

    results = []
    for t in topics:
        r = eval_topic(t, use_llm=use_llm, max_results=args.max, rank=args.rank)
        results.append(r)
        if r["acc"] is None:
            print(f"  ✗ 「{t}」检索为空（可能网络不通或被限流），跳过")
            continue
        mark = "✔" if r["acc"] >= PASS_LINE else "✘"
        print(f"  {mark} 「{t}」 {r['relevant']}/{r['n']} = {r['acc']:.1%}")
        if args.verbose:
            for title, ok in r["details"]:
                print(f"        [{'相关' if ok else '不相关'}] {title}")

    scored = [r for r in results if r["acc"] is not None]
    if not scored:
        print("\n没有可评测的主题（检索全部为空）。检查网络/代理设置后重试。")
        return

    # 总体口径：把所有主题的论文汇总后算微平均，更贴近"整体准确率"
    total_n = sum(r["n"] for r in scored)
    total_rel = sum(r["relevant"] for r in scored)
    micro = total_rel / total_n
    macro = sum(r["acc"] for r in scored) / len(scored)

    print(f"\n=== 汇总（{len(scored)} 个主题，共 {total_n} 篇）===")
    print(f"  微平均准确率（按论文汇总）: {micro:.1%}")
    print(f"  宏平均准确率（按主题平均）: {macro:.1%}")
    verdict = "达标 ✔" if micro >= PASS_LINE else "未达标 ✘"
    print(f"  对照及格线 {PASS_LINE:.0%}：{verdict}")


if __name__ == "__main__":
    main()

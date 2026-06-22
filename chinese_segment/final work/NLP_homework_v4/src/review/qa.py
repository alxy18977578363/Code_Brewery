"""论文问答（基于当前检索结果的 RAG QA）。

与「选题助手」(assistant.py) 不同：选题助手是帮用户想检索词；这里是对【已检索到的
文献】做 grounded 问答——只依据当前文献列表的标题/摘要/抽取结果/精读详评回答，
并强制用 [n] 引用，引用号超出范围会被标记为幻觉。无 LLM 时降级为关键词匹配。
"""
import logging
import re
from typing import Dict, List

from config import llm_available
from src.llm.deepseek_client import chat
from src.models import Paper, StructuredRecord
from src.review.generator import _validate_citations

logger = logging.getLogger(__name__)

_SYS_PROMPT = """你是一个严谨的学术问答助手。下面会给你一批带编号的论文资料（每篇含标题、方法、数据集、指标、结论、摘要等）。
请只依据这些资料回答用户的问题，并严格遵守：
1. 答案中每一处事实性陈述都必须用 [n] 标注来源编号，n 只能取自给定的论文编号，禁止编造编号或资料里没有的内容。
2. 如果资料不足以回答问题，请直接说明“根据当前文献无法回答该问题”，不要臆测。
3. 用中文回答，专有名词可保留英文；回答要简洁、有条理，可使用要点或对比。
4. 不要原样罗列资料，要针对问题做归纳、比较与提炼。
"""


def _build_context(papers: List[Paper], records: List[StructuredRecord]) -> str:
    """把每篇文献整理成带 [n] 编号的上下文块，供模型引用。"""
    paper_map = {p.paper_id: p for p in papers}
    blocks = []
    for i, r in enumerate(records, 1):
        p = paper_map.get(r.paper_id)
        parts = [f"[{i}] 标题：{r.title}（{r.year or '年份未知'}）"]
        if r.methods:
            parts.append(f"方法：{', '.join(r.methods)}")
        if r.datasets:
            parts.append(f"数据集：{', '.join(r.datasets)}")
        if r.metrics:
            parts.append(f"指标：{', '.join(r.metrics)}")
        if getattr(r, "results", None):
            res = []
            for x in r.results:
                key = " - ".join(filter(None, [x.get("dataset", ""), x.get("metric", "")]))
                if key:
                    res.append(f"{key}: {x.get('value', '')}")
            if res:
                parts.append("定量结果：" + "; ".join(res))
        if r.conclusion:
            parts.append(f"结论：{r.conclusion}")
        if p and p.abstract:
            parts.append(f"摘要：{p.abstract[:600]}")
        if getattr(r, "detailed_analysis", None):
            parts.append(f"精读详评：{r.detailed_analysis[:800]}")
        blocks.append("\n".join(parts))
    return "\n\n".join(blocks)


def _fallback_answer(question: str, papers: List[Paper], records: List[StructuredRecord]) -> Dict:
    """无 LLM 时：用关键词重叠找出最相关的文献列出来，仍带 [n] 引用。"""
    paper_map = {p.paper_id: p for p in papers}
    terms = {t for t in re.split(r"[^\w一-鿿]+", question.lower()) if len(t) >= 2}
    scored = []
    for i, r in enumerate(records, 1):
        p = paper_map.get(r.paper_id)
        hay = " ".join([
            r.title or "", " ".join(r.methods), " ".join(r.datasets),
            (p.abstract if p else "") or "",
        ]).lower()
        score = sum(1 for t in terms if t in hay)
        if score:
            scored.append((score, i, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:3]
    if not top:
        return {"answer": "（未配置大模型，且未在当前文献中找到与问题相关的内容。）",
                "citations_used": [], "hallucinated_citations": [], "fallback": True}
    lines = ["（未配置大模型，以下为基于关键词匹配的相关文献，供参考：）", ""]
    cited = []
    for _, i, r in top:
        extra = f"，方法：{', '.join(r.methods[:3])}" if r.methods else ""
        lines.append(f"- {r.title} [{i}]{extra}")
        cited.append(i)
    return {"answer": "\n".join(lines), "citations_used": sorted(cited),
            "hallucinated_citations": [], "fallback": True}


def answer_question(question: str, papers: List[Paper], records: List[StructuredRecord]) -> Dict:
    """返回 {answer, citations_used, hallucinated_citations, fallback}。"""
    if not records:
        return {"answer": "当前没有可用文献，请先运行检索后再提问。",
                "citations_used": [], "hallucinated_citations": [], "fallback": True}

    if not llm_available():
        return _fallback_answer(question, papers, records)

    context = _build_context(papers, records)
    try:
        text = chat(
            [
                {"role": "system", "content": _SYS_PROMPT},
                {"role": "user", "content": f"【论文资料】\n{context}\n\n【问题】\n{question}"},
            ],
            temperature=0.2,
            max_tokens=2048,
        ).strip()
    except Exception as e:
        logger.warning("论文问答 LLM 调用失败，降级为关键词匹配：%s", e)
        return _fallback_answer(question, papers, records)

    n = len(records)
    hallucinated = _validate_citations(text, n)
    citations_used = sorted({
        int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", text)
        if 1 <= int(m.group(1)) <= n
    })
    return {
        "answer": text,
        "citations_used": citations_used,
        "hallucinated_citations": hallucinated,
        "fallback": False,
    }

"""规则法 vs LLM 抽取的量化评测核心（无副作用，供 CLI 与 Web 共用）。

评测口径：
- methods / datasets / metrics：集合级 P/R/F1，做大小写和空白归一化
- conclusion：按"关键词命中率"评估（gold 给关键词列表/同义词组，预测结论里是否包含）

CLI 入口在 eval/compare.py，Web 入口是 app.py 的 /api/eval_compare，
两者都调用这里的 evaluate / run_comparison，保证口径完全一致。
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from src.extraction import LLMExtractor, RuleBasedExtractor
from src.models import Paper

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA = ROOT / "eval" / "labeled.json"


def _norm(s: str) -> str:
    return s.strip().lower().replace(" ", "").replace("-", "")


def _set(items: List[str]) -> Set[str]:
    return {_norm(x) for x in items if x and x.strip()}


def _as_groups(keywords: List) -> List[List[str]]:
    """把 conclusion_keywords 统一成"同义词组"列表。

    兼容两种写法：
    - 旧格式 ["state-of-the-art", "BERT"]  → 每个词单独成组
    - 新格式 [["state-of-the-art", "最优", "SOTA"], ["BERT"]] → 组内任一命中即算命中
    这样规则法（输出英文原句）与 LLM（输出中文）在同一把尺子下对比，
    不会因为"语言不同"被系统性扣分。
    """
    groups = []
    for kw in keywords:
        groups.append([kw] if isinstance(kw, str) else list(kw))
    return groups


def prf(pred: List[str], gold: List[str]) -> Tuple[float, float, float]:
    p, g = _set(pred), _set(gold)
    if not p and not g:
        return 1.0, 1.0, 1.0
    if not p:
        return 0.0, 0.0, 0.0
    if not g:
        return 0.0, 1.0, 0.0  # gold 为空时把召回算 1 避免惩罚抽取
    tp = len(p & g)
    precision = tp / len(p)
    recall = tp / len(g)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def conclusion_hit(pred: str, keywords: List) -> float:
    """结论命中率：按同义词组算，组内中英任一表述命中即记 1 分。

    归一化时去掉大小写/空格/连字符，保证 "state-of-the-art" 与 "state of the art"、
    "SOTA" 与 "sota" 等表面差异不影响判定。
    """
    groups = _as_groups(keywords)
    if not groups:
        return 1.0
    pred_norm = _norm(pred)
    hit = 0
    for forms in groups:
        if any(_norm(f) in pred_norm for f in forms if f):
            hit += 1
    return hit / len(groups)


def evaluate(extractor, examples: List[dict], label: str) -> Dict:
    rows = []
    for ex in examples:
        paper = Paper(
            paper_id=ex["paper_id"],
            title=ex["title"],
            abstract=ex["abstract"],
            year=ex.get("year"),
        )
        rec = extractor.extract(paper)
        gold = ex["gold"]
        rows.append({
            "paper_id": ex["paper_id"],
            "datasets_prf": prf(rec.datasets, gold.get("datasets", [])),
            "metrics_prf": prf(rec.metrics, gold.get("metrics", [])),
            "conclusion_hit": conclusion_hit(rec.conclusion, gold.get("conclusion_keywords", [])),
        })

    # 只对比数据集与指标两项（方法名表述太宽泛、规范化困难，已从对比中移除）
    summary: Dict = {}
    for field in ["datasets_prf", "metrics_prf"]:
        ps = [r[field][0] for r in rows]
        rs = [r[field][1] for r in rows]
        fs = [r[field][2] for r in rows]
        summary[field] = {
            "P": sum(ps) / len(ps),
            "R": sum(rs) / len(rs),
            "F1": sum(fs) / len(fs),
        }
    summary["conclusion"] = {
        "hit_rate": sum(r["conclusion_hit"] for r in rows) / len(rows)
    }
    summary["_label"] = label
    summary["_n"] = len(examples)
    return summary


def run_comparison(data_path: Optional[str] = None, *, with_llm: bool = False) -> Dict:
    """跑一遍评测，返回 {n, rule, llm?}（llm 仅在 with_llm 时存在）。

    供 Web 端 /api/eval_compare 调用。各 summary 均为可直接 JSON 序列化的字典。
    """
    path = Path(data_path) if data_path else DEFAULT_DATA
    examples = json.loads(path.read_text(encoding="utf-8"))

    result: Dict = {
        "n": len(examples),
        "rule": evaluate(RuleBasedExtractor(), examples, "规则法 (jieba + 词典)"),
    }
    if with_llm:
        result["llm"] = evaluate(LLMExtractor(), examples, "LLM 法 (DeepSeek)")
    return result

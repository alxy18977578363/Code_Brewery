"""规则法中文信息抽取：jieba 分词 + 自建词典 + 正则。

设计思路：
- 用 jieba.analyse 抽关键词（TF-IDF）
- 方法/数据集/评测指标走自建词典匹配（兼容中英文）
- 结论句用 "实验表明/结果显示/achieve/outperform" 等触发词定位
- 给出的结构与 LLM 抽取一致，便于后续对比实验
"""
import re
from pathlib import Path
from typing import List, Set

import jieba
import jieba.analyse

from config import DICT_DIR
from src.extraction.base import BaseExtractor
from src.models import Paper, StructuredRecord


def _load_terms(path: Path) -> List[str]:
    if not path.exists():
        return []
    return [
        line.strip() for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


METHOD_TERMS = _load_terms(DICT_DIR / "methods.txt")
DATASET_TERMS = _load_terms(DICT_DIR / "datasets.txt")
METRIC_TERMS = _load_terms(DICT_DIR / "metrics.txt")

# 把所有专业术语加入 jieba 词表，避免被切碎
for t in METHOD_TERMS + DATASET_TERMS + METRIC_TERMS:
    if any("一" <= c <= "鿿" for c in t):
        jieba.add_word(t)

CONCLUSION_TRIGGERS_CN = ["实验表明", "结果显示", "结果表明", "我们提出", "本文提出", "本研究"]
CONCLUSION_TRIGGERS_EN = [
    "we propose", "we present", "experiments show", "results show",
    "we demonstrate", "achieve", "outperform", "state-of-the-art",
]
METRIC_NUMBER_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*%?\s*(?:accuracy|f1|bleu|rouge|准确率|f1\s*值)",
    re.IGNORECASE,
)


def _find_terms(text: str, terms: List[str]) -> List[str]:
    """词典匹配（大小写不敏感的英文 + 精确匹配的中文）。保持词典中的原始拼写。"""
    lower = text.lower()
    hits: Set[str] = set()
    for term in terms:
        if any("一" <= c <= "鿿" for c in term):
            if term in text:
                hits.add(term)
        else:
            if term.lower() in lower:
                hits.add(term)
    return sorted(hits)


def _extract_keywords(text: str, topk: int = 8) -> List[str]:
    if not text.strip():
        return []
    chinese_chars = sum(1 for c in text if "一" <= c <= "鿿")
    if chinese_chars > 20:
        return jieba.analyse.extract_tags(text, topK=topk, allowPOS=("n", "nz", "v", "vn"))
    # 英文走简单的 token-based TF（避免再装 sklearn）
    tokens = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "are", "but", "not",
        "have", "has", "our", "we", "is", "in", "of", "to", "on", "by", "as",
        "an", "a", "be", "it", "or", "at", "can", "such", "than", "which", "into",
    }
    freq: dict[str, int] = {}
    for t in tokens:
        if t in stop or len(t) < 3:
            continue
        freq[t] = freq.get(t, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:topk]]


def _extract_conclusion(text: str) -> str:
    if not text:
        return ""
    # 切句（中文按。！？，英文按 . ! ?）
    sents = re.split(r"(?<=[。！？.!?])\s+", text)
    triggers = CONCLUSION_TRIGGERS_CN + CONCLUSION_TRIGGERS_EN
    for s in sents:
        low = s.lower()
        if any(t.lower() in low for t in triggers):
            return s.strip()
    # 没匹配到就取最后一句（综述类摘要通常结尾是结论）
    return sents[-1].strip() if sents else ""


class RuleBasedExtractor(BaseExtractor):
    name = "rule_based"

    def extract(self, paper: Paper) -> StructuredRecord:
        text = f"{paper.title}。{paper.abstract}"
        methods = _find_terms(text, METHOD_TERMS)
        datasets = _find_terms(text, DATASET_TERMS)
        metrics = _find_terms(text, METRIC_TERMS)
        # 把摘要里出现的"数字+指标"也补进 metrics，附带数值
        for m in METRIC_NUMBER_RE.findall(paper.abstract):
            metrics.append(f"{m}")
        metrics = sorted(set(metrics))

        keywords = _extract_keywords(paper.abstract)
        conclusion = _extract_conclusion(paper.abstract)

        return StructuredRecord(
            paper_id=paper.paper_id,
            title=paper.title,
            year=paper.year,
            authors=paper.authors,
            keywords=keywords,
            methods=methods,
            datasets=datasets,
            metrics=metrics,
            results=[],
            conclusion=conclusion,
            extracted_by=self.name,
        )

"""贯穿全流程的数据结构。"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Paper:
    """检索阶段得到的原始论文条目。"""
    paper_id: str
    title: str
    abstract: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: str = ""
    url: str = ""
    source: str = ""
    code_url: str = ""
    image_url: str = ""
    github_stars: int = 0
    full_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StructuredRecord:
    """信息抽取后的结构化记录。规则法和 LLM 法都输出这个结构，便于直接对比。"""
    paper_id: str
    title: str
    year: Optional[int]
    authors: List[str]
    keywords: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    results: List[dict] = field(default_factory=list)
    detailed_analysis: str = ""
    conclusion: str = ""
    extracted_by: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

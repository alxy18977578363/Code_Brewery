"""LLM 抽取：用 DeepSeek 做结构化抽取，输出与规则法一致的字段。

关键点：
- 强制 JSON 输出，字段对齐 StructuredRecord
- prompt 用中文写，要求模型即使输入是英文摘要也输出中文术语（便于评审）
- 单条调用一次，方便后续做对比；如果要省 token 可批量但格式更难控
"""
import logging
from typing import List

from src.extraction.base import BaseExtractor
from src.llm.deepseek_client import chat_json, DeepSeekError
from src.models import Paper, StructuredRecord

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一名中文文献信息抽取助手。任务：从给定论文标题、摘要以及部分正文中抽取结构化信息。

要求：
1. 严格输出 JSON，字段固定如下：
   - keywords: 关键词列表（3-8 个，强制使用英文专业术语）
   - methods: 使用或提出的方法/模型/技术（强制使用英文，如"Self-Attention", "BERT", "Contrastive Learning"）
   - datasets: 出现的数据集名称（强制使用英文）
   - metrics: 评测指标（强制使用英文，如"F1", "BLEU", "Accuracy"）
   - results: 定量评测结果的数组，必须包含具体数值，例如 [{"dataset": "GLUE", "metric": "Accuracy", "value": "89.5%"}]。如果没有数值则返回空数组 []
   - detailed_analysis: 一篇至少300字的详细长篇解析，涵盖：研究背景、核心创新点、实验设计、主要结论与未来展望等。请使用 Markdown 格式排版以增加可读性。如果没有足够的信息（例如只输入了短摘要），则尽可能详尽地概括。
   - conclusion: 一句话核心结论或贡献
2. 若某字段在原文中没有明确出现，对于列表型字段请返回空列表 []，对于 detailed_analysis 和 conclusion 请尽力分析，不要编造具体数值。
3. 用中文写 conclusion 和 detailed_analysis，即使摘要是英文。
"""


class LLMExtractor(BaseExtractor):
    name = "llm_deepseek"

    def extract(self, paper: Paper) -> StructuredRecord:
        user_prompt = (
            f"标题：{paper.title}\n"
            f"摘要：{paper.abstract}\n\n"
        )
        if getattr(paper, "full_text", ""):
            user_prompt += f"部分正文内容：\n{paper.full_text[:40000]}\n\n"
        user_prompt += "请根据上述内容进行抽取并严格输出 JSON。"
        try:
            data = chat_json(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=2500,
                timeout=240,
            )
        except DeepSeekError as e:
            logger.warning("LLM 抽取失败 %s: %s", paper.paper_id, e)
            return StructuredRecord(
                paper_id=paper.paper_id,
                title=paper.title,
                year=paper.year,
                authors=paper.authors,
                extracted_by=f"{self.name}:error",
            )

        return StructuredRecord(
            paper_id=paper.paper_id,
            title=paper.title,
            year=paper.year,
            authors=paper.authors,
            keywords=_as_list(data.get("keywords")),
            methods=_as_list(data.get("methods")),
            datasets=_as_list(data.get("datasets")),
            metrics=_as_list(data.get("metrics")),
            results=data.get("results") if isinstance(data.get("results"), list) else [],
            detailed_analysis=str(data.get("detailed_analysis") or "").strip(),
            conclusion=str(data.get("conclusion") or "").strip(),
            extracted_by=self.name,
        )


def _as_list(v) -> List[str]:
    if not v:
        return []
    if isinstance(v, str):
        return [v]
    return [str(x).strip() for x in v if str(x).strip()]

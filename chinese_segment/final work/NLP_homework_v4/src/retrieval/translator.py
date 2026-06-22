"""查询关键词翻译。

中文主题对国际学术库（arXiv / S2）几乎搜不到核心论文，需要先把中文术语翻译成
英文检索词。优先用 LLM 翻译（语义准确），LLM 不可用时退回到一个小术语表。
"""
import logging
import re

from config import llm_available
from src.llm.deepseek_client import chat, DeepSeekError

logger = logging.getLogger(__name__)

# LLM 不可用时的应急映射，只覆盖最常见的几个 NLP 术语
_FALLBACK_TABLE = {
    "大语言模型": "large language model",
    "大模型": "large language model",
    "预训练": "pretraining",
    "微调": "fine-tuning",
    "命名实体识别": "named entity recognition",
    "关系抽取": "relation extraction",
    "信息抽取": "information extraction",
    "情感分析": "sentiment analysis",
    "文本分类": "text classification",
    "机器翻译": "machine translation",
    "问答系统": "question answering",
    "对话系统": "dialogue system",
    "知识图谱": "knowledge graph",
    "检索增强": "retrieval augmented generation",
    "强化学习": "reinforcement learning",
    "对比学习": "contrastive learning",
    "迁移学习": "transfer learning",
    "少样本": "few-shot",
    "零样本": "zero-shot",
    "提示学习": "prompt learning",
    "思维链": "chain of thought",
    "注意力机制": "attention mechanism",
    "神经网络": "neural network",
    "深度学习": "deep learning",
    "智能体": "agent",
    "多智能体": "multi-agent",
}


def has_chinese(s: str) -> bool:
    return bool(re.search(r"[一-鿿]", s))


def translate_query(query: str) -> str:
    """中文查询 → 英文检索词。已是英文则原样返回。"""
    if not has_chinese(query):
        return query

    if llm_available():
        try:
            text = chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "You translate a Chinese research topic into English academic search "
                            "keywords. Preserve EVERY key concept and qualifier in the topic — "
                            "especially language/domain modifiers (e.g. 'Chinese') and the specific "
                            "object of study (e.g. 'sentence embedding'). Do NOT over-summarize or "
                            "drop any word. Output ONLY lowercase English keywords separated by "
                            "spaces (up to 8 words), no punctuation, no explanation, no quotes."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                temperature=0.0,
                max_tokens=128,  # 该模型需先消耗推理 token，额度给足以免返回空串
            )
            cleaned = re.sub(r"[^a-zA-Z0-9\s\-]", " ", text).strip()
            cleaned = re.sub(r"\s+", " ", cleaned).lower()
            if cleaned:
                logger.info("查询翻译：「%s」 → 「%s」", query, cleaned)
                return cleaned
        except DeepSeekError as e:
            logger.warning("LLM 翻译失败，退回到术语表：%s", e)

    # 退回到术语表
    parts = []
    remaining = query
    for cn, en in sorted(_FALLBACK_TABLE.items(), key=lambda x: -len(x[0])):
        if cn in remaining:
            parts.append(en)
            remaining = remaining.replace(cn, " ")
    leftover = re.findall(r"[A-Za-z][A-Za-z\-]+", remaining)
    parts.extend(w.lower() for w in leftover)
    return " ".join(parts) if parts else query

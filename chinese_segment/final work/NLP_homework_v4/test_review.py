import os
from config import llm_available
from src.llm.deepseek_client import chat

SYSTEM_PROMPT = """你是一名中文学术综述写作助手。请基于给定的论文列表（每篇都带有编号、标题、方法、结论、以及精读详评等信息），
撰写一份结构化的中文文献综述。

输出结构（必须包含以下小节，用 ## 作为标题）：
## 研究背景
## 主要方法分类
## 各类方法对比
## 研究空白
## 未来方向

硬性要求：
1. 所有事实性陈述必须用 [n] 形式引用编号（n 取自论文列表，不得编造编号）
2. 不引入未在论文列表里出现的方法名、数据集名或结论
3. 全程使用中文，专有名词保留英文
4. 总长度 800-1500 字。如果论文信息丰富，请务必详细论述，避免空泛。
5. 【重要】如果提供的文献带有【定量结果】或【详评】，请务必在对比章节充分引用具体的数值（如准确率、F1分数）、数据集对比、以及模型创新和局限性细节，让综述更具专业深度。
6. 必须在最后附加一段 Mermaid 格式的图表代码（以 ```mermaid 开头），用于描述论文中涉及算法的演进路线（例如按年份或技术继承关系）。
7. 【致命要求】Mermaid 图表的节点文本中严禁包含未转义的特殊字符（如括号、连字符、引号等），必须严格使用 `id["节点文本"]` 的格式包裹（例如：`A["Transformer 2017"] --> B["BERT"]`），否则会导致渲染引擎崩溃！
"""

user_prompt = """以下是 1 篇论文及其抽取结果，请基于这些撰写综述：

[1] Large Language Models
    年份: 2024; 方法: Transformer
    数据集: Text
    结论: It is good.
    详评: This is a very detailed analysis of the paper...
"""

import json
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

payload = {
    "model": DEEPSEEK_MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ],
    "temperature": 0.4,
    "max_tokens": 2000,
}
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json",
}
url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"

print("Sending request...")
resp = requests.post(url, headers=headers, json=payload, timeout=60)
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Done, saved to output.txt")

"""综述生成。

可追溯引用是评分点。这里的做法：
1. prompt 里给每篇论文配 [n] 编号，只允许引用这些编号
2. 模型输出后，正则扫所有 [n]，超出范围的引用号当作幻觉报错
3. 如果 LLM 不可用，给一个降级版（基于规则的拼接），不让前端崩
"""
import logging
import re
from typing import Dict, List, Optional

from config import llm_available
from src.llm.deepseek_client import chat, DeepSeekError
from src.models import StructuredRecord, Paper

logger = logging.getLogger(__name__)

import concurrent.futures

def _run_planner_agent(papers: List[Paper], records: List[StructuredRecord], clusters: Optional[Dict]) -> List[dict]:
    lines = []
    for i, (p, r) in enumerate(zip(papers, records), 1):
        abstract_snippet = p.abstract[:300].replace('\n', ' ') if p.abstract else "无摘要"
        lines.append(
            f"[{i}] 标题: {p.title}\n"
            f"    年份: {r.year or '未知'}; 方法: {', '.join(r.methods) or '未提取'}\n"
            f"    摘要: {abstract_snippet}...\n"
        )
    metadata_text = "\n".join(lines)
    
    sys_prompt = """你是一个综述规划大纲的 Planner Agent。
任务：根据给定的论文列表（含摘要和方法），输出一个 JSON 数组作为综述大纲。
必须输出合法的 JSON 数组，每个元素包含：
- "heading": 章节标题（例如：研究背景、主要方法分类、各类方法对比、研究空白、未来方向等）
- "intent": 本章节写作意图说明
- "paper_ids": 本章节需要重点引用的论文编号列表（例如 [1, 2, 5]）

注意：
- 第一个章节通常是"研究背景"或"引言"。
- 最后一个章节通常是"未来方向"或"总结"。
- 根据文献主题，合理将相关文献分配到大纲各章节中，不要全部堆在同一章。
"""
    try:
        from src.llm.deepseek_client import chat_json
        outline = chat_json(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": metadata_text}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        if not isinstance(outline, list):
            raise DeepSeekError("Planner 未返回 JSON 数组")
        return outline
    except Exception as e:
        logger.warning(f"Planner 运行失败: {e}")
        return [
            {"heading": "研究背景", "intent": "介绍领域背景", "paper_ids": list(range(1, len(records)+1))},
            {"heading": "方法与对比", "intent": "核心方法对比", "paper_ids": list(range(1, len(records)+1))},
            {"heading": "未来方向", "intent": "总结与展望", "paper_ids": []},
        ]

def _run_writer_agent(section: dict, records: List[StructuredRecord]) -> str:
    heading = section.get("heading", "章节")
    intent = section.get("intent", "无")
    pids = section.get("paper_ids", [])
    
    context_lines = []
    for pid in pids:
        if 1 <= pid <= len(records):
            r = records[pid-1]
            details = f"详评: {r.detailed_analysis}" if getattr(r, "detailed_analysis", None) else ""
            res_text = ""
            if getattr(r, "results", None):
                res_list = []
                for res in r.results:
                    dataset = res.get("dataset", "")
                    metric = res.get("metric", "")
                    val = res.get("value", "")
                    k = " - ".join(filter(None, [dataset, metric]))
                    if k:
                        res_list.append(f"{k}: {val}")
                if res_list:
                    res_text = f"定量结果: {'; '.join(res_list)}"
            context_lines.append(
                f"[{pid}] {r.title}\n结论: {r.conclusion}\n{res_text}\n{details}\n"
            )
            
    context = "\n".join(context_lines) if context_lines else "（该章节无特别指定的局部文献上下文，请结合常识简要泛谈）"
    
    sys_prompt = f"""你是一名综述章节的 Writer Agent。
当前正在撰写的章节：## {heading}
写作意图：{intent}

硬性要求：
1. 请参考下方提供的局部文献上下文进行撰写，不可编造不在列表中的信息。
2. 必须用 [n] 形式引用提到的事实，严禁张冠李戴。
3. 若上下文中提供了【定量结果】或【详评】，务必引用具体的数值和深入细节，凸显专业性。
4. 全程使用中文。不要输出额外的客套话或多余的 Markdown 语法，直接输出该小节的正文。
5. 长度控制在 200-400 字，要求逻辑连贯。
"""
    try:
        from src.llm.deepseek_client import chat
        text = chat(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"文献上下文：\n{context}"}
            ],
            temperature=0.4,
            max_tokens=2048
        )
        return f"## {heading}\n{text.strip()}\n"
    except Exception as e:
        logger.warning(f"Writer 运行失败: {e}")
        return f"## {heading}\n（撰写失败）\n"

def _run_mermaid_agent(records: List[StructuredRecord]) -> str:
    lines = []
    for i, r in enumerate(records, 1):
        lines.append(f"[{i}] {r.title} - 年份:{r.year} - 方法:{', '.join(r.methods)}")
    
    sys_prompt = """你是一个专门生成算法演进图的 Mermaid Agent。
请根据下方提供的论文年份和方法，生成一段 Mermaid 流程图代码（graph LR）。
要求：
1. 只能使用 id["文本"] 的格式，严禁出现未转义的括号或连字符。
2. 按时间递增或技术继承的合理逻辑顺序连接。
3. 只输出 ```mermaid ... ``` 代码块，不输出其他任何废话！
"""
    try:
        from src.llm.deepseek_client import chat
        text = chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": "\n".join(lines)}
        ], temperature=0.1, max_tokens=1024)
        
        mermaid_match = re.search(r"```[mM]ermaid\s*\n?(.*?)\n?```", text, re.DOTALL)
        if mermaid_match:
            return mermaid_match.group(1).strip()
        fallback_match1 = re.search(r"```\s*\n?((?:graph|flowchart) (?:TD|LR|TB|RL|BT).*?)\n?```", text, re.DOTALL)
        if fallback_match1:
            return fallback_match1.group(1).strip()
    except Exception as e:
        logger.warning(f"Mermaid Agent 运行失败: {e}")
    return ""


def _validate_citations(text: str, n: int) -> List[int]:
    """返回引用编号超出 [1..n] 范围的列表（疑似幻觉）。"""
    nums = [int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", text)]
    return sorted({x for x in nums if x < 1 or x > n})


def _has_cjk(s: str) -> bool:
    return any("一" <= c <= "鿿" for c in s)





def _build_fallback_mermaid(records: List[StructuredRecord]) -> str:
    """LLM 没吐出演进图时，用抽取到的"方法+年份"确定性地拼一张演进图。

    保证前端永远有图可渲染，不再出现"演进图突然消失"。
    节点严格用 id["文本"] 格式包裹，避免特殊字符让 mermaid 渲染崩溃。
    """
    seen: set = set()
    nodes: List = []
    for r in sorted(records, key=lambda x: (x.year or 0)):
        if not r.year:
            continue
        for m in (r.methods or []):
            key = (m or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            nodes.append((r.year, m.strip()))
            break  # 每篇只取一个代表方法，控制节点数量
    nodes = nodes[:8]
    if len(nodes) < 2:
        return ""

    lines = ["graph LR"]
    ids: List[str] = []
    for i, (yr, m) in enumerate(nodes):
        nid = f"N{i}"
        safe = re.sub(r'["\[\]()|]', " ", m).strip()
        lines.append(f'    {nid}["{safe} {yr}"]')
        ids.append(nid)
    for a, b in zip(ids, ids[1:]):
        lines.append(f"    {a} --> {b}")
    return "\n".join(lines)


_YEAR_RE = re.compile(r"(?:19|20)\d{2}")


def _authoritative_years(records: List[StructuredRecord]) -> Dict[str, int]:
    """方法名（小写）→ 年份，作为校正演进图节点年份的权威依据。

    依据来自抽取结果里每篇论文的 methods + year，比 LLM 在图里随手写的年份可信。
    同名方法保留最早出现的年份（演进图关心的是"何时提出"）。
    """
    table: Dict[str, int] = {}
    for r in records:
        if not r.year:
            continue
        for m in (r.methods or []):
            k = (m or "").strip().lower()
            if len(k) >= 2:
                table[k] = min(table.get(k, r.year), r.year)
    return table


def _parse_mermaid(code: str):
    """解析 mermaid 流程图，返回 (header, nodes{id:label}, order[id], edges[(a,b)])。

    兼容两种写法：节点单独声明 `N0["BERT 2018"]`，或在边里内联 `A["x"] --> B["y"]`。
    只处理本项目 prompt/兜底会产出的 graph/flowchart 语法，遇到无法解析的返回空结构。
    """
    header_match = re.match(r"((?:graph|flowchart)\s+\w+)", code.strip())
    header = header_match.group(1) if header_match else "graph LR"

    nodes: Dict[str, str] = {}
    order: List[str] = []
    node_re = re.compile(r'([A-Za-z0-9_]+)\s*\[\s*"([^"]*)"\s*\]')
    for m in node_re.finditer(code):
        nid, label = m.group(1), m.group(2).strip()
        if nid not in nodes:
            order.append(nid)
        nodes[nid] = label

    # 去掉节点标签，得到只剩 id 与箭头的骨架，避免标签里的字符干扰边解析
    skeleton = node_re.sub(lambda m: m.group(1), code)
    skeleton = re.sub(r'([A-Za-z0-9_]+)\s*\[[^\]]*\]', lambda m: m.group(1), skeleton)

    edges: List = []
    edge_re = re.compile(r"([A-Za-z0-9_]+)\s*[-.=]+>\s*(?:\|[^|]*\|\s*)?([A-Za-z0-9_]+)")
    for m in edge_re.finditer(skeleton):
        a, b = m.group(1), m.group(2)
        edges.append((a, b))
        for nid in (a, b):
            if nid not in nodes:
                nodes[nid] = nid
                order.append(nid)
    return header, nodes, order, edges


def _node_year(label: str, year_table: Dict[str, int]):
    """返回 (权威年份 or None, 标签里写的年份 or None)。"""
    low = label.lower()
    auth = None
    best_len = 0
    for term, yr in year_table.items():  # 取最长匹配，避免 "gan" 命中 "organ"
        if term in low and len(term) > best_len:
            auth, best_len = yr, len(term)
    m = _YEAR_RE.search(label)
    literal = int(m.group(0)) if m else None
    return auth, literal


def _render_mermaid(header: str, nodes: Dict[str, str], order: List[str], edges: List) -> str:
    lines = [header]
    for nid in order:
        label = nodes.get(nid, nid)
        safe = re.sub(r'["\[\]()|]', " ", label).strip()
        lines.append(f'    {nid}["{safe}"]')
    seen = set()
    for a, b in edges:
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        lines.append(f"    {a} --> {b}")
    return "\n".join(lines)


def _validate_and_fix_mermaid(code: str, records: List[StructuredRecord]):
    """校验并修正演进图里的"时间错误"，返回 (修正后的 code, 问题列表)。

    对应作业性能要求「算法演进图无明显时间错误」。两类时间错误：
    1. 节点标注的年份与抽取到的论文年份不符 → 用权威年份改写标签
    2. 箭头方向把"晚→早"画反了（如 BERT 2018 → Transformer 2017）→ 调换方向
    只有真正发生修改时才重建图并返回问题列表，否则原样返回。
    """
    if not code or not code.strip():
        return code, []
    try:
        header, nodes, order, edges = _parse_mermaid(code)
    except Exception:  # 解析失败就别冒险改图，原样返回
        return code, []
    if len(nodes) < 2 or not edges:
        return code, []

    year_table = _authoritative_years(records)
    issues: List[str] = []
    node_year: Dict[str, int] = {}
    changed = False

    for nid in order:
        label = nodes[nid]
        auth, literal = _node_year(label, year_table)
        node_year[nid] = auth if auth is not None else literal
        if auth is not None and literal is not None and auth != literal:
            new_label = _YEAR_RE.sub(str(auth), label, count=1)
            if new_label != label:
                issues.append(f"节点年份修正：「{label}」→「{new_label}」（抽取年份为 {auth}）")
                nodes[nid] = new_label
                changed = True
        elif auth is not None and literal is None:
            nodes[nid] = f"{label} {auth}"
            issues.append(f"节点补全年份：「{label}」→「{nodes[nid]}」")
            changed = True

    fixed_edges: List = []
    for a, b in edges:
        ya, yb = node_year.get(a), node_year.get(b)
        if ya is not None and yb is not None and ya > yb:
            issues.append(
                f"时间倒置修正：「{nodes.get(a, a)}」→「{nodes.get(b, b)}」方向颠倒，已调换为按年份递增"
            )
            a, b = b, a
            changed = True
        fixed_edges.append((a, b))

    if not changed:
        return code, []
    return _render_mermaid(header, nodes, order, fixed_edges), issues


def _check_grounding(text: str, records: List[StructuredRecord]) -> List[dict]:
    """使用专用 Agent 检验学术综述中是否存在“张冠李戴”事实幻觉。"""
    from src.llm.deepseek_client import chat_json
    
    context_lines = []
    for i, r in enumerate(records, 1):
        methods = ", ".join(r.methods) if getattr(r, "methods", None) else "无"
        datasets = ", ".join(r.datasets) if getattr(r, "datasets", None) else "无"
        context_lines.append(f"[{i}] {r.title} | 方法: {methods} | 数据集: {datasets}")
        
    context = "\n".join(context_lines)
    
    sys_prompt = """你是一个专门检验学术综述中是否存在“张冠李戴”事实幻觉的专家 Agent。
你的任务是对照给定的【论文方法与数据集列表】，逐句核查【综述草稿】中带有 [n] 引用的句子。
如果发现某句话中提到了一种具体的方法、模型或数据集，但这篇 [n] 对应的论文并没有提出或使用它，这就是“张冠李戴”幻觉。

请返回一个合法的 JSON 数组，每个元素包含：
- "snippet": 包含幻觉的句子片段
- "terms": 句中错误归属的具体术语列表（例如 ["Qwen-Image-VAE"]）
- "cited": 该句所引用的论文编号数组（例如 [8]）

注意：如果经过核查，你没有发现任何张冠李戴的幻觉，请务必直接返回空数组 []，绝对不能为了凑字数而强行编造问题！
"""
    try:
        issues = chat_json(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"【论文方法与数据集列表】\n{context}\n\n【综述草稿】\n{text}"}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        if not isinstance(issues, list):
            return []
        return issues
    except Exception as e:
        logger.warning(f"Grounding Agent 运行失败: {e}")
        return []


def _fallback_review(records: List[StructuredRecord]) -> str:
    """LLM 不可用时的降级方案：按规则拼出一份草稿。不算综述，但保证前端能跑。"""
    lines = ["## 研究背景", "本综述基于检索得到的相关文献，自动梳理研究脉络。"]

    lines.append("\n## 主要方法分类")
    method_count: Dict[str, List[int]] = {}
    for i, r in enumerate(records, 1):
        for m in r.methods:
            method_count.setdefault(m, []).append(i)
    for m, refs in sorted(method_count.items(), key=lambda x: -len(x[1]))[:8]:
        cites = "".join(f"[{i}]" for i in refs[:5])
        lines.append(f"- {m}：相关文献 {cites}")

    lines.append("\n## 各类方法对比")
    lines.append("（LLM 未配置，自动综述降级为方法清单。配置 DEEPSEEK_API_KEY 后可获得完整对比。）")

    lines.append("\n## 研究空白")
    lines.append("待 LLM 启用后自动归纳。")

    lines.append("\n## 未来方向")
    lines.append("待 LLM 启用后自动归纳。")
    return "\n".join(lines)


def generate_review(papers: List[Paper], records: List[StructuredRecord], clusters: Optional[Dict] = None) -> dict:
    """生成综述。返回 {text, citations_used, hallucinated_citations, fallback}."""
    if not records:
        return {"text": "（无可用文献）", "mermaid_code": "", "citations_used": [],
                "hallucinated_citations": [], "unsupported_claims": [],
                "mermaid_time_issues": [], "fallback": False}

    if not llm_available():
        text = _fallback_review(records)
        return {
            "text": text,
            "mermaid_code": "",
            "citations_used": sorted({int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", text)}),
            "hallucinated_citations": [],
            "unsupported_claims": [],
            "mermaid_time_issues": [],
            "fallback": True,
        }

    # 1. Planner Agent 规划大纲
    logger.info("启动 Planner Agent 规划综述大纲...")
    outline = _run_planner_agent(papers, records, clusters)
    
    # 2. Writer Agents 并发逐节撰写 (含按需 RAG 注入)
    from config import DEEPSEEK_API_KEYS
    workers = min(20, 5 * max(1, len(DEEPSEEK_API_KEYS)))
    logger.info(f"启动 {len(outline)} 个 Writer Agent (并发 {workers}) 撰写各章节...")
    draft_sections = [""] * len(outline)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {executor.submit(_run_writer_agent, sec, records): i for i, sec in enumerate(outline)}
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            draft_sections[idx] = future.result()
            
    text = "\n\n".join(draft_sections)
    
    # 3. Mermaid Agent 独立生成图表
    logger.info("启动 Mermaid Agent 生成演进图...")
    mermaid_code = _run_mermaid_agent(records)

    # LLM 偶尔忘记输出演进图：用抽取结果确定性兜底，保证图不消失
    if not mermaid_code:
        mermaid_code = _build_fallback_mermaid(records)
        if mermaid_code:
            logger.info("LLM 未输出演进图，已根据抽取的方法/年份自动生成兜底图")

    # 演进图时间校验：修正年份标注与"晚→早"的倒置箭头，保证无明显时间错误
    mermaid_code, mermaid_time_issues = _validate_and_fix_mermaid(mermaid_code, records)
    if mermaid_time_issues:
        logger.info("演进图时间校验：修正 %d 处时间错误", len(mermaid_time_issues))

    hallucinated = _validate_citations(text, len(records))
    citations_used = sorted({
        int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", text)
        if 1 <= int(m.group(1)) <= len(records)
    })
    unsupported = _check_grounding(text, records)
    return {
        "text": text,
        "mermaid_code": mermaid_code,
        "citations_used": citations_used,
        "hallucinated_citations": hallucinated,
        "unsupported_claims": unsupported,
        "mermaid_time_issues": mermaid_time_issues,
        "fallback": False,
    }

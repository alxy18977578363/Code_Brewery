import logging
import re
from typing import List, Dict
import concurrent.futures

from src.models import StructuredRecord, Paper
from src.llm.deepseek_client import chat, DeepSeekError

logger = logging.getLogger(__name__)

def _run_auditor_agent(draft: str, records: List[StructuredRecord], extra_issues: str = "") -> str:
    """找茬专家：对照 RAG 源数据，检查草稿中的幻觉、数值错误、引用错误。"""
    # 构造精确的上下文源数据
    context_lines = []
    for i, r in enumerate(records, 1):
        details = f"详评: {r.detailed_analysis}" if getattr(r, "detailed_analysis", None) else ""
        res_text = ""
        if getattr(r, "results", None):
            res_list = [f"{res.get('dataset', '')}({res.get('metric', '')}): {res.get('value', '')}" for res in r.results]
            if res_list:
                res_text = f"定量结果: {'; '.join(res_list)}"
        context_lines.append(f"[{i}] {r.title}\n{res_text}\n{details}")
        
    context = "\n".join(context_lines)
    
    sys_prompt = """你是一名严格的学术审查员 (Auditor Agent)。
请仔细比对提供的【原始文献上下文】与下方的【综述草稿】。
重点核查：
1. 草稿中提到的定性结论、定量数据是否与原始文献完全一致？
2. 引用的编号 [n] 是否出现了“张冠李戴”（比如 [1] 的方法被标成了 [2]）？
3. 是否存在毫无根据的幻觉编造？

请输出一份《缺陷报告》，列出 3-5 点最严重的具体错误。如果没有明显错误，请说明“未发现严重事实错误，建议润色语句”。
"""
    try:
        user_content = f"【原始文献上下文】\n{context}\n\n【专门检测到的疑似幻觉】\n{extra_issues}\n\n【综述草稿】\n{draft}"
        report = chat(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            max_tokens=2048
        )
        return report
    except Exception as e:
        logger.warning(f"Auditor 运行失败: {e}")
        return "未能生成缺陷报告。"

def _run_reviser_agent(draft: str, report: str) -> str:
    """主编：根据 Auditor 的缺陷报告，对草稿进行定向改写。"""
    sys_prompt = """你是一名综述主编 (Reviser Agent)。
你的任务是根据 Auditor 提供的《缺陷报告》，对当前的【综述草稿】进行精准修复和重写。
要求：
1. 保持原有的章节结构（## 标题）不变。
2. 修复报告中指出的所有事实、数值、引用错误。
3. 优化语句，使其更加连贯、专业。
4. 输出的依然是一篇完整的综述正文（保留所有的 [n] 引用标号）。
5. 不要输出任何额外的客套话或解释，直接输出重写后的综述正文。
"""
    try:
        text = chat(
            [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"【缺陷报告】\n{report}\n\n【综述草稿】\n{draft}"}
            ],
            temperature=0.3,
            max_tokens=8192
        )
        return text.strip()
    except Exception as e:
        logger.warning(f"Reviser 运行失败: {e}")
        return draft

def optimize_review(draft: str, records: List[StructuredRecord], level: int = 1, initial_issues: List[dict] = None) -> Dict:
    """多级优化调度入口。
    Level 1: 仅 Reviser 单次快速润色
    Level 2: 一轮 Auditor + Reviser 迭代
    Level 3: 两轮极限迭代（或更强力度）
    """
    current_draft = draft
    logs = []
    
    if level == 1:
        logs.append("[Level 1] 开始单轮快速润色...")
        report = "全面通读草稿，修正语病，使过渡更自然，无需苛求事实核查。"
        current_draft = _run_reviser_agent(current_draft, report)
        logs.append("[Level 1] 润色完成。")
        
    elif level >= 2:
        iterations = 2 if level == 3 else 1
        logs.append(f"[Level {level}] 启动多智能体深度审核（计划 {iterations} 轮迭代）...")
        
        for i in range(iterations):
            if i == 0 and initial_issues is not None:
                logs.append(f"  -> 第 {i+1} 轮：复用初稿生成的幻觉扫描结果...")
                grounding_issues = initial_issues
            else:
                logs.append(f"  -> 第 {i+1} 轮：Grounding Agent 正在进行幻觉扫描...")
                from src.review.generator import _check_grounding
                grounding_issues = _check_grounding(current_draft, records)
                
            if grounding_issues:
                issue_str = "\n".join([f"警报：句段 '{iss.get('snippet', '')}' 中将术语 {iss.get('terms', [])} 错误归属给了文献 {iss.get('cited', [])}。" for iss in grounding_issues])
            else:
                issue_str = "无明显张冠李戴幻觉。"
                
            logs.append(f"  -> 第 {i+1} 轮：Auditor 正在综合找茬...")
            report = _run_auditor_agent(current_draft, records, extra_issues=issue_str)
            logs.append(f"  -> 第 {i+1} 轮：Auditor 发现问题：\n{report[:300]}...")
            
            if "未发现" in report and "严重事实错误" in report:
                logs.append("  -> Auditor 满意当前版本，提前结束迭代。")
                break
                
            logs.append(f"  -> 第 {i+1} 轮：Reviser 正在根据报告重写...")
            current_draft = _run_reviser_agent(current_draft, report)
            logs.append(f"  -> 第 {i+1} 轮：重写完成。")
            
        logs.append(f"[Level {level}] 深度审核与优化全部完成。")
        
    # 在返回前，利用已有的方法重新计算各项指标，保证前端面板实时更新
    from src.review.generator import _validate_citations, _check_grounding
    hallucinated = _validate_citations(current_draft, len(records))
    citations_used = sorted({
        int(m.group(1)) for m in re.finditer(r"\[(\d+)\]", current_draft)
        if 1 <= int(m.group(1)) <= len(records)
    })
    unsupported = _check_grounding(current_draft, records)
        
    return {
        "text": current_draft,
        "citations_used": citations_used,
        "hallucinated_citations": hallucinated,
        "unsupported_claims": unsupported,
        "logs": logs
    }

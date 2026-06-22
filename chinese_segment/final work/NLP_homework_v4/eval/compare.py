"""规则法 vs LLM 抽取的量化对比脚本（CLI 入口）。

用法：
    python eval/compare.py            # 只跑规则法
    python eval/compare.py --llm      # 同时跑 LLM（需配置 DEEPSEEK_API_KEY）

评测核心逻辑在 src/extraction/evaluator.py，CLI 与 Web 端共用，保证口径一致。
评测口径：
- methods / datasets / metrics：集合级 P/R/F1，做大小写和空白归一化
- conclusion：按"关键词命中率"评估（gold 给关键词列表，预测结论里是否包含）
"""
import argparse
import io
import json
import sys
from pathlib import Path
from typing import Dict

# Windows 控制台默认 GBK，强制 UTF-8 输出避免中文乱码
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import llm_available  # noqa: E402
from src.extraction import LLMExtractor, RuleBasedExtractor  # noqa: E402
from src.extraction.evaluator import evaluate  # noqa: E402


def fmt(summary: Dict) -> str:
    lines = [f"\n=== {summary['_label']} (n={summary['_n']}) ==="]
    for field in ["datasets_prf", "metrics_prf"]:
        s = summary[field]
        name = field.replace("_prf", "")
        lines.append(f"  {name:<10} P={s['P']:.3f}  R={s['R']:.3f}  F1={s['F1']:.3f}")
    lines.append(f"  {'conclusion':<10} hit={summary['conclusion']['hit_rate']:.3f}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="同时跑 LLM 抽取")
    ap.add_argument("--data", default=str(ROOT / "eval" / "labeled.json"))
    args = ap.parse_args()

    examples = json.loads(Path(args.data).read_text(encoding="utf-8"))

    print(f"加载 {len(examples)} 条标注样本，开始评测…")

    rule_summary = evaluate(RuleBasedExtractor(), examples, "规则法 (jieba + 词典)")
    print(fmt(rule_summary))

    if args.llm:
        if not llm_available():
            print("\n[警告] 未配置 DEEPSEEK_API_KEY，跳过 LLM 评测")
            return
        llm_summary = evaluate(LLMExtractor(), examples, "LLM 法 (DeepSeek)")
        print(fmt(llm_summary))

        print("\n=== 对比 (LLM − 规则) ===")
        for field in ["datasets_prf", "metrics_prf"]:
            name = field.replace("_prf", "")
            diff = llm_summary[field]["F1"] - rule_summary[field]["F1"]
            sign = "+" if diff >= 0 else ""
            print(f"  {name:<10} ΔF1 = {sign}{diff:.3f}")


if __name__ == "__main__":
    main()

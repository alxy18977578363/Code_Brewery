from __future__ import annotations

import argparse
import ast
import html
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from great_expectations.dataset import PandasDataset


ROOT = Path(__file__).resolve().parent
DEFAULT_PARQUET_PATH = ROOT / "data" / "OK-VQA" / "data_clean.parquet"
DEFAULT_OUTPUT_DIR = ROOT / "src" / "data_processing" / "ge_expectations"
DEFAULT_SUITE_PATH = DEFAULT_OUTPUT_DIR / "okvqa_expectation_suite.json"
DEFAULT_RESULT_PATH = DEFAULT_OUTPUT_DIR / "okvqa_validation_result.json"
DEFAULT_DUCKDB_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "okvqa_duckdb_summary.json"
DEFAULT_REPORT_PATH = ROOT / "index.html"


@dataclass
class RuleSpec:
    field: str
    rule_type: str
    description: str
    expectation: str
    kwargs: dict[str, Any]
    note: str = ""


def _safe_parse_answers(value: Any) -> list[Any]:
    """将 answers 字段统一解析为 list，兼容 list[dict] / list[str] / 字符串化列表。"""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, list):
        return value
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []

    return []


def _json_safe(obj: Any) -> Any:
    """将对象转换为 JSON 可序列化结构。"""
    try:
        from great_expectations.core.util import convert_to_json_serializable

        return convert_to_json_serializable(obj)
    except Exception:
        if isinstance(obj, dict):
            return {k: _json_safe(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_json_safe(v) for v in obj]
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        return obj


def _normalize_answer_text(answer: Any) -> str:
    if answer is None:
        return ""
    if isinstance(answer, dict):
        answer = answer.get("answer", "")
    return str(answer).strip().lower()


def _all_answers_not_empty(value: Any) -> bool:
    answers = _safe_parse_answers(value)
    if not answers:
        return False
    for item in answers:
        if isinstance(item, dict):
            answer_text = str(item.get("answer", "")).strip()
            if not answer_text:
                return False
        else:
            if not str(item).strip():
                return False
    return True


def _compute_image_bytes(image_name: Any, image_dir: Path) -> int | None:
    if image_name is None:
        return None
    image_path = image_dir / str(image_name)
    try:
        return os.path.getsize(image_path)
    except Exception:
        return None


def load_and_prepare_df(parquet_path: Path) -> pd.DataFrame:
    """读取数据并补充质量规则与统计需要的派生字段。"""
    df = pd.read_parquet(parquet_path, engine="pyarrow")

    try:
        df["question_id"] = pd.to_numeric(df["question_id"], errors="raise").astype("int64")
    except Exception as exc:
        raise ValueError(f"question_id 无法全部转换为 int64，请检查输入数据。原始异常: {exc}")

    answers_list = df["answers"].apply(_safe_parse_answers)
    df["answers_count"] = answers_list.apply(len)
    df["answers_all_not_empty"] = df["answers"].apply(_all_answers_not_empty)
    df["question"] = df["question"].astype(str)
    df["question_len"] = df["question"].str.len()

    image_dir = (parquet_path.parent / "images").resolve()
    df["image_bytes"] = df["image"].apply(lambda v: _compute_image_bytes(v, image_dir))
    return df


def run_duckdb_summary(parquet_path: Path, df: pd.DataFrame) -> dict[str, Any]:
    """输出 DuckDB 基础统计，便于在报告中展示全局质量背景。"""
    con = duckdb.connect()
    total_rows = int(con.execute(f"SELECT COUNT(*) FROM parquet_scan('{parquet_path.as_posix()}')").fetchone()[0])
    con.close()

    missing_values = {
        col: int(df[col].isna().sum()) for col in ["question_id", "image", "question", "answers", "question_type", "answer_type"]
    }

    question_type_dist = df["question_type"].astype(str).value_counts().to_dict()
    answer_type_dist = df["answer_type"].astype(str).value_counts().to_dict()

    normalized_answers = df["answers"].apply(_safe_parse_answers).apply(
        lambda xs: [txt for txt in (_normalize_answer_text(a) for a in xs) if txt]
    )
    answers_count_dist = df["answers_count"].value_counts().sort_index().to_dict()

    main_answer_ratio = []
    for answers in normalized_answers:
        if not answers:
            main_answer_ratio.append(0.0)
            continue
        counts = pd.Series(answers).value_counts()
        main_answer_ratio.append(float(counts.iloc[0] / len(answers)))

    ratio_series = pd.Series(main_answer_ratio)
    return {
        "total_rows": total_rows,
        "missing_values": missing_values,
        "question_type_dist": question_type_dist,
        "answer_type_dist": answer_type_dist,
        "answers_count_dist": answers_count_dist,
        "main_answer_ratio": {
            "mean": float(ratio_series.mean()),
            "min": float(ratio_series.min()),
            "max": float(ratio_series.max()),
        },
        "question_length": {
            "mean": float(df["question_len"].mean()),
            "min": int(df["question_len"].min()),
            "max": int(df["question_len"].max()),
        },
    }


def build_rules() -> list[RuleSpec]:
    return [
        RuleSpec("question_id", "非空", "所有 question_id 必须非空", "expect_column_values_to_not_be_null", {"column": "question_id"}),
        RuleSpec("question_id", "唯一性", "所有 question_id 必须全局唯一", "expect_column_values_to_be_unique", {"column": "question_id"}),
        RuleSpec("question_id", "类型", "所有 question_id 必须为 int64 类型", "expect_column_values_to_be_of_type", {"column": "question_id", "type_": "int64"}),
        RuleSpec("question_id", "数值范围", "所有 question_id 必须大于等于 1", "expect_column_values_to_be_between", {"column": "question_id", "min_value": 1}),
        RuleSpec("image", "非空", "所有 image 字段必须非空", "expect_column_values_to_not_be_null", {"column": "image"}),
        RuleSpec(
            "image_bytes",
            "长度范围",
            "图片字节长度应在 1KB~10MB 之间，95% 以上样本满足",
            "expect_column_values_to_be_between",
            {"column": "image_bytes", "min_value": 1024, "max_value": 10485760, "mostly": 0.95},
            "部分图片可能缺失或损坏",
        ),
        RuleSpec(
            "image",
            "类型正则",
            "图片文件名后缀应为 jpg/jpeg/png/gif/bmp/webp",
            "expect_column_values_to_match_regex",
            {"column": "image", "regex": r"(?i)\.(jpg|jpeg|png|gif|bmp|webp)$"},
            "若 image 字段不是文件名（而是列表/结构化对象），该规则会失败",
        ),
        RuleSpec("question", "非空", "所有 question 字段必须非空", "expect_column_values_to_not_be_null", {"column": "question"}),
        RuleSpec(
            "question",
            "正则",
            "问题文本应以英文问号 ? 结尾",
            "expect_column_values_to_match_regex",
            {"column": "question", "regex": r"\?$", "mostly": 0.99},
            "个别样本可能为陈述句",
        ),
        RuleSpec("question", "长度", "问题文本长度应在 1~300 之间", "expect_column_value_lengths_to_be_between", {"column": "question", "min_value": 1, "max_value": 300}),
        RuleSpec("answers", "非空", "所有 answers 字段必须非空", "expect_column_values_to_not_be_null", {"column": "answers"}),
        RuleSpec(
            "answers_count",
            "数量范围",
            "每个问题答案数量应在 1~10 之间",
            "expect_column_values_to_be_between",
            {"column": "answers_count", "min_value": 1, "max_value": 10, "mostly": 0.99},
            "个别样本答案数量可能异常",
        ),
        RuleSpec(
            "answers_all_not_empty",
            "内容完整",
            "所有答案均应为非空文本，95% 以上样本满足",
            "expect_column_values_to_be_in_set",
            {"column": "answers_all_not_empty", "value_set": [True], "mostly": 0.95},
            "部分答案可能为空字符串",
        ),
        RuleSpec("question_type", "非空", "所有 question_type 字段必须非空", "expect_column_values_to_not_be_null", {"column": "question_type"}),
        RuleSpec(
            "question_type",
            "类别合法性",
            "所有 question_type 必须属于预定义 11 类",
            "expect_column_values_to_be_in_set",
            {
                "column": "question_type",
                "value_set": [
                    "Brands, Companies and Products",
                    "Cooking and Food",
                    "Geography, History, Language and Culture",
                    "Objects, Material and Clothing",
                    "Other",
                    "People and Everyday life",
                    "Plants and Animals",
                    "Science and Technology",
                    "Sports and Recreation",
                    "Vehicles and Transportation",
                    "Weather and Climate",
                ],
            },
        ),
        RuleSpec("answer_type", "非空", "所有 answer_type 字段必须非空", "expect_column_values_to_not_be_null", {"column": "answer_type"}),
        RuleSpec("answer_type", "类别合法性", "所有 answer_type 只能为 other", "expect_column_values_to_be_in_set", {"column": "answer_type", "value_set": ["other"]}),
    ]


def run_expectations(df: pd.DataFrame, rules: list[RuleSpec]) -> tuple[PandasDataset, list[dict[str, Any]]]:
    dataset = PandasDataset(df)
    results: list[dict[str, Any]] = []
    for rule in rules:
        method = getattr(dataset, rule.expectation)
        result = method(**rule.kwargs)
        results.append(result)
    return dataset, results


def to_report_rows(total_rows: int, rules: list[RuleSpec], ge_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for rule, result in zip(rules, ge_results):
        payload = result.get("result", {})
        kwargs = result.get("expectation_config", {}).get("kwargs", {})
        element_count = int(payload.get("element_count") or total_rows)

        if "unexpected_count" in payload:
            unexpected_count = int(payload.get("unexpected_count") or 0)
        else:
            unexpected_count = 0 if result.get("success") else element_count

        pass_count = max(element_count - unexpected_count, 0)
        pass_rate = (pass_count / element_count) if element_count > 0 else 0.0
        pass_rate_pct = f"{pass_rate * 100:.2f}%"

        mostly = kwargs.get("mostly")
        if mostly is not None and result.get("success"):
            threshold = float(mostly) * 100
            threshold_text = int(threshold) if float(threshold).is_integer() else round(threshold, 2)
            pass_rate_pct = f">={threshold_text}%"

        note = rule.note
        if not result.get("success") and not note:
            partial = payload.get("partial_unexpected_list", [])
            note = "存在异常样本"
            if partial:
                note = f"示例异常值: {str(partial[0])[:80]}"

        rows.append(
            {
                "field": rule.field,
                "rule_type": rule.rule_type,
                "description": rule.description,
                "total": element_count,
                "unexpected": unexpected_count,
                "pass_rate": pass_rate_pct,
                "status": "通过" if result.get("success") else "未通过",
                "status_class": "pass" if result.get("success") else "fail",
                "note": note,
            }
        )
    return rows


def render_html_report(report_rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    total_rules = len(report_rows)
    passed_rules = sum(1 for row in report_rows if row["status"] == "通过")
    failed_rules = total_rules - passed_rules
    global_pass_rate = (passed_rules / total_rules * 100) if total_rules > 0 else 0.0

    html_rows = []
    for row in report_rows:
        html_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['field']))}</td>"
            f"<td>{html.escape(str(row['rule_type']))}</td>"
            f"<td>{html.escape(str(row['description']))}</td>"
            f"<td>{row['total']}</td>"
            f"<td>{row['unexpected']}</td>"
            f"<td>{html.escape(str(row['pass_rate']))}</td>"
            f"<td class=\"{row['status_class']}\">{row['status']}</td>"
            f"<td>{html.escape(str(row['note']))}</td>"
            "</tr>"
        )

    missing_items = "".join(
        f"<li>{html.escape(k)}: {v}</li>" for k, v in summary.get("missing_values", {}).items()
    )

    return f"""<!DOCTYPE html>
<html lang=\"zh-cn\">
<head>
    <meta charset=\"UTF-8\" />
    <title>OK-VQA数据集质量验证结果</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 36px;
            color: #222;
            background: #fafafa;
        }}
        .summary {{
            width: 95%;
            margin: 0 auto 18px auto;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px 16px;
            box-sizing: border-box;
        }}
        .summary h3 {{
            margin: 0 0 8px 0;
            font-size: 1.05em;
        }}
        .summary p {{
            margin: 4px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 95%;
            margin: 0 auto;
            background: #fff;
        }}
        th, td {{
            border: 1px solid #aaa;
            padding: 8px 12px;
            text-align: center;
        }}
        th {{
            background: #f2f2f2;
        }}
        .pass {{
            color: #228b22;
            font-weight: bold;
        }}
        .fail {{
            color: #b22222;
            font-weight: bold;
        }}
        caption {{
            font-size: 1.3em;
            margin-bottom: 15px;
        }}
        ul {{
            margin: 6px 0;
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class=\"summary\">
        <h3>执行摘要</h3>
        <p>总样本数: {summary.get('total_rows', 0)}</p>
        <p>规则总数: {total_rules}，通过: {passed_rules}，未通过: {failed_rules}，规则通过率: {global_pass_rate:.2f}%</p>
        <p>问题文本长度（均值/最小/最大）: {summary.get('question_length', {}).get('mean', 0):.2f} / {summary.get('question_length', {}).get('min', 0)} / {summary.get('question_length', {}).get('max', 0)}</p>
        <p>字段缺失值概览:</p>
        <ul>{missing_items}</ul>
    </div>

    <table>
        <caption>OK-VQA数据集质量规则验证详细结果</caption>
        <tr>
            <th>字段名</th>
            <th>规则类型</th>
            <th>规则描述</th>
            <th>样本总数</th>
            <th>异常样本数</th>
            <th>通过率</th>
            <th>验证结果</th>
            <th>备注</th>
        </tr>
        {''.join(html_rows)}
    </table>

    <p style=\"text-align:center;margin-top:30px;\">
        <b>结论：</b>本报告由脚本自动生成。
    </p>
</body>
</html>
"""


def save_json(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(_json_safe(content), f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="OK-VQA 一键质量验证脚本")
    parser.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET_PATH, help="Parquet 数据路径")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH, help="HTML 报告输出路径")
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE_PATH, help="Expectation Suite 输出路径")
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT_PATH, help="验证结果 JSON 输出路径")
    parser.add_argument("--duckdb-summary", type=Path, default=DEFAULT_DUCKDB_SUMMARY_PATH, help="DuckDB 摘要输出路径")
    args = parser.parse_args()

    parquet_path = args.parquet.resolve()
    if not parquet_path.exists():
        raise FileNotFoundError(f"未找到数据文件: {parquet_path}")

    df = load_and_prepare_df(parquet_path)
    duckdb_summary = run_duckdb_summary(parquet_path, df)

    rules = build_rules()
    dataset, ge_results = run_expectations(df, rules)

    suite = dataset.get_expectation_suite(discard_failed_expectations=False)
    save_json(args.suite.resolve(), suite.to_json_dict())

    success_count = sum(1 for item in ge_results if item.get("success"))
    statistics = {
        "evaluated_expectations": len(ge_results),
        "successful_expectations": success_count,
        "unsuccessful_expectations": len(ge_results) - success_count,
        "success_percent": round(success_count / len(ge_results) * 100, 2) if ge_results else 0.0,
    }
    validation_result = {
        "success": success_count == len(ge_results),
        "results": ge_results,
        "statistics": statistics,
    }
    save_json(args.result.resolve(), validation_result)
    save_json(args.duckdb_summary.resolve(), duckdb_summary)

    report_rows = to_report_rows(duckdb_summary["total_rows"], rules, ge_results)
    report_html = render_html_report(report_rows, duckdb_summary)

    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_html, encoding="utf-8")

    print("验证完成，输出如下：")
    print(f"- HTML 报告: {report_path}")
    print(f"- Expectation Suite: {args.suite.resolve()}")
    print(f"- 验证结果 JSON: {args.result.resolve()}")
    print(f"- DuckDB 摘要 JSON: {args.duckdb_summary.resolve()}")
    print(f"- 规则通过率: {statistics['success_percent']}% ({statistics['successful_expectations']}/{statistics['evaluated_expectations']})")


if __name__ == "__main__":
    main()

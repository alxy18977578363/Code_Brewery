"""
OK-VQA 数据质量规则（Great Expectations）

功能：
1. 读取 data_clean.parquet
2. 构建并执行不少于 5 条数据质量规则
3. 导出 expectation suite 与验证结果 JSON
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from great_expectations.dataset import PandasDataset


ROOT = Path(__file__).resolve().parents[1]
PARQUET_PATH = ROOT / "data" / "OK-VQA" / "data_clean.parquet"
OUTPUT_DIR = ROOT / "src" / "data_processing" / "ge_expectations"
SUITE_PATH = OUTPUT_DIR / "okvqa_expectation_suite.json"
RESULT_PATH = OUTPUT_DIR / "okvqa_validation_result.json"


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

		# JSON 失败时再退化到 literal_eval，避免直接使用 eval 的安全风险。
		try:
			parsed = ast.literal_eval(raw)
			if isinstance(parsed, list):
				return parsed
		except Exception:
			return []

	return []


def _json_safe(obj: Any) -> Any:
	"""将 Great Expectations 返回对象转换为 JSON 可序列化结构。"""
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


def load_and_prepare_df(parquet_path: Path) -> pd.DataFrame:
	"""读取数据并补充质量规则需要的派生字段。"""
	df = pd.read_parquet(parquet_path, engine="pyarrow")

	# 强制将 question_id 转为 int 类型，若失败则报错
	try:
		df["question_id"] = df["question_id"].astype(int)
	except Exception as e:
		raise ValueError(f"question_id 字段无法全部转换为 int，请检查数据内容。原始异常: {e}")

	answers_list = df["answers"].apply(_safe_parse_answers)
	df["answers_count"] = answers_list.apply(len)
	df["question_len"] = df["question"].astype(str).str.len()

	# image 字段字节长度（如图片文件可访问）
	# 假设 image 字段为图片路径或文件名，图片文件位于 data/OK-VQA/images 目录
	image_dir = (parquet_path.parent / "images").resolve()
	def get_image_bytes(img_name):
		import os
		img_path = image_dir / str(img_name)
		try:
			return os.path.getsize(img_path)
		except Exception:
			return None
	df["image_bytes"] = df["image"].apply(get_image_bytes)

	return df

def add_quality_features(df: pd.DataFrame) -> pd.DataFrame:
	"""生成数据质量辅助特征，如 answers_all_not_empty。"""
	def all_answers_not_empty(ans):
		if not ans:
			return False
		for item in ans:
			if isinstance(item, dict):
				if not item.get("answer") or not str(item.get("answer")).strip():
					return False
			else:
				if not str(item).strip():
					return False
		return True
	df["answers_all_not_empty"] = df["answers"].apply(_safe_parse_answers).apply(all_answers_not_empty)
	return df

def apply_expectations(dataset: PandasDataset) -> None:	
	"""定义并应用数据质量规则。"""
	# question_id 检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="question_id")
	# 2. 唯一
	dataset.expect_column_values_to_be_unique(column="question_id")
	# 3. 类型为 int（已在数据加载阶段强制转换）
	dataset.expect_column_values_to_be_of_type(column="question_id", type_="int64")
	# 4. 数值大于 0
	dataset.expect_column_values_to_be_between(column="question_id", min_value=1)

	# image 字段检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="image")
	# 2. 字节长度合理性（如 image_bytes 不为 None）
	# 合理范围假设为 1KB~10MB（1024~10_485_760 字节），可根据实际图片调整
	dataset.expect_column_values_to_be_between(column="image_bytes", min_value=1024, max_value=10_485_760, mostly=0.95)
	# 3. 图片类型检查（jpg/jpeg/png/gif/bmp/webp等）
	dataset.expect_column_values_to_match_regex(column="image", regex=r"(?i)\\.(jpg|jpeg|png|gif|bmp|webp)$")

	# question 字段检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="question")
	# 2. 正则表达式检查：以“？”结尾
	dataset.expect_column_values_to_match_regex(column="question", regex=r"\?$")
	# 3. 文本长度检查：1~300
	dataset.expect_column_value_lengths_to_be_between(column="question", min_value=1, max_value=300)

	# answers 字段检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="answers")
	# 2. 答案数量检查（1~10）
	dataset.expect_column_values_to_be_between(column="answers_count", min_value=1, max_value=10)
	# 3. 每个答案非空（通过辅助列实现）
	dataset.expect_column_values_to_be_in_set(column="answers_all_not_empty", value_set=[True], mostly=0.95)
	
	# question_type 字段检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="question_type")
	# 2. 类型检查（限定为11个类别）
	dataset.expect_column_values_to_be_in_set(
		column="question_type",
		value_set=[
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
		]
	)

	# answer_type 字段检查
	# 1. 非空
	dataset.expect_column_values_to_not_be_null(column="answer_type")
	# 2. 类别检查（只能是other）
	dataset.expect_column_values_to_be_in_set(column="answer_type", value_set=["other"])



def save_suite(dataset: PandasDataset, suite_path: Path) -> None:
	"""导出 expectation suite。"""
	suite = dataset.get_expectation_suite(discard_failed_expectations=False)
	suite_path.parent.mkdir(parents=True, exist_ok=True)
	with suite_path.open("w", encoding="utf-8") as f:
		json.dump(_json_safe(suite.to_json_dict()), f, ensure_ascii=False, indent=2)


def save_validation_result(dataset: PandasDataset, result_path: Path) -> dict[str, Any]:
	"""执行验证并导出结果。"""
	result = dataset.validate(only_return_failures=False, result_format="SUMMARY")
	result_path.parent.mkdir(parents=True, exist_ok=True)
	with result_path.open("w", encoding="utf-8") as f:
		json.dump(_json_safe(result), f, ensure_ascii=False, indent=2)
	return result


def main() -> None:
	if not PARQUET_PATH.exists():
		raise FileNotFoundError(f"未找到数据文件: {PARQUET_PATH}")

	df = load_and_prepare_df(PARQUET_PATH)
	df = add_quality_features(df)
	ge_df = PandasDataset(df)
	apply_expectations(ge_df)

	save_suite(ge_df, SUITE_PATH)
	result = save_validation_result(ge_df, RESULT_PATH)

	stats = result.get("statistics", {})
	print("Great Expectations 验证完成")
	print(f"- expectation_suite: {SUITE_PATH}")
	print(f"- validation_result: {RESULT_PATH}")
	print(f"- evaluated_expectations: {stats.get('evaluated_expectations')}")
	print(f"- successful_expectations: {stats.get('successful_expectations')}")
	print(f"- unsuccessful_expectations: {stats.get('unsuccessful_expectations')}")
	print(f"- success_percent: {stats.get('success_percent')}")


if __name__ == "__main__":
	main()

"""
DuckDB 数据加载与基础行数统计脚本
-----------------------------
功能：
1. 加载 Parquet 数据
2. 查询数据总行数
"""

import duckdb
import pandas as pd
from collections import Counter
import re
import json
import ast

def get_total_rows(parquet_path):
	"""
	统计 Parquet 文件的总行数
	参数：
		parquet_path (str): Parquet 文件路径
	返回：
		int: 总行数
	"""
	con = duckdb.connect()
	query = f"SELECT COUNT(*) AS total_rows FROM parquet_scan('{parquet_path}')"
	result = con.execute(query).fetchdf()
	con.close()
	return result['total_rows'][0]

def get_missing_report(parquet_path):
    """
    统计每个字段的缺失值数量和比例
    返回：DataFrame，包含字段名、缺失数量、缺失比例
    """
    con = duckdb.connect()
    # 获取所有字段名
    columns = pd.read_parquet(parquet_path).columns.tolist()
    total_rows = con.execute(f"SELECT COUNT(*) FROM parquet_scan('{parquet_path}')").fetchone()[0]
    # 构造缺失值统计SQL
    sql = " UNION ALL ".join([
        f"SELECT '{col}' AS column, COUNT(*) AS missing_count, COUNT(*)*1.0/{total_rows} AS missing_ratio FROM parquet_scan('{parquet_path}') WHERE {col} IS NULL"
        for col in columns
    ])
    df = con.execute(sql).fetchdf()
    con.close()
    return df

def get_semantic_stats(parquet_path):
    """
    统计具有业务统计意义的字段：
    - question_type/answer_type 类别分布
    - answers: 答案数量分布、主流答案占比
    - question: 文本长度分布、词频分析
    返回：dict，包含各统计结果
    """
    df = pd.read_parquet(parquet_path, engine='pyarrow')
    result = {}
    # 1. question_type 分布
    result['question_type_dist'] = df['question_type'].value_counts().to_frame('count')
    
    # 2. answer_type 分布
    result['answer_type_dist'] = df['answer_type'].value_counts().to_frame('count')
    
    # 3. answers: 答案数量分布、主流答案占比
    import numpy as np
    def parse_answers(x):
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, list):
            return x
        if pd.isna(x):
            return []
        if isinstance(x, str):
            s = x.strip()
            if not s:
                return []
            try:
                v = json.loads(s)
                if isinstance(v, list):
                    return v
            except Exception:
                pass
            try:
                v = ast.literal_eval(s)
                if isinstance(v, list):
                    return v
            except Exception:
                return []
        return []

    def normalize_answer_text(a):
        if a is None:
            return ''
        # 兼容 OK-VQA 常见结构：answers 为 list[dict]，优先取 dict['answer']。
        if isinstance(a, dict):
            a = a.get('answer', '')
        return str(a).strip().lower()

    answers_list = df['answers'].apply(parse_answers)
    normalized_answers = answers_list.apply(lambda xs: [normalize_answer_text(a) for a in xs if normalize_answer_text(a)])
    answer_count = normalized_answers.apply(len)
    result['answers_count_dist'] = answer_count.value_counts().sort_index().to_frame('count')
    def main_answer_ratio(ans):
        if not ans:
            return 0
        c = Counter(ans)
        return c.most_common(1)[0][1] / len(ans)
    result['main_answer_ratio'] = normalized_answers.apply(main_answer_ratio).describe()
    
    # 4. question: 文本长度分布、词频分析
    question_len = df['question'].astype(str).apply(len)
    result['question_length_dist'] = question_len.describe()
    # 词频统计（简单分词，按空格和标点切分）
    all_text = ' '.join(df['question'].astype(str).tolist()).lower()
    words = re.findall(r'\b\w+\b', all_text)
    word_freq = Counter(words)
    result['question_word_freq'] = pd.DataFrame(word_freq.most_common(30), columns=['word', 'freq'])
    return result


def analyze_uniqueness_duckdb(parquet_path, cols):
    """
    检查给定特征序列是否能唯一标识每一行数据（候选码分析）
    参数：
        parquet_path (str): Parquet 文件路径
        cols (list): 特征名列表，按优先级排序
    输出：
        每一步组合的唯一性统计，及最终结论
    """
    con = duckdb.connect()
    total_rows = con.execute(f"SELECT COUNT(*) FROM parquet_scan('{parquet_path}')").fetchone()[0]
    print(f"总行数: {total_rows}")
    current_cols = []
    for i, col in enumerate(cols):
        current_cols.append(col)
        # 构造列名字符串，防止SQL关键字冲突
        col_list = ', '.join([f'"{c}"' for c in current_cols])
        # 用 GROUP BY 统计唯一组合数
        query = f"SELECT COUNT(*) FROM (SELECT 1 FROM parquet_scan('{parquet_path}') GROUP BY {col_list}) t"
        unique_count = con.execute(query).fetchone()[0]
        print(f"使用特征 {current_cols} 唯一值数量: {unique_count}")
        # 若当前组合已唯一，直接返回
        if unique_count == total_rows:
            print(f"特征组合 {current_cols} 可以唯一标识每一行（候选码）")
            con.close()
            return
    # 若所有组合都不能唯一标识
    print(f"特征序列 {cols} 组合后，唯一值数量为 {unique_count}，小于总行数，不能唯一标识每一行，存在重复。")
    con.close()

def main():
    parquet_path = 'data/OK-VQA/data_clean.parquet'
    total_rows = get_total_rows(parquet_path)
    print('数据总行数:', total_rows)

    missing_report = get_missing_report(parquet_path)
    print("\n缺失值统计报告:")
    print(missing_report)

    stats = get_semantic_stats(parquet_path)
    print("question_type 类别分布:")
    print("="*50)
    print(stats['question_type_dist'])
    print("="*50)

    print("\nanswer_type 类别分布:")
    print("="*50)
    print(stats['answer_type_dist'])
    print("="*50)

    print("\nanswers 答案数量分布:")
    print("="*50)
    print(stats['answers_count_dist'])
    print("="*50)

    print("="*50)
    print("\n主流答案占比描述:")
    print(stats['main_answer_ratio'])
    print("="*50)

    print("\nquestion 文本长度描述:")
    print("="*50)
    print(stats['question_length_dist'])
    print("\nquestion 词频Top30:")
    print(stats['question_word_freq'])
    print("="*50)


    # 检查数据唯一性
    print("\n检查数据唯一性示例1：['question_id']")
    print("="*50)
    analyze_uniqueness_duckdb(parquet_path, ['question_id'])
    print("\n检查数据唯一性示例2：['question', 'answers', 'answer_type']")
    analyze_uniqueness_duckdb(parquet_path, ['question', 'answers','image'])
    print("="*50)

if __name__ == "__main__":
	main()

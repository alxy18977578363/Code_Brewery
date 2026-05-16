"""
Chennai Restaurant Dataset - Data Loader Module
数据加载模块：负责定位和加载CSV文件
"""

from pathlib import Path
import pandas as pd


def locate_dataset_dir():
    """
    查找数据集目录 - 按优先级搜索多个位置
    
    搜索顺序：
    1. Kaggle官方路径
    2. Kaggle挂载点
    3. 本地 dataset/ 文件夹
    4. 上级目录 dataset/ 文件夹
    5. 当前工作目录
    6. 上级工作目录
    7. Kaggle input 下递归搜索
    
    Returns
    -------
    Path
        包含数据集CSV文件的目录路径
    
    Raises
    ------
    FileNotFoundError
        如果找不到Zomato_Chennai_Final.csv
    """
    cwd = Path.cwd()
    candidates = [
        Path("/kaggle/input/datasets/devvraj/chennai-restaurant-dataset"),
        Path("/kaggle/input/chennai-restaurant-dataset"),
        cwd / "dataset",
        cwd.parent / "dataset",
        cwd,
        cwd.parent,
    ]
    
    for base in candidates:
        csv_path = base / "Zomato_Chennai_Final.csv"
        if csv_path.exists():
            print(f"✓ 在此位置找到数据集: {base}")
            return base
    
    # 递归搜索 Kaggle input 目录
    kaggle_input = Path("/kaggle/input")
    if kaggle_input.exists():
        matches = list(kaggle_input.rglob("Zomato_Chennai_Final.csv"))
        if matches:
            print(f"✓ 在Kaggle目录中找到数据集: {matches[0].parent}")
            return matches[0].parent
    
    # 如果都没找到，抛出错误
    raise FileNotFoundError(
        "❌ 找不到 Zomato_Chennai_Final.csv\n"
        "   请添加 Kaggle 数据集或将文件放在 ./dataset 目录中"
    )


def load_datasets(data_dir=None, verbose=True):
    """
    加载主数据集和参考数据集
    
    Parameters
    ----------
    data_dir : Path or str, optional
        数据集目录路径。如果为None，自动定位
    verbose : bool
        是否打印加载信息
    
    Returns
    -------
    tuple
        (raw_df, segmented_df)
        - raw_df: 主数据集DataFrame
        - segmented_df: 参考数据集DataFrame (如果存在) 或 None
    
    Examples
    --------
    >>> raw, segmented = load_datasets()
    >>> print(f"加载了 {len(raw):,} 行数据")
    """
    if data_dir is None:
        data_dir = locate_dataset_dir()
    else:
        data_dir = Path(data_dir)
    
    final_path = data_dir / "Zomato_Chennai_Final.csv"
    segmented_path = data_dir / "Zomato_Chennai_Segmented.csv"
    
    # 加载主数据集
    raw = pd.read_csv(final_path)
    
    # 加载参考数据集 (如果存在)
    segmented = None
    if segmented_path.exists():
        segmented = pd.read_csv(segmented_path)
    
    if verbose:
        print("=" * 70)
        print("📊 数据集加载完成")
        print("=" * 70)
        print(f"📁 数据集目录: {data_dir}")
        print(f"📄 主文件: {final_path.name}")
        print(f"   行数: {len(raw):,} | 列数: {raw.shape[1]}")
        if segmented is not None:
            print(f"📄 参考文件: {segmented_path.name}")
            print(f"   行数: {len(segmented):,} | 列数: {segmented.shape[1]}")
        print("=" * 70)
    
    return raw, segmented


def check_data_integrity(raw_df, segmented_df=None):
    """
    检查数据完整性和质量
    
    Parameters
    ----------
    raw_df : pd.DataFrame
        主数据集
    segmented_df : pd.DataFrame, optional
        参考数据集
    
    Returns
    -------
    dict
        完整性检查结果
    
    Examples
    --------
    >>> health = check_data_integrity(raw)
    >>> print(health['duplicated_urls'])
    """
    sources = []
    
    # 检查主文件
    sources.append({
        "file": "Zomato_Chennai_Final.csv",
        "rows": len(raw_df),
        "columns": raw_df.shape[1],
        "missing_cells": int(raw_df.isna().sum().sum()),
        "duplicated_urls": 0,  # 先占位
    })
    
    # 检查参考文件
    if segmented_df is not None:
        sources.append({
            "file": "Zomato_Chennai_Segmented.csv",
            "rows": len(segmented_df),
            "columns": segmented_df.shape[1],
            "missing_cells": int(segmented_df.isna().sum().sum()),
            "duplicated_urls": 0,  # 先占位
        })
    
    health_df = pd.DataFrame(sources)
    
    return {
        "integrity": health_df,
        "has_null_urls": health_df["duplicated_urls"].any(),
    }


if __name__ == "__main__":
    # 快速测试
    try:
        raw, segmented = load_datasets()
        print("\n✓ 数据加载成功")
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")

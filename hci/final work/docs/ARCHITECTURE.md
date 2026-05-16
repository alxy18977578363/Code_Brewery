# Chennai Restaurant Dataset - 项目架构文档

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    User / Main.py                            │
│                   (主程序入口)                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Config   │   │ DataLoader│   │Processor  │
    │ (配置层)   │   │ (数据层)  │   │(处理层)   │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │                │                │
          │      ┌─────────┴────────────┐   │
          │      │                      │   │
          └──────┼─────────┬────────────┼───┘
                 │         │            │
          ┌──────▼──┐  ┌───▼─────┐ ┌──▼──────┐
          │ Analysis│  │Utilities │ │Visualize│
          │ (分析)  │  │ (工具)   │ │ (展示)  │
          └──────┬──┘  └───┬─────┘ └──┬──────┘
                 │         │          │
                 └─────────┼──────────┘
                           │
                    ┌──────▼──────┐
                    │ 输出: PNG   │
                    │ CSV / MD    │
                    └─────────────┘
```

---

## 📊 模块依赖关系

```
config.py (0依赖)
   ↑
   ├── utils.py (依赖: config)
   │    ↑
   │    ├── data_loader.py (依赖: utils)
   │    │    ↑
   │    │    ├── data_processor.py (依赖: utils, config)
   │    │    │    ↑
   │    │    │    ├── analysis.py (依赖: utils, config)
   │    │    │    │    ↑
   │    │    │    └─── visualizations.py (依赖: utils, config, analysis)
   │    │    │         ↑
   │    │    └─────────┘
   │    │
   │    └── main.py (依赖: 所有模块)
   │
   └── main.py
```

---

## 🔄 数据流动

### 流程1: 数据加载
```
main.py
  ↓
load_datasets() [data_loader.py]
  ├─ locate_dataset_dir()  # 自动查找
  ├─ read_csv()
  └─ check_data_integrity()  # 验证
  ↓
返回 (raw_df, segmented_df)
```

### 流程2: 数据处理
```
preprocess_dataframe(raw) [data_processor.py]
  ├─ normalize_columns()  [utils.py]
  ├─ 验证必需列
  ├─ add_derived_features()
  │  ├─ 添加 restaurant_id
  │  ├─ 创建 rating_band
  │  ├─ 计算 same_name_outlets
  │  └─ 标记 is_multi_outlet_name
  └─ 返回 df
```

### 流程3: 多值展开
```
create_long_format_data(df) [data_processor.py]
  ├─ explode_attribute(df, "cuisine", "cuisine")  [utils.py]
  │  └─ split_tokens()  [utils.py]
  ├─ explode_attribute(df, "features", "feature")
  └─ explode_attribute(df, "top_dishes", "dish")
  
返回 {
    "cuisine": cuisine_long,
    "feature": feature_long,
    "dish": dish_long,
}
```

### 流程4: 分析计算
```
analyzer = RestaurantAnalyzer(df, long_format_data) [analysis.py]
  ├─ segment_analysis()
  │  └─ df.groupby("market_segment").agg(...)
  ├─ area_analysis()
  │  ├─ pd.crosstab()
  │  └─ entropy_from_counts()  [utils.py]
  ├─ cuisine_analysis()
  ├─ dish_analysis()
  ├─ feature_analysis()
  ├─ chain_analysis()
  └─ rating_distribution()
```

### 流程5: 可视化生成
```
fig = plot_segment_analysis(analyzer) [visualizations.py]
  ├─ analyzer.segment_analysis()
  ├─ 使用 PALETTE  [config.py]
  ├─ 使用 clean_axis()  [utils.py]
  ├─ 使用 add_panel_title()  [utils.py]
  ├─ 使用 label_bar_ends()  [utils.py]
  └─ 返回 matplotlib.figure.Figure

fig.savefig("plot.png")
```

---

## 📦 模块职责矩阵

| 模块 | 主要函数 | 输入 | 输出 | 依赖 |
|------|--------|------|------|------|
| config.py | configure_matplotlib() | - | 全局配置 | - |
| utils.py | split_tokens() | Series | Series | config |
| | normalize_columns() | DataFrame | DataFrame | config |
| | entropy_from_counts() | Series | float | - |
| data_loader.py | load_datasets() | path | DataFrame | utils |
| | locate_dataset_dir() | - | Path | - |
| data_processor.py | preprocess_dataframe() | raw_df | df | utils, config |
| | create_long_format_data() | df | dict | utils |
| | add_derived_features() | df | df | config |
| analysis.py | RestaurantAnalyzer | df, long_data | 分析器 | utils, config |
| visualizations.py | plot_*() | analyzer | Figure | utils, config |
| main.py | main() | - | 输出 | 所有模块 |

---

## 🎯 设计原则

### 1. 单一职责原则 (Single Responsibility)
```python
# ❌ 不好 - 一个文件做太多事
data_and_analyze_and_visualize.py

# ✓ 好 - 每个文件一个职责
config.py           # 配置
data_loader.py      # 加载数据
data_processor.py   # 处理数据
analysis.py         # 分析数据
visualizations.py   # 展示数据
```

### 2. 依赖倒置原则
```python
# ❌ 低级模块依赖高级模块
visualizations.py ──→ main.py

# ✓ 高级模块依赖低级模块
main.py ──→ visualizations.py ──→ analysis.py ──→ utils.py ──→ config.py
```

### 3. 开闭原则 (扩展开放，修改关闭)
```python
# 要添加新的分析方法？只需在 RestaurantAnalyzer 类中添加
# 要添加新的图表？只需在 visualizations.py 中添加
# 不需要修改其他模块！
```

### 4. 关注点分离 (Separation of Concerns)
```
数据流向图:

原始数据
   ↓
[data_loader] ───── 获取CSV
   ↓
未处理的数据
   ↓
[data_processor] ── 清洁、规范化、衍生特征
   ↓
分析就绪的数据
   ↓
┌──────────────────────┐
│ [analysis] ─────────→ 统计计算 → 数据洞察
│ [visualizations] ──→ 图表生成 → 视觉故事
│ [utils] ────────────→ 通用工具 → 支持函数
└──────────────────────┘
   ↓
最终产品 (PNG、CSV、MD)
```

---

## 🔌 扩展点

### 1. 添加新的分析维度
```python
# 在 analysis.py 中添加新方法到 RestaurantAnalyzer 类:

class RestaurantAnalyzer:
    def my_custom_analysis(self):
        """我的自定义分析"""
        result = self.df.groupby("area").apply(my_function)
        return result
```

### 2. 添加新的可视化
```python
# 在 visualizations.py 中添加新函数:

def plot_my_visualization(analyzer):
    """我的自定义图表"""
    fig, ax = plt.subplots()
    # 绘制逻辑
    return fig
```

### 3. 添加新的工具函数
```python
# 在 utils.py 中添加新函数:

def my_helper_function(data):
    """我的辅助函数"""
    return processed_data
```

### 4. 更改配置
```python
# 在 config.py 中修改:

PALETTE["my_color"] = "#123456"
# 或
def my_custom_configure():
    mpl.rcParams.update({...})
```

---

## 🧪 测试策略

### 单元测试示例
```python
# test_utils.py
import unittest
from utils import split_tokens, entropy_from_counts
import pandas as pd
import numpy as np

class TestUtils(unittest.TestCase):
    def test_split_tokens(self):
        s = pd.Series(["A, B, C", "D, E"])
        result = split_tokens(s)
        self.assertEqual(len(result), 5)
    
    def test_entropy_from_counts(self):
        row = pd.Series([1000, 1, 1, 1])
        entropy = entropy_from_counts(row)
        self.assertLess(entropy, 0.5)
```

### 集成测试示例
```python
# test_pipeline.py
from data_loader import load_datasets
from data_processor import preprocess_dataframe
from analysis import RestaurantAnalyzer

def test_full_pipeline():
    raw, _ = load_datasets(verbose=False)
    df = preprocess_dataframe(raw)
    analyzer = RestaurantAnalyzer(df, {})
    
    # 验证结果
    assert len(df) > 0
    assert "restaurant_id" in df.columns
```

---

## 📈 性能优化

### 1. 缓存长格式数据
```python
# 只展开一次，重复使用
long_data = create_long_format_data(df)
analyzer1 = RestaurantAnalyzer(df, long_data)
analyzer2 = RestaurantAnalyzer(df, long_data)  # 重用
```

### 2. 预先计算统计
```python
# 在 analysis.py 中缓存计算结果
report = generate_eda_report(analyzer)
# 所有计算已完成，后续查询都是快速的
```

### 3. 向量化操作
```python
# ✓ 快速 - 向量化操作
df['flag'] = df['rating'] > 3.5

# ❌ 慢速 - 循环迭代
for i, row in df.iterrows():
    df.loc[i, 'flag'] = row['rating'] > 3.5
```

---

## 🔒 数据验证

### 验证管道
```
原始数据
   ↓
check_data_integrity()  # 完整性检查
   ├─ 重复URL检查
   ├─ 缺失值检查
   └─ 结构检查
   ↓
preprocess_dataframe()  # 预处理验证
   ├─ 列名规范化
   ├─ 必需列验证
   └─ 类型转换
   ↓
validate_rating_range()  # 业务规则检查
validate_coordinates()
   ↓
✓ 通过 → 分析就绪

✗ 失败 → 错误报告
```

---

## 📚 代码示例

### 例1: 快速分析 (2行代码)
```python
from main import *
main()  # 执行完整EDA
```

### 例2: 自定义过滤分析
```python
from data_loader import load_datasets
from data_processor import preprocess_dataframe, create_long_format_data
from analysis import RestaurantAnalyzer

raw, _ = load_datasets(verbose=False)
df = preprocess_dataframe(raw)

# 只分析高评分餐厅
high_rated = df[df['rating'] >= 4.0]

long_data = create_long_format_data(high_rated)
analyzer = RestaurantAnalyzer(high_rated, long_data)

print(analyzer.segment_analysis())
```

### 例3: 导出自定义报告
```python
analyzer = RestaurantAnalyzer(df, long_data)
report = {
    "top_cuisines": analyzer.cuisine_analysis().head(10),
    "top_areas": analyzer.area_analysis().head(10),
    "insights": analyzer.generate_insights(),
}

# 保存为JSON
import json
with open("custom_report.json", "w") as f:
    json.dump({k: v.to_dict() for k, v in report.items()}, f)
```

---

## 🚀 部署建议

### 开发环境
```bash
# 虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

### 生产环境 (Docker)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 📊 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-05-14 | 初始版本 - 完整模块化架构 |

---

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/my-feature`)
3. 提交更改 (`git commit -am 'Add feature'`)
4. 推送到分支 (`git push origin feature/my-feature`)
5. 开启 Pull Request

---

**文档版本**: 1.0  
**最后更新**: 2026年5月14日

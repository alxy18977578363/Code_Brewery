# T7：准确率和响应时间评估

## 1. 评估对象

T7 使用以下文件：

- `eval/cases.json`：20 个带 `expected_label` 的离线测试案例。
- `eval/results.json`：T4 规则检测输出。
- `eval/t5_results.json`：T5 根因分析输出，可包含规则回退或模型结果。

评估程序按 `case_id` 匹配文件，不依赖数组顺序。

## 2. 指标口径

### 异常检测准确率

只比较 T4 的 `result.label` 与案例的 `expected_label`：

```text
accuracy = correct_cases / total_cases
accuracy_percent = accuracy × 100
```

根因文字和建议质量暂不自动评分，留给 T8 报告中的人工分析。

### 响应时间

程序从每个结果的 `performance.latency_ms` 读取耗时，分别计算：

- `average`：平均值
- `minimum`：最小值
- `maximum`：最大值
- `median`：中位数

T4 和 T5 的响应时间分开统计，不把规则检测和模型网络耗时混为一个指标。

### 模型使用情况

如果提供 T5 结果，还会统计：

- `model_calls`：`model_used` 为 `true` 的案例数
- `fallback_cases`：使用安全回退的案例数
- `normal_cases_without_model`：正常案例未调用模型的数量
- `rule_cases`：未使用模型的案例数

## 3. 运行命令

完整评估：

```powershell
python src/evaluate_results.py
```

显式指定路径：

```powershell
python src/evaluate_results.py `
  --cases eval/cases.json `
  --t4-results eval/results.json `
  --t5-results eval/t5_results.json `
  --output eval/metrics.json
```

只评估 T4：

```powershell
python src/evaluate_results.py --without-t5
```

输出保存为 `eval/metrics.json`，同时在终端打印准确率和平均响应时间。

## 4. 完成标准

- 20 个案例全部参与评估。
- 案例和结果按 `case_id` 一一匹配。
- 缺失、重复案例或非法耗时会明确报错。
- 输出包含总体指标和逐案例 `case_results`。
- 评估程序不参与 Agent Prompt，不会把测试答案泄露给模型。

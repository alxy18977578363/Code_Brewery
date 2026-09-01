# T4：第一版规则异常检测

## 1. 任务边界

T4 读取 T3 的指标和日志输入，判断服务是否正常，并生成符合
`T3_AGENT_OUTPUT_SCHEMA.md` 的 JSON。T4 不调用大模型、不分析完整根因、不执行修复命令。

## 2. 第一版规则

| 字段或事件 | 规则 | 是否计为异常信号 |
|---|---:|---:|
| `cpu_usage_percent` | `> 80` | 是 |
| `memory_usage_percent` | `> 95` | 是 |
| `disk_usage_percent` | `> 90` | 是 |
| `load_1m` | `> 8` | 是 |
| `response_time_ms` | `> 500` | 是 |
| `error_rate_percent` | `> 5` | 是 |
| `db_connection_usage_percent` | `> 80` | 是 |
| `ERROR` 日志 | 日志级别为 `ERROR` | 是 |
| `WARN` 日志 | 日志级别为 `WARN` | 否，仅作为辅助证据 |
| `request_rate_per_sec` | 第一版不设固定阈值 | 否 |

`load_1m > 8` 是为了覆盖当前演示数据的固定阈值。真实部署时应根据机器 CPU 核数或历史基线调整，不能直接视为所有机器的通用阈值。

等于阈值不算异常，例如 CPU 为 `80` 时不触发，CPU 为 `80.1` 时触发。

## 3. 缺失值处理

指标为 `null` 或不可比较时不触发异常；检测器会在 `evidence.metrics` 中记录
`operator: "missing"` 或 `operator: "invalid"`，并降低正常结论的置信度。

第一版没有 `insufficient_data` 标签，因此数据不足但没有异常信号时仍输出
`normal`，同时在摘要中明确说明“部分指标缺失”。

## 4. 严重程度和置信度

每个超过阈值的指标和每条 `ERROR` 日志计为一个异常信号：

| 信号数量 | `result.severity` |
|---:|---|
| 0 | `normal` |
| 1 | `low` |
| 2-3 | `medium` |
| 4-5 | `high` |
| 6+ | `critical` |

异常置信度使用 `0.75 + 0.05 × 信号数量`，最高为 `0.99`。无异常时，指标完整使用
`0.90`，存在缺失指标使用 `0.65`。

## 5. 程序和命令

主程序：`src/detect_anomalies.py`

处理 20 个案例并在终端输出：

```powershell
python src/detect_anomalies.py eval/cases.json
```

保存为结果文件：

```powershell
python src/detect_anomalies.py eval/cases.json --output eval/results.json
```

输入是单个 JSON 对象时输出单个对象，输入是案例数组时输出同样长度的数组。
程序不会读取或复制输入中的 `expected_label`。

## 6. T4 与 T5 的分工

- T4 填写 `result`、`evidence` 和 `performance`。
- T4 的 `root_causes`、`recommendations` 暂时为空数组。
- T5 在保留检测结果和证据的基础上补充根因与人工确认建议。
- `safety.auto_remediation_allowed` 固定为 `false`，`actions_taken` 固定为空数组。

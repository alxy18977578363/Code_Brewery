# T3 第二版：Agent 标准输出格式

## 1. 设计目标

Agent 每次处理一个输入案例后，必须返回一个 JSON 对象。固定结构便于：

- T4 异常检测读取 `result.label`。
- T5 根因分析和建议读取 `evidence` 并填写 `root_causes`、`recommendations`。
- T7 将 `result.label` 与测试数据中的 `expected_label` 比较。
- 程序记录响应耗时，而不依赖自然语言解析。

运行时输出不得包含输入案例中的 `expected_label`，防止把测试答案泄露给 Agent。

## 2. 完整输出示例

```json
{
  "schema_version": "1.0",
  "case_id": "case-001",
  "analyzed_at": "2026-08-26T10:00:05+08:00",
  "service": {
    "name": "demo-service"
  },
  "result": {
    "label": "abnormal",
    "severity": "high",
    "confidence": 0.96,
    "summary": "CPU、响应时间、错误率和数据库连接使用率同时超过阈值"
  },
  "evidence": {
    "metrics": [
      {
        "name": "cpu_usage_percent",
        "value": 95.2,
        "threshold": 80,
        "operator": ">",
        "reason": "CPU 使用率超过异常阈值"
      },
      {
        "name": "response_time_ms",
        "value": 850,
        "threshold": 500,
        "operator": ">",
        "reason": "响应时间超过异常阈值"
      }
    ],
    "logs": [
      {
        "timestamp": "2026-08-26T10:00:03+08:00",
        "level": "ERROR",
        "source": "database",
        "message": "database connection timeout",
        "reason": "日志显示数据库连接超时"
      }
    ]
  },
  "root_causes": [
    {
      "cause": "数据库连接池接近耗尽，导致请求等待数据库连接",
      "confidence": 0.82,
      "evidence_refs": [
        "metrics.db_connection_usage_percent",
        "logs[0]"
      ]
    }
  ],
  "recommendations": [
    {
      "priority": "P1",
      "action": "检查数据库连接池上限、活动连接和慢查询",
      "rationale": "先确认数据库连接是否为主要瓶颈",
      "requires_approval": true
    }
  ],
  "safety": {
    "auto_remediation_allowed": false,
    "actions_taken": []
  },
  "performance": {
    "latency_ms": 1032,
    "detector": "rule-v1",
    "model_used": false,
    "model_name": null
  }
}
```

## 3. 字段约定

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `schema_version` | string | 是 | 输出格式版本，当前为 `1.0` |
| `case_id` | string | 是 | 与输入案例对应的唯一编号 |
| `analyzed_at` | ISO 8601 string | 是 | Agent 完成分析的时间 |
| `service.name` | string | 是 | 被分析的服务名称 |
| `result.label` | string | 是 | 只能是 `normal` 或 `abnormal` |
| `result.severity` | string | 是 | `normal`、`low`、`medium`、`high` 或 `critical` |
| `result.confidence` | number | 是 | 0 到 1 之间的置信度 |
| `result.summary` | string | 是 | 面向用户的简短结论 |
| `evidence.metrics` | array | 是 | 支持结论的指标证据，可为空数组 |
| `evidence.logs` | array | 是 | 支持结论的日志证据，可为空数组 |
| `root_causes` | array | 是 | 推测的根因；T4 阶段可以为空 |
| `recommendations` | array | 是 | 修复或排查建议；T4 阶段可以为空 |
| `safety` | object | 是 | 安全控制信息，禁止自动执行危险修复 |
| `performance` | object | 是 | 检测器、模型和响应耗时信息 |

## 4. 证据格式

指标证据对象包含：

- `name`：必须是输入中的指标名称。
- `value`：原始数值，也可以是 `null`。
- `threshold`：用于比较的阈值；无法比较时使用 `null`。
- `operator`：例如 `>`、`>=` 或 `missing`。
- `reason`：为什么该指标支持或不支持异常结论。

日志证据对象保留输入日志的 `timestamp`、`level`、`source`、`message`，并增加 `reason` 说明其意义。

## 5. 根因与建议

`root_causes` 和 `recommendations` 必须使用数组，即使只有一项或暂无内容也不能改成字符串或 `null`。

- `root_causes[].confidence` 范围为 0 到 1。
- `root_causes[].evidence_refs` 使用字段路径引用证据，例如 `metrics.cpu_usage_percent`、`logs[0]`。
- `recommendations[].priority` 只能使用 `P1`、`P2` 或 `P3`。
- `requires_approval` 固定为 `true`，表示建议需要人工确认，Agent 不直接执行命令。

## 6. T4 与 T5 的使用方式

- T4 只负责填写 `result`、`evidence` 和 `performance`；`root_causes`、`recommendations` 使用空数组。
- T5 在不改变 `result` 和证据的前提下补充根因与建议。
- `safety.auto_remediation_allowed` 当前固定为 `false`，`actions_taken` 当前固定为空数组。
- 如果模型调用失败，也必须返回合法 JSON，并在 `result.summary` 或 `performance` 中说明失败，不得返回无法解析的散文文本。

## 7. 评估规则

离线评估时只比较：

```text
输出.result.label == 输入.expected_label
```

`summary`、根因和建议用于人工检查，不直接参与第一版准确率计算。

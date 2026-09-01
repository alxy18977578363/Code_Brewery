# T3 第一版：指标与输入格式设计

## 1. 设计目标

本项目使用“一次观测快照”作为 Agent 的一次输入。每个快照描述某个服务在一个时间点的运行状态，包含基本信息、监控指标、日志和测试标签。

## 2. 完整输入格式

```json
{
  "schema_version": "1.0",
  "case_id": "case-001",
  "observed_at": "2026-08-26T10:00:00+08:00",
  "service": {
    "name": "demo-service"
  },
  "metrics": {
    "cpu_usage_percent": 95.2,
    "memory_usage_percent": 87.4,
    "disk_usage_percent": 63.1,
    "load_1m": 4.8,
    "request_rate_per_sec": 120.5,
    "response_time_ms": 850,
    "error_rate_percent": 8.5,
    "db_connection_usage_percent": 92.0
  },
  "logs": [
    {
      "timestamp": "2026-08-26T10:00:03+08:00",
      "level": "ERROR",
      "source": "database",
      "message": "database connection timeout"
    }
  ],
  "expected_label": "abnormal"
}
```

## 3. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `schema_version` | string | 是 | 输入格式版本，当前为 `1.0` |
| `case_id` | string | 是 | 案例唯一编号 |
| `observed_at` | ISO 8601 string | 是 | 指标快照采集时间 |
| `service` | object | 是 | 服务基本信息 |
| `service.name` | string | 是 | 服务名称 |
| `metrics` | object | 是 | 指标集合 |
| `logs` | array | 是 | 该时间点相关日志，可为空数组 |
| `expected_label` | string | 测试时是 | 正确标签：`normal` 或 `abnormal` |

## 4. 指标字段

| 指标 | 类型 | 合法范围/单位 |
|---|---|---|
| `cpu_usage_percent` | number/null | 0-100% |
| `memory_usage_percent` | number/null | 0-100% |
| `disk_usage_percent` | number/null | 0-100% |
| `load_1m` | number/null | >= 0，无单位 |
| `request_rate_per_sec` | number/null | >= 0 次/秒 |
| `response_time_ms` | number/null | >= 0 毫秒 |
| `error_rate_percent` | number/null | 0-100% |
| `db_connection_usage_percent` | number/null | 0-100% |

暂时没有数据时使用 `null`，不要把单位写进字符串，例如使用 `95.2`，不要使用 `"95.2%"`。

## 5. 日志字段

每条日志包含：

- `timestamp`：ISO 8601 时间字符串。
- `level`：`DEBUG`、`INFO`、`WARN` 或 `ERROR`。
- `source`：日志来源，例如 `application`、`database`、`system`。
- `message`：日志文本。

## 6. 测试标签

`expected_label` 仅用于离线测试和计算检测准确率。真实运行时可以省略，因为真实系统不会提前提供正确答案。

## 7. 第一版规则参考

这些阈值供 T4 异常检测使用，不在 T3 中执行：

- CPU 使用率 > 80%：疑似异常。
- 内存使用率 > 85%：疑似异常。
- 磁盘使用率 > 90%：疑似异常。
- 响应时间 > 500ms：疑似异常。
- 错误率 > 5%：疑似异常。
- 数据库连接使用率 > 80%：疑似异常。
- 出现 `ERROR` 日志：需要进一步分析。

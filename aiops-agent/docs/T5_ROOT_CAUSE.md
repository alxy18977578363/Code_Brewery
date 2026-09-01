# T5：根因分析和安全建议

## 1. 任务边界

T5 读取 T4 的标准 JSON 输出，解释异常可能原因，并生成需要人工确认的排查建议。
T5 不改变 T4 的 `result` 和 `evidence`，不执行命令，也不进行自动修复。

## 2. 分析流程

```text
T4 result/evidence
  ↓
规则生成候选根因
  ↓
（可选）调用模型进行解释和排序
  ↓
验证模型 JSON 和安全性
  ↓ 失败时
规则回退
  ↓
补充 root_causes 和 recommendations
```

正常案例不调用模型，直接输出空的 `root_causes` 和 `recommendations`。异常案例默认使用安全的规则回退；加入 `--use-model` 才会调用 `.env` 中配置的 OpenAI-compatible 接口。

## 3. 规则候选原因

第一版使用指标和日志的组合生成候选原因：

- CPU 或负载过高：计算资源饱和或并发压力。
- 内存过高：内存压力、缓存过大或内存增长。
- 磁盘过高：日志、临时文件或业务数据持续占用空间。
- 响应时间和数据库连接同时异常：连接池紧张或慢查询。
- 错误率或 `ERROR` 日志：应用组件或上游依赖发生失败。

候选原因最多保留 3 个，必须引用 T4 的真实证据路径。

## 4. 模型输出约束

模型只返回：

```json
{
  "root_causes": [],
  "recommendations": []
}
```

程序会检查字段类型、数量、置信度、证据引用、优先级和 `requires_approval`。模型输出中的删除、停机、重启生产服务、修改系统服务或其他危险操作会被拒绝，并改用规则回退。

Prompt 模板见 `docs/prompts/T5_ROOT_CAUSE_PROMPT.md`。

## 5. 安全回退

模型不可用、超时、返回非法 JSON 或未通过安全检查时：

- 使用规则生成根因和建议。
- 输出仍保持合法标准 JSON。
- `performance.detector` 标记为 `rule-v1-fallback`。
- `performance.model_used` 为 `false`。
- 建议的 `requires_approval` 固定为 `true`。

回退建议只包含人工检查动作，例如检查日志、连接池、慢查询、线程和资源趋势，不包含可直接执行的危险命令。

## 6. 运行命令

先生成 T4 结果：

```powershell
python src/detect_anomalies.py eval/cases.json --output eval/results.json
```

离线运行 T5（不调用模型）：

```powershell
python src/analyze_root_cause.py eval/results.json --output eval/t5_results.json
```

使用 `.env` 配置的模型分析异常案例：

```powershell
python src/analyze_root_cause.py eval/results.json --use-model --output eval/t5_results.json
```

为避免一次批量调用模型，可以只分析一个案例：

```powershell
python src/analyze_root_cause.py eval/results.json --case-id case-011 --use-model --output eval/t5-case-011.json
```

API Key 只从环境变量或本机 `.env` 读取，不会写入输出文件或日志。

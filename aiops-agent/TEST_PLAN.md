# 测试要求

至少准备 20 个案例，包括：

- 正常 CPU 和内存
- CPU 过高
- 内存过高
- 数据库连接超时
- 磁盘空间不足
- 大量错误日志
- 多种异常同时发生

每个案例必须包含：

- 输入指标
- 输入日志
- 正确标签
- 期望输出类型

期望输出类型为符合 `docs/T3_AGENT_OUTPUT_SCHEMA.md` 的 JSON 对象。评估时比较
`result.label` 与案例的 `expected_label`，不要求摘要、根因和建议使用固定自然语言。

## T4 异常检测

运行规则检测器：

```powershell
python src/detect_anomalies.py eval/cases.json --output eval/results.json
```

运行 T4 自动化测试：

```powershell
python -m unittest tests.test_detect_anomalies -v
```

T4 测试检查阈值边界、指标和日志证据、`null` 指标、20 个案例的标签、标准输出字段以及安全开关。

## T5 根因分析

离线规则回退测试：

```powershell
python src/analyze_root_cause.py eval/results.json --output eval/t5_results.json
```

可选模型分析（仅异常案例会调用模型）：

```powershell
python src/analyze_root_cause.py eval/results.json --use-model --output eval/t5_results.json
```

单案例模型集成测试：

```powershell
python src/analyze_root_cause.py eval/results.json --case-id case-011 --use-model --output eval/t5-case-011.json
```

T5 测试检查规则候选根因、模型 JSON 合并、非法模型结果回退、证据引用、`expected_label` 隔离和危险建议拦截。

## T7 评估

生成 T4/T5 结果后运行：

```powershell
python src/evaluate_results.py
```

结果写入 `eval/metrics.json`。评估程序按 `case_id` 匹配 20 个案例，计算准确率以及 T4/T5 的平均、最小、最大和中位响应时间。

## T8 AIOps 分析 API

启动本地 API：

```powershell
python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000
```

接口测试运行：

```powershell
python -m unittest tests.test_result_store tests.test_api_server -v
```

T8 测试检查 API 健康状态、T3 输入校验、正常与异常案例分析、SQLite 历史结果、未知 ID 的 404 响应、`expected_label` 隔离和禁止自动修复。

## T9 本机采集

查看一次本机采集结果：

```powershell
python src/collect_local.py
```

自动化测试运行：

```powershell
python -m unittest tests.test_local_collector tests.test_api_server -v
```

T9 测试检查 CPU、内存和磁盘指标转换，固定项目日志文件中的 WARN/ERROR 筛选，日志缺失时的安全行为，以及 `POST /api/collect-now` 的提交和分析流程。

## T10 FreeAiOps 适配

接口测试运行：

```powershell
python -m unittest tests.test_freeaiops_adapter tests.test_api_server -v
```

T10 测试检查 FreeAiOps 健康接口 HTTP 200、网络错误降级、状态接口输出、分析结果关联状态，以及 FreeAiOps 不可用时 T4/T5 仍可完成。

## T11 实时控制台

前端语法检查：

```powershell
node --check web/app.js
```

启动 API 后访问 `http://127.0.0.1:8000/`，确认页面加载后自动调用一次 `/api/collect-now`，并显示本机指标、分析结论、FreeAiOps 状态和最近分析记录。点击历史记录应能恢复对应观测、日志、根因和建议；API 不可用时应显示明确提示。

同时确认左侧四个视图可切换，实时监控的自动检测开关、暂停/继续、频率选择和立即检测按钮可用；页面切到后台时不继续轮询。

记录交互检查：历史分析表和测试案例表的记录悬停时有可点击反馈，点击后弹出记录名片，展示实际指标、阈值及红/绿/灰状态条；遮罩、关闭按钮和 `Esc` 可关闭名片。

## T3 格式校验

运行：

```powershell
python src/validate_cases.py eval/cases.json --require-label
```

校验程序检查 JSON 结构、必填字段、指标类型和范围、日志字段、时间格式、测试标签以及案例 ID 唯一性。

自动化测试运行：

```powershell
python -m unittest discover -s tests -v
```


# 交付信息留存
请每次在制作时，在
当前任务：T10
状态：已完成

本次修改：
- `src/freeaiops_adapter.py`、`src/api_server.py`：提供 FreeAiOps 只读健康适配和关联状态接口。
- `tests/test_freeaiops_adapter.py`、`tests/test_api_server.py`：覆盖在线、不可达、降级和分析继续运行。

测试：
- 执行命令：`python -m unittest discover -s tests -v`
- 测试结果：41 项通过；FreeAiOps 适配、真实本机采集和 HTTP 采集分析均通过。
- 未通过项目：无。

当前风险：
- FreeAiOps 当前只接入健康状态；业务告警和任务接口尚未确认，因此不做伪造集成。

下一步：
- T11：将网页升级为实时 AIOps 控制台
- 前置条件：T8/T9 API、采集流程和 T10 FreeAiOps 状态适配已完成

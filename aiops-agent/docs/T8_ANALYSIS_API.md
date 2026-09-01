# T8：AIOps 分析 API 和结果存储

## 作用

T8 将已有的 T3 输入校验、T4 异常检测和 T5 根因分析封装为本地 HTTP API。它使用项目自己的 SQLite 数据库保存观测和结果，不使用或修改 FreeAiOps 的 MySQL 数据库。

默认只运行规则分析。请求中明确传入 `use_model: true` 时，异常案例才会尝试使用本机 `.env` 或环境变量中的模型配置；模型失败时自动使用安全规则回退。

## 安装和启动

```powershell
Set-Location 'E:\December\Desktop\aiops-agent'
python -m pip install -r requirements.txt
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_api.ps1
```

浏览器打开 `http://127.0.0.1:8000/docs` 可以查看并测试接口。运行时数据库位于 `runtime/aiops.db`，该目录不会提交到 Git。

正常使用请打开 `http://127.0.0.1:8000/`。该地址会显示 AIOps 操作界面；`/docs` 仅保留给开发调试。

## 接口

- `GET /api/health`：检查本项目 API 和 SQLite 存储是否已启动。
- `POST /api/observations`：提交一条符合 T3 1.0 格式的观测数据，返回 `observation_id`。
- `POST /api/analyze`：传入 `observation_id`，运行 T4 和 T5，返回分析结果和 `analysis_id`。
- `POST /api/analyze-now`：一次提交观测并完成 T4/T5，供简单操作页面使用，不需要用户处理 ID。
- `GET /api/results/latest`：读取最近一次结果，包含原始观测、分析和关联的 FreeAiOps 状态。
- `GET /api/results/{analysis_id}`：读取指定历史结果及其原始观测和 FreeAiOps 状态。
- `GET /api/results?limit=20`：读取最近的多条结果，供实时控制台展示历史记录。
- `POST /api/ai/ask`：提交 `{ "question": "...", "include_latest": true, "analysis_id": "analysis-..." }`，由服务端调用 `.env` 中配置的模型并返回回答、模型名称、耗时和安全状态；传入 `analysis_id` 时使用指定历史记录作为上下文；未配置模型返回 `503`，模型请求失败返回 `502`。
- `POST /api/fault-detection`：提交 `{ "observation": { ... } }`，接收符合 T3 格式的指标和日志，运行 T4/T5 并返回 `report_type: fault_detection` 的结构化检测报告，同时保存到 SQLite；非法输入返回 `422`。

提交观测时，`expected_label` 可以存在于离线测试案例中，但 API 会在保存和分析前移除它，确保测试答案不会进入 T4、T5、模型提示词或接口输出。

## 安全边界

- API Key 不会写入 SQLite、响应体或日志。
- `auto_remediation_allowed` 固定为 `false`，`actions_taken` 固定为空数组。
- API 不执行删除、停机、重启、修改系统服务或自动修复命令。
- FreeAiOps 业务状态适配属于 T10；本任务不调用其业务接口。

## 测试

```powershell
python -m unittest tests.test_result_store tests.test_api_server -v
python -m unittest discover -s tests -v
```

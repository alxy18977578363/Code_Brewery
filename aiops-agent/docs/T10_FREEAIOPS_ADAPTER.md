# T10：FreeAiOps 状态与任务适配层

## 目标

T10 将已启动的 FreeAiOps 纳入项目可见运行链路，但保持只读边界。适配层只请求 FreeAiOps 的公开健康接口 `GET /health`，不提交观测、不创建任务、不修改 FreeAiOps 数据。

## 接口

- `GET /api/freeaiops/status`：返回 `online`（2xx）、`degraded`（可达但为 4xx/5xx）或 `offline`（连接失败/超时），并包含检查时间、HTTP 状态、健康检查地址和耗时。
- `POST /api/collect-now`、`POST /api/analyze-now`：分析响应附带本次关联的 `freeaiops` 状态。
- `GET /api/results/latest`、`GET /api/results`：历史分析记录包含执行该分析时保存的 `freeaiops` 状态（旧记录没有该字段时仍可正常读取）。

健康检查默认超时为 0.5 秒，适合实时控制台的高频轮询；可在单元测试或特殊网络环境中通过构造函数覆盖。

FreeAiOps 地址默认是 `http://127.0.0.1:8080`，也可以通过本机环境变量 `FREEAIOPS_BASE_URL` 指定，不写入网页或分析结果中的密钥信息。

## 降级行为

FreeAiOps 未启动、超时或返回错误时，状态标记为 `offline`，但本项目的 T4/T5 分析仍然继续完成。网页会显示离线状态，不会阻断本地分析。

## 当前边界

FreeAiOps 的业务告警、任务编排等接口没有在本项目中假定或伪造。若后续确认了安全、稳定的业务接口，再单独设计扩展；当前 T10 只证明 FreeAiOps 在线状态并将其关联到分析记录。

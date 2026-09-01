# 项目文档索引

本目录集中存放 T2/T3 的接口、数据格式和 Agent 输出约定，避免项目根目录堆放过程文档。

## 文档

- [T2 模型接口说明](T2_MODEL_API.md)：模型配置项、API 连通性测试和预期结果。
- [T3 指标与日志输入格式](T3_METRIC_SCHEMA.md)：Agent 的输入快照格式、指标范围和日志字段。
- [T3 Agent 标准输出格式](T3_AGENT_OUTPUT_SCHEMA.md)：异常判断、证据、根因、建议、安全和性能字段。
- [T4 异常检测说明](T4_ANOMALY_DETECTION.md)：规则阈值、严重程度和检测命令。
- [T5 根因分析说明](T5_ROOT_CAUSE.md)：规则候选、模型调用、安全校验和回退机制。
- [T7 评估说明](T7_EVALUATION.md)：准确率、延迟和模型使用情况统计。
- [T8 分析 API 说明](T8_ANALYSIS_API.md)：本地 HTTP 接口、SQLite 结果存储和运行方法。
- [T9 本机采集说明](T9_LOCAL_COLLECTION.md)：允许采集的数据、日志边界和一键分析方式。
- [T10 FreeAiOps 适配说明](T10_FREEAIOPS_ADAPTER.md)：健康状态、降级行为和只读边界。

## 关联目录

- `eval/`：离线评估案例数据。
- `src/`：输入校验和后续检测代码。
- `tests/`：自动化测试。
- `scripts/`：运行和接口测试脚本。

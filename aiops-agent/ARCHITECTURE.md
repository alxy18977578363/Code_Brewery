# 项目架构说明

## T3 第一版数据流

```text
一次观测快照
  ├─ 基本信息：schema_version、case_id、observed_at、service
  ├─ metrics：8 个监控指标
  ├─ logs：0 条或多条日志
  └─ expected_label：仅测试数据使用
```

T4 将读取 `metrics` 和 `logs`，先执行异常检测；T5 再将检测证据交给 Agent 分析原因并生成建议。

## T3 Agent 输出数据流

```text
输入快照
  -> T4 异常检测
  -> 标准 JSON 输出
       ├─ result：normal/abnormal、严重程度、置信度、摘要
       ├─ evidence：指标和日志证据
       ├─ root_causes：T5 填写的根因数组
       ├─ recommendations：T5 填写的建议数组
       ├─ safety：禁止自动修复
       └─ performance：检测器、模型和耗时
```

标准字段和示例见 `docs/T3_AGENT_OUTPUT_SCHEMA.md`。离线评估只将输出的
`result.label` 与输入的 `expected_label` 比较。

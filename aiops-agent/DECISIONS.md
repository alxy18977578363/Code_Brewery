# 技术决定

## 2026-08-21

选择 FreeAiOps，不选择 AIOpsLab。

原因：

- FreeAiOps 更适合当前时间和基础水平。
- AIOpsLab 需要 Kubernetes、kind 和微服务故障注入。
- 当前项目只实现检测、分析和建议。

暂不使用自动修复，避免执行危险命令。
# 2026-09-01 - 完成课程设计报告终稿

- 生成可编辑终稿 `report/AIOps课程设计报告终稿.docx`，根据 `REPORT_OUTLINE.md` 完成 12 章正文、参考文献和附录，插入 assets 中 14 类截图（17 个内嵌实例）。
- 新增 `report/AIOps课程设计报告.tex`，遵循 graduate_report_skill 中文模板结构，补充 AIOps、日志异常检测、根因分析和工程组件引用。
- 新增 `report/mermaid/architecture.mmd` 与 `report/mermaid/sequence.mmd`，架构图、数据链路和时序流程使用 Mermaid 源码表达。
- Word 结构审计：31 个显式分页（最低 32 页）、17 个图片实例、73 个标题、9 个表格；图片 alt 文本和表头标记已补齐；占位符扫描为 0。
- 最新回归验证：`python -m unittest discover -s tests -v` 共 50 项通过，`node --check web/app.js` 和 T3 案例格式校验通过。
- 使用 ReportLab 将 Word 终稿渲染为 `report/AIOps课程设计报告终稿.pdf`，PDF 共 42 页、约 1.46 MB；Poppler 已成功栅格化全部页面并抽查封面、正文、截图页和附录，中文字体与图片显示正常。
- 按 documents 技能尝试渲染 DOCX，但当前环境没有 LibreOffice/soffice，无法生成 PNG/PDF 视觉检查结果；未将渲染失败伪装为通过。

# 2026-08-30

- 优化 T8/T11 使用体验：新增 `/api/analyze-now` 单次提交分析接口。
- 在网页增加“实时分析”操作区，隐藏 observation_id 和多步 API 细节，支持指标填写、正常/异常示例和结果展示。
- 验证前端 HTTP 200、API 新接口和异常案例一键分析；原有自动化测试继续通过。
- 将网页和 `eval` 数据挂载到同一 API 服务，访问 `http://127.0.0.1:8000/` 即可打开操作界面，不再要求启动第二个网页终端。
- 完成 T9：新增本机 CPU、内存、项目所在磁盘采集，以及固定项目日志 `runtime/local_events.log` 的 WARN/ERROR 读取。
- 新增本机采集预览和一键采集分析接口，并在网页提供“采集本机数据”按钮；不扫描用户目录，无法采集的业务指标使用 `null`。
- 完成 T10：新增 FreeAiOps 只读健康适配层、状态接口和分析结果关联；FreeAiOps 不可用时本地分析安全降级。
- 完善 T10：将 FreeAiOps 状态持久化到 SQLite 分析记录；区分可达但异常的 `degraded` 与连接失败的 `offline`，并补充 HTTP 503、历史结果关联和兼容旧数据库的测试。
- 完成 T11：网页新增实时本机指标、最近分析历史和 FreeAiOps 状态展示；实时区域从 T8 API 读取并在采集/分析后自动刷新，保留 20 案例离线评估区域。
- T11 验证：`node --check web/app.js` 通过，后端 44 项测试通过，备用端口 HTTP 联调确认网页和历史结果接口正常。
- T11 体验优化：网页加载完成后自动执行一次本机采集和分析，无需用户先点击按钮或手动刷新；手动采集入口仍保留。
- 修复自动采集未生效风险：为 `app.js` 增加缓存版本号，并让首次采集独立于评估数据初始化流程启动；兼容旧 HTML 时不因实时刷新按钮缺失而中断脚本。
- 增加持续自动检测：网页打开立即采集一次，之后每 1 秒自动采集并分析；页面不可见时暂停轮询，且避免并发采集请求。
- 将 FreeAiOps 健康检查默认超时从 2 秒降为 0.5 秒，避免 FreeAiOps 离线时拖慢 1 秒轮询。
- 重构 T11 网页布局：拆分实时监控、历史分析、测试案例和系统状态四个视图，增加自动检测开关、暂停/继续、频率选择、资源趋势和最新状态面板。
- 更新网页回归断言并验证新控制台由 API 进程正常返回。
- 新增 AI 助手视图和 `/api/ai/ask` 问答接口：支持结合最近分析结果提问，模型密钥只在服务端读取，回答强制标注人工确认和禁止自动修复。
- 优化 AI 助手：安全渲染 Markdown、增加可滚动历史记录选择、常用问题示例、复制回答和清空对话；问答支持指定 `analysis_id` 上下文。
- 修复手动分析结果被自动采集覆盖的问题：自动检测不再调用手动结果渲染，只更新实时监控和历史记录。
- 更新前端脚本缓存版本，确保浏览器加载手动/自动分析隔离后的最新逻辑。
- 新增记录详情名片：历史记录与测试案例悬停显示可点击提示，点击后查看指标实际值、阈值和红绿状态条，并支持遮罩/关闭键退出。
- 手动分析异常示例改为随机生成：每次随机选择 1-3 个指标超过规则阈值，保证至少触发一个异常信号。
- 随机异常案例验证：连续生成 100 次，异常指标数量始终为 1-3 个，且每次数据均不同。
- 新增故障检测场景接口 `/api/fault-detection`：接收指标/日志后自动判断异常并输出结构化检测报告；网页手动入口已切换到该接口。
- 增加独立“故障检测”导航入口，点击后直接定位到手动故障检测表单。

# 2026-08-29

- 完成 T8：新增 FastAPI 本地分析接口，支持提交 T3 观测、运行 T4/T5、读取历史结果和健康检查。
- 新增 SQLite 结果存储，运行时数据位于 `runtime/aiops.db`，与 FreeAiOps MySQL 保持独立。
- 新增 T8 接口和存储自动化测试；默认不调用模型，且 API 输出隔离 `expected_label` 并固定禁止自动修复。
- 增加简化实时分析界面：网页通过 `/api/analyze-now` 一次完成提交和分析，用户无需接触 Swagger、observation_id 或多步 API。

# 2026-08-26

- 完成 T1：使用 GitHub 版本 FreeAiOps，目录为 `framework/FreeAiOps`。
- 在 WSL2 Ubuntu 中启动 FreeAiOps，并连接 Docker MySQL 容器 `freeaiops-mysql-3307`。
- 已验证 `http://localhost:8080/health` 返回 HTTP 200 和 `"ok..."`。
- 完成 T2：使用 `.env` 中的配置测试 DeepSeek 兼容接口，返回 HTTP 200、`MODEL_API_OK`，响应约 1032 ms。
- T3 新增输入格式校验程序 `src/validate_cases.py`，并添加标准库自动化测试；当前案例可校验通过。
- T3 测试数据已扩展至 20 个案例，覆盖正常状态、单项指标异常、多指标组合异常、日志异常和 `null` 指标。
- T3 确定 Agent 标准 JSON 输出格式，包含判断结果、证据、根因、建议、安全控制和性能信息。
- 整理 T2/T3 文档至 `docs/` 目录，并新增文档索引，保持根目录清晰。
- 完成 T4 第一版规则异常检测：支持指标阈值、ERROR/WARN 日志证据、缺失指标处理、标准 JSON 输出和 20 个案例批量检测。
- 完成 T5 根因分析第一版：支持规则候选原因、可选模型解释、模型 JSON 校验、安全回退和人工确认建议。
- 完成 T7 评估程序：按 `case_id` 计算 20 个案例的准确率、T4/T5 延迟统计和模型使用情况，并生成 `eval/metrics.json`。
- 新增 `web/` 本地 AIOps 可视化控制台原型，可展示评估指标、案例证据、根因和 AI 建议。
- 按参考后台管理界面重做网页视觉：浅色布局、左侧导航、概览卡片、指标趋势图和告警列表。
- 根据实际功能收敛网页内容：移除虚构的主机、流量和日期控件，改为展示真实评估统计，并保留案例筛选、详情查看和刷新数据交互。
- 修复左侧导航交互：点击后当前模块高亮，其他导航项恢复暗色，并保留页面锚点跳转。
- 调整后续任务规划：新增 T8-T11，用于 AIOps API、真实指标与日志采集、FreeAiOps 状态适配和实时网页；原报告、演示视频、最终检查顺延为 T12-T14。
- 完成完整 AIOps 运行环境补充：启动 Docker Desktop，部署 Demo 微服务和 MySQL，使用 WSL2 启动 FreeAiOps 并完成数据库迁移；Agent 可读取 Demo `/metrics` 与日志，调用已配置的 DeepSeek 兼容 LLM，网页显示完整链路。
- 新增 `docker-compose.yml`、`demo_service/app.py`、`demo_service/Dockerfile` 和 `scripts/run_freeaiops.ps1`；`run_api.ps1` 自动解析 WSL2 地址作为 FreeAiOps 健康检查目标。
- 网页系统状态新增完整链路卡片，显示 Demo 微服务、Agent 采集、FreeAiOps 和 LLM 的当前状态。
- 新增 `scripts/start_all.ps1`，支持一次命令启动并检查 Docker、Demo、MySQL、WSL2 FreeAiOps 和 Agent API；已运行的组件会复用，不重复启动。
## 2026-08-31 - FreeAiOps event pipeline

- Added a compatibility event envelope in `src/freeaiops_adapter.py` that
  publishes abnormal observations to FreeAiOps' `/api/v1/app` endpoint and
  retrieves them before T5 analysis.
- Added `GET /api/freeaiops/events` for read-only dashboard access.
- Runtime analyses now expose event publish/retrieval status in the saved
  `freeaiops` metadata. Healthy one-second samples are not sent as events.
- Added an optional “规则检测 + AI 诊断” mode to the quick analysis form.
- FreeAiOps source code remains unchanged.
## 2026-08-31 - 实时监控工作台增强

- 实时监控页新增服务概览、异常信号和事件链路三个信息面板。
- 监控卡片补充系统负载、响应时间、错误率和数据库连接使用率。
- 新增 FreeAiOps 事件去重：同一异常指纹只上报一次，恢复正常后才允许再次上报。
## 2026-08-31 - 修复 WSL2 启动命令

- 新增 `scripts/run_freeaiops_wsl.sh`，在 Bash 内设置 `EWA_CONFIG` 并切换到 FreeAiOps 的 Go 模块目录。
- `run_freeaiops.ps1` 和 `start_all.ps1` 不再把 Linux `export` 嵌入 PowerShell 字符串，避免 `export` 被误识别为 PowerShell 命令。
- 已验证数据库迁移和 FreeAiOps 服务可正常启动。
## 2026-08-31 - 事件去重状态展示

- 相同异常指纹在持续监控期间会被标记为 `deduplicated`，不会重复创建 FreeAiOps 事件。
- 实时监控页面将显示“已去重 · 既有事件”，避免将正常的去重行为误认为写入失败。

## 2026-08-31 - 完成课程报告提纲

- 根据课程设计 PDF、当前代码、架构文档和评测结果补充 `REPORT_OUTLINE.md`。
- 提纲覆盖项目背景、需求、安全边界、技术选型、数据流、部署、Agent 实现、网页、测试评估、演示、局限与改进、参考文献和附录。
- 明确记录 20 个案例准确率 100%、T4/T5 规则路径耗时、48 项自动化测试，以及 FreeAiOps 与本项目 T4/T5 的职责边界。

## 2026-09-01 - 按意见优化报告提纲

- 将报告中的任务编号改为直接描述对应技术和功能，便于课程报告阅读。
- 保留真实实现、评测数据、接口名称和文件证据，未修改业务代码。

## 2026-09-01 - 补充报告能力与环境章节

- 在 `REPORT_OUTLINE.md` 中明确写出故障检测和 Log+Metric 根因分析两个已实现应用场景。
- 扩展技术方案选型理由、Agent 分层设计、测试结果讨论和困难解决过程总结。
- 按课程环境要求补充 Python、Docker、MySQL、WSL2、FreeAiOps、LLM 的配置说明；缺少截图或现场输出的位置使用红色待补充占位。

## 2026-09-01 - 生成 IEEEtran 30 页 PDF 终稿

- 按 graduate-report-skill 原始论文风格重写并扩充 `report/AIOps课程设计报告.tex`，保留 IEEEtran 双栏正文和 Mermaid 源码说明。
- 新增 `report/appendix_extra.tex`，补充分析状态机、部署复现、Docker/WSL2 配置、T3/T4/T5 字段契约、请求响应样例、20 个案例逐案表、50 项测试矩阵、性能解释、故障时间线、安全威胁模型、代码阅读和后续实验设计。
- 使用 MiKTeX XeLaTeX 连续编译两遍，退出码均为 0，生成 30 页 `report/latex_build/AIOps课程设计报告.pdf`，并覆盖复制为 `report/AIOps课程设计报告终稿.pdf`。
- 使用 Poppler 栅格化抽查首页、方法页、部署页和附录末页；未发现致命排版错误。长英文标识符存在少量 overfull/underfull 提示，但不影响阅读。
- 最新自动化验证：50 项 unittest 全部通过，`node --check web/app.js` 通过，T3 案例校验通过。

## 2026-09-01 - 生成课程报告 Word 初稿

- 根据报告提纲生成可编辑文件 `report/AIOps课程设计报告初稿.docx`，包含封面、目录、正文、表格、命令示例和附录。
- 报告明确包含故障检测和 Log+Metric 根因分析两个场景，并保留 20 案例、100% 准确率、48 项测试等实际结果。
- 缺少现场截图、命令输出或模型调用凭证的位置使用红色占位，便于后续补录。
- 已完成 DOCX 结构检查；当前环境缺少 LibreOffice/soffice，暂未完成 PNG 视觉渲染检查。

## 2026-09-01 - 重构技术演示稿重点

- 重写 `PRESENTATION_SCRIPT.md`，将演示主线调整为“问题与目标 → 整体技术架构 → 核心设计与个人实现 → 两个应用场景 → 界面使用 → 测试与总结”。
- 减少连续命令和具体操作的篇幅，增加统一数据结构、检测与分析分层、FreeAiOps 适配、异常去重、安全降级等个人设计说明。
- 将网页演示改为面向用户的使用讲解，说明实时监控、故障检测、AI 助手和历史诊断书分别如何帮助排查问题。

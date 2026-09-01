# 任务清单

- [×] T0 安装 Python、Git、Docker
- [x] T1 下载并启动 FreeAiOps
- [x] T2 确认模型接口可用
- [x] T3 定义日志和指标 JSON 格式
- [x] T4 实现异常检测
- [x] T5 实现根因分析和修复建议
- [x] T6 准备至少 20 个测试案例
- [x] T7 计算准确率和平均响应时间
- [x] T8 实现 AIOps 分析 API 和结果存储
- [x] T9 接入真实本机指标和日志采集
- [x] T10 接入 FreeAiOps 状态与任务适配层
- [x] T11 将网页升级为实时 AIOps 控制台
- [x] T12 整理报告
- [ ] T13 录制演示视频（演讲稿已完成，见 PRESENTATION_SCRIPT.md）
- [ ] T14 检查并提交文件

## 完整 AIOps 运行环境补充（T11 扩展）

- [x] Docker Desktop 引擎启动并验证
- [x] Docker Demo 微服务启动（端口 9000，提供 `/health`、`/metrics`、`/error`）
- [x] Docker MySQL 启动并通过健康检查（端口 3307）
- [x] FreeAiOps 使用 WSL2 Ubuntu 启动，数据库迁移成功，`/health` 可访问
- [x] Agent 采集 Demo 微服务指标和 `runtime/demo_service.log`
- [x] Agent 使用 `.env` 配置调用 DeepSeek 兼容 LLM
- [x] 网页展示 Demo → Agent → FreeAiOps → LLM 的运行状态和分析结果

说明：FreeAiOps 源码保持不变；FreeAiOps 在 Windows 主机的 WSL2 地址上运行，Agent 通过动态 `FREEAIOPS_BASE_URL` 检查其健康状态。

运行验证（2026-08-31）：Docker Demo `/health`、`/metrics` 和 MySQL 健康检查通过；FreeAiOps WSL2 数据库迁移通过，`/health` 返回 `"ok..."`；Agent 读取 Demo 指标并以 `use_model=true` 调用 `deepseek-chat`，分析结果为 `abnormal`，FreeAiOps 状态为 `online`。

一键启动：运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_all.ps1`，脚本会检查 Docker、启动 Demo/MySQL、检查或启动 WSL2 FreeAiOps，并检查或启动 Agent API。


## 详细任务
T2：确认模型接口可用。

准备文件：
- `scripts/test_model_api.py`
- `.env.example`
- `docs/T2_MODEL_API.md`

完成标准：
1. API Key 只通过本机环境变量提供，不写入代码、报告或 Git。
2. 测试脚本收到 HTTP 200。
3. 返回体包含模型响应内容。
4. 记录模型名称和响应时间。
5. 未修改 FreeAiOps 源代码。

T3 当前进度：
- [x] 第一版指标与日志格式文档
- [x] 合法 JSON 示例
- [x] 输入格式校验程序
- [x] 校验程序自动化测试
- [x] 扩展到至少 20 个测试案例
- [x] 确定 Agent 标准输出格式

T1：下载并启动 FreeAiOps。
项目根目录是：
E:\December\Desktop\aiops-agent
要求：
1. 先阅读课程设计 PDF。
2. 阅读 PROJECT_SPEC.md、AGENTS.md 和 TASKS.md。
3. 将 FreeAiOps 下载到 framework/FreeAiOps。
4. 先检查 Go、Git 和 Docker 是否安装。
5. 不修改 FreeAiOps 源代码。
6. 不接入大模型。
7. 不执行删除文件、修改系统服务或自动修复命令。
8. 准备 MySQL 依赖。
9. 执行 Go 依赖安装。
10. 执行数据库迁移。
11. 启动 FreeAiOps。
12. 请求 http://localhost:8080/health 验证服务。

T8：实现 AIOps 分析 API 和结果存储。

目标：把当前“手动执行脚本并生成 JSON”的离线流程封装为可调用的本地服务。

计划内容：
- 新增项目自己的 Python API 服务，提供健康检查、提交观测数据、执行分析和读取结果接口。
- 复用现有 T3/T4/T5 逻辑，不重写已经通过测试的异常检测和根因分析代码。
- 将分析结果保存到本地 SQLite 或 JSON 历史记录，支持网页读取最新结果和历史记录。
- API Key 仍只从本机 `.env` 或环境变量读取，不返回给网页或写入结果。
- 保持 `auto_remediation_allowed: false`，不执行修复命令。

完成标准：
1. `POST /api/observations` 能接收符合 T3 格式的单条观测数据。
2. `POST /api/analyze` 能运行 T4 和 T5，并返回标准输出格式。
3. `GET /api/results` 能读取最近分析结果。
4. 有接口测试，覆盖正常、异常和非法输入。

T9：接入真实本机指标和日志采集。

目标：让项目除了 20 个离线案例外，也能采集当前电脑的真实运行数据。

计划内容：
- 使用轻量级 Python 采集器读取本机 CPU、内存、磁盘和系统负载等可获得指标。
- 读取一份明确指定的演示日志文件中的 WARN/ERROR 记录；不扫描或上传用户无关文件。
- 将采集结果转换为 T3 JSON 格式后交给 T8 API 分析。
- 第一版对暂时无法安全获取的指标使用 `null`，并明确标记为缺失，不伪造数据。

完成标准：
1. 可手动运行一次采集并获得带当前时间的 T3 观测数据。
2. 采集结果可成功送入 T8 API 并生成 T4/T5 结果。
3. 采集和转换逻辑有单元测试；正常案例与异常模拟案例均可验证。

当前实现：
- 已采集本机 CPU、内存和项目所在磁盘的真实百分比；Windows 不支持时系统负载为 `null`。
- 已接入固定路径 `runtime/local_events.log` 的 WARN/ERROR 日志读取；不会扫描任意用户文件。
- 已提供网页“采集本机数据”按钮、`GET /api/local-observation`、`POST /api/collect-now` 和独立采集命令。

T10：接入 FreeAiOps 状态与任务适配层。

目标：让已启动的 FreeAiOps 成为项目运行链路中的可见组件，而不只用于一次健康检查。

计划内容：
- 新增适配层，检测 FreeAiOps 的 `/health` 状态并记录可用性和检查时间。
- 仅使用 FreeAiOps 已确认存在且安全的公开接口；如没有可用的告警写入接口，则明确记录为“仅健康状态集成”，不伪造业务集成。
- 将 AIOps 分析结果关联到本项目的分析 ID，供网页显示 FreeAiOps 在线状态和关联信息。
- 不修改 `framework/FreeAiOps` 源码，不自动创建、删除或修改远程运维任务。

完成标准：
1. API 可返回 FreeAiOps 在线、离线或不可达状态。
2. FreeAiOps 不可用时，T4/T5 分析仍可安全完成，网页显示降级状态。
3. 有适配层测试，覆盖 HTTP 200、超时和异常响应。

当前实现：
- 已新增只读 `FreeAiOpsAdapter`，默认检查 `http://127.0.0.1:8080/health`，支持 `FREEAIOPS_BASE_URL` 覆盖。
- 已提供 `GET /api/freeaiops/status`，并在一键采集/分析响应中关联 FreeAiOps 状态。
- FreeAiOps 不可用时分析继续执行并返回 `offline` 降级状态；未调用任何业务写入或任务修改接口。

T10 实施方案与验收记录：
1. 适配层：封装只读 `GET /health`，统一输出 `online`（2xx）、`degraded`（服务可达但返回 4xx/5xx）或 `offline`（连接失败/超时），同时记录检查时间、HTTP 状态和耗时。
2. API 接入：在 `/api/freeaiops/status` 暴露独立状态，并在 `/api/analyze`、`/api/analyze-now`、`/api/collect-now` 中对同一次分析只检查一次并返回关联状态。
3. 结果关联：SQLite `analyses` 表增加可空 `freeaiops_json` 字段；已有数据库启动时自动补列，历史记录仍可读取，新分析可通过 `/api/results` 查询关联状态。
4. 安全边界：不修改 `framework/FreeAiOps`，不调用未知业务接口，不发送观测数据，不创建/删除/修改任务，不执行自动修复。
5. 测试：覆盖 HTTP 200、HTTP 503、网络异常，覆盖状态接口、分析响应和历史结果持久化；FreeAiOps 离线时 T4/T5 仍正常返回。

验收状态：已完成，自动化测试和真实本地 API 验证记录见 `CHANGELOG.md`。

T11：将网页升级为实时 AIOps 控制台。

目标：网页从读取静态 `eval/*.json` 升级为读取 T8 API 的最新分析数据。

计划内容：
- 已完成基础操作界面：网页可通过单次操作调用 T8 `/api/analyze-now`，隐藏 observation_id 和多步接口细节。
- 将网页数据源改为项目 API，显示最新采集时间、当前指标、异常状态、根因建议和 FreeAiOps 状态。
- 保留现有案例筛选和 20 个评估案例页面，作为离线评估证据。
- 提供“立即采集并分析”交互，只触发数据采集和分析，不触发自动修复。
- 显示 API 或 FreeAiOps 不可用时的明确错误提示和最近一次成功结果。

完成标准：
1. 网页能显示一次真实本机采集的分析结果。
2. 网页能显示 FreeAiOps 服务状态及最后检查时间。
3. 页面不显示 API Key，不提供危险操作按钮。
4. 前端逻辑通过语法检查，后端接口测试和原有 27 项测试继续通过。

T11 实施方案与验收记录：
1. 数据源：保留 `eval/*.json` 作为离线评估区域，同时将实时区域改为读取 `/api/results` 和 `/api/freeaiops/status`，不依赖浏览器直接读取本机文件。
2. 实时状态：新增本机 CPU、内存、磁盘、系统负载指标卡，展示最近采集时间、分析结论、FreeAiOps 状态及检查时间。
3. 操作闭环：页面打开后自动执行一次本机采集和分析，之后每 1 秒自动更新，且不依赖静态评估数据加载；同时保留手动观测分析与再次采集按钮，操作成功后自动刷新实时区域和历史记录，页面刷新后也能从 SQLite 恢复最近结果。高频模式可能快速增加 SQLite 记录。
4. 历史记录：新增最近分析列表，点击记录可查看完整指标、日志、根因和建议；API 历史结果携带原始观测，避免只显示分析摘要。
5. 降级提示：API 不可用或 FreeAiOps 离线时显示明确状态；FreeAiOps 离线不阻断本地 T4/T5 分析。
6. 安全与兼容：不展示 API Key，不增加修复按钮；API 同源部署优先，同时兼容 `http://127.0.0.1:5500` 调试页面。
7. 界面结构：将网页拆分为“实时监控、历史分析、测试案例、系统状态”四个可切换视图；实时监控突出当前状态，评估数据与运行数据分离。
8. 监控控制：实时监控提供自动检测开关、暂停/继续、1/5/30 秒频率选择和立即检测按钮；页面不可见时暂停轮询。
9. AI 助手：新增独立 AI 问答视图和 `POST /api/ai/ask`，问题由服务端读取 `.env` 模型配置并转发，可选择带入最近一次只读分析；不向浏览器返回 API Key，不执行修复命令。
10. AI 助手体验：回答按安全白名单渲染 Markdown；历史记录可滚动选择并作为上下文；提供常用问题示例、复制回答和清空对话。
11. 数据隔离修复：自动检测只更新实时监控与历史区域，不再写入手动分析结果区；手动分析结果仅由手动提交操作更新。
12. 记录名片：历史记录和测试案例支持悬停提示并点击打开详情名片，显示具体指标值、阈值、红绿状态条、日志数量和异常信号。
13. 随机异常案例：手动分析区的“填入异常示例”每次随机生成指标，随机选择 1-3 个指标超过阈值，保证提交后至少有一处异常。
14. 故障检测场景：新增 `POST /api/fault-detection`，接收 T3 指标/日志数据，自动运行 T4/T5 并输出结构化故障检测报告；网页手动检测入口直接调用该接口。
15. 故障检测入口：左侧导航新增“故障检测”，点击后直接定位到指标输入和报告区域，避免功能隐藏在实时监控页面下方。

验收结果：已完成。`node --check web/app.js` 通过；后端自动化测试 47 项全部通过；备用端口真实 HTTP 验证网页 `200`、API 健康 `ok`、历史结果包含观测和 FreeAiOps 状态。

T12：整理课程设计报告。

前置条件：T7 评估结果、T8-T11 的实现和验证记录已具备。

当前进度：已完成 IEEEtran/XeLaTeX 终稿 `report/AIOps课程设计报告终稿.pdf`、LaTeX 源文件 `report/AIOps课程设计报告.tex`、补充附录 `report/appendix_extra.tex` 和 Mermaid 源文件 `report/mermaid/*.mmd`。报告插入 assets 中的环境、服务、控制台和 AI 助手截图，包含故障检测与 Log+Metric 根因分析两个场景、引用文献、API/数据格式/测试结果、20 个案例逐案分析、50 项测试矩阵、安全威胁模型和复现步骤。XeLaTeX 两遍编译成功，PDF 共 30 页；已用 Poppler 抽查封面、正文、图片页和附录末页。

T13：录制演示视频。

前置条件：可展示离线 20 案例评估、一次真实采集分析、网页结果和 FreeAiOps 健康状态。
当前进度：已根据演示重点重写 `PRESENTATION_SCRIPT.md`，突出整体技术架构、创新点、个人设计和界面使用说明；具体录制仍待完成。

T14：检查并提交文件。

前置条件：代码、测试数据、报告和演示视频均已准备完成。

T12 验收记录（2026-09-01）：`python -m unittest discover -s tests -v` 共 50 项全部通过；`node --check web/app.js` 通过；`python src/validate_cases.py eval/cases.json --require-label` 通过；XeLaTeX 两遍退出码均为 0，PDF 页数为 30。报告中的评测数据更新为 T4 平均 0.004 ms、T5 平均 0.166 ms，未使用旧版 48 项测试数字。
## T8.1 FreeAiOps 事件链路增强（已完成）

- Agent 采集 Demo 微服务指标和日志后执行 T4 检测。
- 仅对异常观测创建 `aiops-event:<event_id>` 事件并写入 FreeAiOps。
- Agent 从 FreeAiOps 查询并取回事件，再将观测交给 T5/LLM。
- 分析结果保存事件状态，网页系统状态展示“已写入/已取回”。
- 使用 FreeAiOps 现有 `/api/v1/app` 接口，不修改 `framework/FreeAiOps` 源代码。

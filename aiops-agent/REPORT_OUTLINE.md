# 基于 Agent 的智能运维系统构建与研究

## 封面

- 题目：基于 Agent 的智能运维系统构建与研究
- 学院：计算机科学与技术学院、专业：数据科学与大数据技术、班级：大数据本科班、姓名：李盛鹏、学号：2351136、指导老师：叶晨、日期：2026.8.30
- 可在副标题中注明：FreeAiOps + Python Agent + Docker Demo 微服务

## 摘要与关键词

### 摘要建议内容

用 300～500 字说明：

1. 背景：微服务运行状态由多种指标和日志共同反映，人工排查效率有限。
2. 目标：构建一个能采集观测、检测异常、管理事件、分析根因并生成诊断建议的本地 AIOps Agent。
3. 方法：Docker 部署 Demo 微服务和 MySQL；Python/FastAPI 实现 Agent；使用可解释规则进行异常检测和根因分析；FreeAiOps 接收、持久化和查询异常事件；可选调用 OpenAI-compatible/DeepSeek 模型；网页统一展示。系统同时实现了指标异常检测报告和 Log+Metric 多维根因分析两个场景。
4. 结果：20 个离线案例全部判定正确，准确率 100%；异常检测平均耗时约 0.004 ms，规则根因分析平均耗时约 0.166 ms；自动化测试 50 项全部通过。
5. 边界：模型为可选增强，离线评估的 20 个案例使用 `rule-v1`；不执行自动修复或危险系统命令。

### 关键词

`AIOps`、`Agent`、`FreeAiOps`、`异常检测`、`根因分析`、`Docker`、`大语言模型`

## 第一章 项目背景与目标

### 1.1 研究背景

- 说明监控数据来源包含 Metrics 和 Logs，单一阈值或单条日志难以完整解释故障。
- 说明 Agent 的价值是把采集、检测、事件管理、分析和展示串成闭环。
- 结合课程题目要求，说明本项目面向教学实验和本地可复现实验环境。

### 1.2 项目目标

按“输入—处理—输出”列出目标：

- 接收符合约定格式的观测快照；
- 采集 CPU、内存、磁盘、负载以及 Demo 服务指标和日志；
- 输出 `normal/abnormal`、严重程度、置信度和证据；
- 给出根因候选、人工排查建议和安全状态；
- 将异常事件写入并从 FreeAiOps 取回；
- 由网页显示实时状态、历史记录、AI 问答和历史诊断书；
- 用至少 20 个案例评估准确率和响应时间。

### 1.3 已实现的两类应用场景

#### 场景一：故障检测

- 输入：一次包含 CPU、内存、磁盘、负载、请求、响应时间、错误率和数据库连接使用率等指标的观测数据，可附带日志；
- 处理：Agent 校验数据格式，使用阈值规则和 ERROR/WARN 日志证据判断是否异常；
- 输出：结构化故障检测报告，包含 `normal/abnormal`、严重程度、置信度、异常指标、日志证据、检测耗时和安全状态；
- 前端位置：实时监控页面和故障检测入口。

#### 场景二：根因分析

- 输入：故障检测结果以及同一时间窗口内的 Log 和 Metric 多维数据；
- 处理：Agent 关联指标异常与日志线索，生成根因候选；配置模型时，再将结构化上下文交给 LLM 生成自然语言诊断；
- 输出：可能原因、证据引用、按优先级排列的修复/排查建议，以及人工确认要求；
- 前端位置：AI 助手和历史诊断书。

这两个场景相互衔接但职责不同：故障检测回答“是否异常”，根因分析回答“为什么异常、应如何排查”。

### 1.4 范围与非目标

- 范围：本机或单机 Docker/WSL2 环境、一个 Demo 微服务、规则检测、可选 LLM 诊断、历史结果存储。
- 非目标：不搭建 Kubernetes 集群，不训练模型，不修改生产服务器，不执行删除、重启、改系统服务或自动修复命令。

**建议证据**：`PROJECT_SPEC.md`、课程设计 PDF 要求页截图。

## 第二章 需求分析与安全约束

### 2.1 功能需求

用表格描述输入、功能和输出，并明确两类核心场景：

| 场景/功能 | 输入 | 主要处理 | 输出 |
|---|---|---|---|
| 故障检测 | 指标快照，可附日志 | 阈值比较、日志证据提取、严重程度计算 | 故障检测报告 |
| 根因分析 | 检测证据、Log、Metric | 多维证据关联、规则推理、可选 LLM 解释 | 根因候选和修复建议 |
| 本机采集 | 主机资源、Demo `/metrics`、项目日志 | 安全采集和格式转换 | 标准观测快照 |
| 历史诊断书 | 用户选定的多条历史分析 | 时间窗口统计、异常比例和趋势汇总 | 诊断书 |
| AI 问答 | 问题和可选历史上下文 | 服务端调用模型 | 自然语言回答 |

### 2.2 非功能需求

- 可解释：异常输出必须包含指标阈值或日志证据；
- 可复现：Docker Compose、固定案例和脚本化命令；
- 可降级：FreeAiOps 或模型不可用时，本地异常检测和根因分析仍可完成；
- 安全：Key 只由后端读取，`auto_remediation_allowed` 固定为 `false`；
- 可测试：接口、采集、检测、分析和存储均有自动化测试。

### 2.3 安全与隐私边界

- `src/local_collector.py` 只读取项目 `runtime/local_events.log` 和 `runtime/demo_service.log` 中的 WARN/ERROR，不扫描用户其他文件；
- 浏览器不会接触 API Key；模型请求由 `src/model_client.py` 在服务端发起；
- 建议对象的 `requires_approval` 为 `true`，Agent 不直接执行建议；
- FreeAiOps 源码保持不变，仅调用已确认的健康和通用 app 接口。

**建议证据**：`AGENTS.md`、标准输出格式文档中的 safety 字段、网页安全状态截图。

## 第三章 技术选型与可行性

### 3.1 技术栈

| 层次 | 选择 | 作用 |
|---|---|---|
| 被运维对象 | Docker Demo 微服务 | 提供 `/health`、`/metrics`、`/error` 和演示日志 |
| Agent/API | Python、FastAPI、Uvicorn | 接收观测、编排分析和提供网页同源 API |
| 采集 | `psutil`、HTTP、固定日志文件 | 获取本机及 Demo 指标、日志 |
| 检测/分析 | `rule-v1` 规则检测与规则回退 | 可解释异常判断、根因候选和建议 |
| 事件框架 | FreeAiOps（WSL2） | 健康检查、事件接收、持久化和查询 |
| 数据库 | FreeAiOps 使用 MySQL；项目结果使用 SQLite | 隔离框架数据与 Agent 历史数据 |
| 模型 | OpenAI-compatible/DeepSeek，可选 | 将结构化上下文生成自然语言诊断 |
| 前端 | 原生 HTML/CSS/JavaScript | 实时监控、历史记录、AI 助手和诊断书 |

### 3.2 选型理由

- 选择 FreeAiOps：符合课程对开源 AIOps Agent 框架的要求，并提供事件接收、持久化和查询能力；当前环境不需要 Kubernetes，部署成本可控；
- 选择规则检测：阈值和日志证据可解释、输出稳定，适合先建立故障检测基线，再叠加模型增强；
- 选择 Python/FastAPI：便于组合采集、检测、分析模块，接口定义清晰，适合网页调用和自动化测试；
- 选择 SQLite：无需额外服务即可保存本项目分析历史，与 FreeAiOps 的 MySQL 数据隔离；
- 选择 Docker Compose：用声明式配置启动 Demo 和 MySQL，便于环境复现和演示；
- 选择 OpenAI-compatible 接口：不把 Agent 绑定到单一厂商，能够使用 DeepSeek 等兼容服务，也可以在后续替换为 Ollama 等本地模型。

**建议证据**：`DECISIONS.md`、`requirements.txt`、`docker-compose.yml`。

## 第四章 总体架构与数据流

### 4.1 逻辑架构图

报告中绘制以下组件图（可用 Mermaid 或 draw.io 重画）：

```text
Docker Demo 微服务 ──指标/日志──> Python Agent
                                  │
                                  ├─ 数据格式校验与标准化
                                  ├─ 规则异常检测
                                  │       └─ abnormal 才写入 FreeAiOps
                                  ├─ FreeAiOps / MySQL 事件管理
                                  │       └─ Agent 查询并取回事件
                                  ├─ 根因分析与建议
                                  ├─ 可选 LLM 诊断
                                  └─ FastAPI/SQLite/网页控制台
```

### 4.2 一次异常请求时序

说明一次采集的顺序：采集 → 数据格式校验 → 规则判定 → 异常事件发布 → FreeAiOps 查询/取回 → 根因分析/LLM → SQLite 保存 → 网页展示。补充同一异常指纹的 `deduplicated` 机制，说明每秒采集不会无限创建重复事件。

### 4.3 组件职责边界

务必写清：异常检测和根因分析的主逻辑在本项目 Python Agent 中；FreeAiOps 当前承担框架运行、事件接收/持久化/查询和健康状态，不声称它替代本项目的分析逻辑；LLM 只生成辅助诊断文本，不负责采集或执行修复。

**建议证据**：`ARCHITECTURE.md`、`src/api_server.py` 的 `_run_analysis_pipeline`、`src/freeaiops_adapter.py`。

## 第五章 环境搭建与部署

### 5.1 环境要求

- Windows 主机、Python 3.13、Git、Docker Desktop、WSL2 Ubuntu；
- Docker 端口：Demo `9000`，MySQL 主机映射 `3307`；
- FreeAiOps：WSL2 内 `8080`；Agent API：`8000`。

<span style="color:red">【待补充素材：Python、Git、Docker Desktop、WSL2 的版本信息和安装验证截图。】</span>

### 5.2 启动步骤

正文给出可复制命令：

```powershell
Set-Location 'E:\December\Desktop\aiops-agent'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_all.ps1
```

说明脚本依次检查 Docker、启动 Demo/MySQL、检查或启动 WSL2 FreeAiOps、检查或启动 Agent API。补充单独启动 API 的命令和访问地址 `http://127.0.0.1:8000/`。

<span style="color:red">【待补充素材：一键启动脚本的实际终端输出截图；如启动失败，保留错误信息和修复后的再次验证结果。】</span>

### 5.3 环境验证

展示以下验证结果：

```powershell
curl.exe -i http://127.0.0.1:9000/health
curl.exe http://127.0.0.1:9000/metrics
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/freeaiops/status
```

FreeAiOps `/health` 以实际运行结果为准（当前验证返回包含 `ok` 的响应）；不要把 Agent 的 `/api/health` 与 FreeAiOps 的 `/health` 混为同一个服务。

**建议证据**：`scripts/start_all.ps1`、`scripts/run_freeaiops_wsl.sh`、Docker/WSL2/终端截图、`CHANGELOG.md` 验证记录。

### 5.4 完整 AIOps 运行环境与关键配置

本节必须对应课程要求，说明 Python 运行环境、Docker 容器环境、被运维 Demo 微服务、MySQL、FreeAiOps 和 LLM 后端均已纳入同一条实验链路。

#### Python 与 Agent 配置

- 依赖来自 `requirements.txt`：FastAPI、Uvicorn、HTTPX 和 psutil；
- Agent 监听 `127.0.0.1:8000`，网页由同一进程的 `/web/` 路径提供；
- SQLite 历史库位于 `runtime/aiops.db`。

<span style="color:red">【待填写：Python 版本、虚拟环境名称、依赖安装命令和成功输出截图。】</span>

#### Docker Demo 与 MySQL 配置

- `docker-compose.yml` 定义 `demo-service` 和 `mysql` 两个服务；
- Demo 暴露 `9000`，提供 `/health`、`/metrics`、`/error`；
- MySQL 使用 8.4 镜像，主机端口映射为 `3307`，数据库名为 `freeaiops`；
- MySQL 数据通过 Docker volume 持久化，健康检查使用 `mysqladmin ping`。

<span style="color:red">【待填写：`docker compose ps`、Demo `/health`、Demo `/metrics`、MySQL healthy 状态截图。】</span>

#### FreeAiOps 与 WSL2 配置

- FreeAiOps 位于 `framework/FreeAiOps`，在 WSL2 Ubuntu 中运行；
- 服务端口为 `8080`，数据库连接到 Docker MySQL；
- Agent 通过 `FREEAIOPS_BASE_URL` 动态检查健康状态，并使用现有通用接口保存和查询兼容事件；
- FreeAiOps 源代码不做修改。

<span style="color:red">【待填写：WSL2 发行版、FreeAiOps 启动命令、数据库迁移输出、`/health` 返回和事件查询截图。】</span>

#### LLM 后端配置

- 模型配置写入项目 `.env` 或系统环境变量，后端通过 OpenAI-compatible 接口读取；
- 浏览器和报告只展示模型名称、调用状态和耗时，不展示 API Key；
- `use_model=true` 时才调用模型，失败时回退到规则分析。

<span style="color:red">【待填写：模型服务名称、接口基地址、模型名、一次成功调用的脱敏请求/响应和耗时截图；API Key 位置必须打码。】</span>

#### 组件验证汇总

建议制作一张汇总表，列出组件、端口、验证命令、预期结果和截图编号。

<span style="color:red">【待补充表格：请将上述各组件截图编号填入此处。】</span>

## 第六章 数据格式、采集与存储设计

### 6.1 观测数据输入格式

介绍 `schema_version`、`case_id`、`observed_at`、`service`、8 项指标、`logs` 和测试专用 `expected_label`。指出运行时输出不携带测试答案，避免标签泄露。

引用标准输出格式文档，放一份精简合法 JSON 示例，不必在正文放全部 20 个案例。

### 6.2 本机与 Demo 采集

- `psutil` 获取 CPU、内存、磁盘和可用时的 `load_1m`；
- `DEMO_SERVICE_BASE_URL` 配置存在时请求 Demo `/metrics`；
- 固定读取两个项目运行日志，只保留 WARN/ERROR；
- 无法获得的指标使用 `null` 并列入 `unavailable_metrics`，不伪造数值。

### 6.3 结果存储

说明 `runtime/aiops.db` 的 SQLite 表：`observations` 保存原始快照，`analyses` 保存标准分析、模型请求标记和 `freeaiops_json`；FreeAiOps 自己的数据由 MySQL 保存。解释两套数据库的隔离原因：框架运行数据和本项目实验历史属于不同所有者，避免改动框架源码或强耦合其表结构。

**建议证据**：`src/local_collector.py`、`src/result_store.py`、`eval/cases.json`、SQLite 查询结果截图。

## 第七章 Agent 核心实现

### 7.1 Agent 总体设计

从“采集层—判断层—分析层—服务层—展示层”解释 Agent：

- 采集层：读取主机资源、Demo 服务接口和指定日志；
- 判断层：根据指标阈值和日志级别判断是否异常，并形成可追溯证据；
- 分析层：结合多维证据生成根因候选和人工排查建议，必要时调用 LLM 生成自然语言诊断；
- 服务层：通过 FastAPI 暴露采集、故障检测、历史查询、诊断书和 AI 问答接口；
- 展示层：网页实时刷新状态，并支持历史记录、事件链路和诊断书查看。

应明确两个场景的调用关系：故障检测先输出“是否异常”的检测报告；只有在需要解释原因时，再把指标、日志和检测证据交给根因分析模块。

### 7.2 数据格式校验与标准输出

说明 `src/validate_cases.py` 检查字段、类型、范围、时间格式和案例 ID；标准输出固定包含 `result`、`evidence`、`root_causes`、`recommendations`、`safety`、`performance`。

### 7.3 规则异常检测与故障检测报告

说明阈值比较、ERROR/WARN 日志证据、严重程度和置信度计算，以及 `null` 指标的处理。给出一条异常指标证据和一条日志证据作为示例，并展示接口如何将这些内容组织成故障检测报告。强调该功能已实现“接收指标数据、自动判断异常、输出检测报告”。

### 7.4 Log + Metric 根因分析与修复建议

说明根因分析模块如何同时读取指标异常和日志线索，进行多维证据关联，生成根因候选、证据引用和 P1/P2/P3 修复/排查建议；模型不可用时使用规则回退；模型结果需经过 JSON 解析、字段校验和危险建议过滤。强调该功能已实现“结合 Log 和 Metric 分析故障原因并给出修复建议”。

### 7.5 FreeAiOps 适配与事件链路

描述 `FreeAiOpsAdapter`：健康状态分为 `online/degraded/offline`；异常观测通过现有 `/api/v1/app` 以 `aiops-event:<event_id>` 兼容信封保存；随后查询并取回同一事件，再交给根因分析模块或 LLM；同一异常指纹返回 `deduplicated`。明确没有修改 `framework/FreeAiOps` 源代码。

### 7.6 LLM 接入

说明 `.env`/环境变量只在后端读取，`use_model=true` 才请求模型；发送的是观测、异常检测证据和根因分析上下文；返回模型名、耗时和安全字段，不返回 Key。离线评测中的 `model_calls=0` 是因为评测采用规则基线，不代表在线模型接口不存在。

**建议证据**：`src/detect_anomalies.py`、`src/analyze_root_cause.py`、`src/model_client.py`、`src/freeaiops_adapter.py`、`src/api_server.py`。

## 第八章 API 与可视化控制台

### 8.1 API 设计

用表格列出主要接口：

| 接口 | 用途 |
|---|---|
| `GET /api/health` | Agent 健康检查 |
| `POST /api/analyze-now` | 提交并分析一条观测 |
| `POST /api/collect-now` | 采集本机/Demo 后分析 |
| `POST /api/fault-detection` | 返回结构化故障检测结果 |
| `GET /api/results`、`/latest` | 查询历史/最新分析 |
| `POST /api/diagnostic-report` | 汇总选定历史窗口 |
| `POST /api/ai/ask` | 带可选历史上下文的 AI 问答 |
| `GET /api/freeaiops/status`、`/events` | 查询框架状态和事件 |

### 8.2 页面功能

说明 `web/` 中的实时监控、历史分析、测试案例、系统状态和 AI 助手；实时区域支持 1/5/30 秒频率、暂停/继续、异常指标红绿条和记录详情；AI 助手支持 Markdown 白名单渲染、历史记录选择、常用问题、复制回答和历史诊断书。

### 8.3 降级与错误提示

说明 API 不可用、FreeAiOps 离线、模型未配置和历史 ID 不存在时的提示；前端不直接读取本机文件，统一通过 Agent API 获取数据。

**建议证据**：网页四个视图截图、浏览器网络请求截图（隐藏 Key）、`web/app.js`、`web/styles.css`。

## 第九章 测试设计与评估结果

### 9.1 测试方案

- 20 个案例覆盖正常、CPU/内存/磁盘/响应时间/错误率/数据库连接异常、ERROR 日志和多异常组合；
- 单元测试覆盖数据格式校验、异常检测、根因分析、采集、FreeAiOps 适配、SQLite 和 API；
- 前端执行 `node --check web/app.js`。

### 9.2 离线评估结果

以 `eval/metrics.json` 为准填写表格：

| 指标 | 当前结果 |
|---|---:|
| 案例总数 | 20 |
| 正确数 | 20 |
| 错误数 | 0 |
| 准确率 | 100% |
| 异常检测平均/中位/最大耗时 | 0.004 / 0.003 / 0.016 ms |
| 根因分析平均/中位/最大耗时 | 0.166 / 0.043 / 2.399 ms |
| 离线模型调用次数 | 0 |

注明：该准确率是第一版规则检测在固定案例上的结果，不等同于真实生产环境泛化准确率；根因分析耗时统计包含规则分析路径。

### 9.3 自动化测试结果

运行并记录：

```powershell
python -m unittest discover -s tests
node --check web/app.js
```

当前验证为 `Ran 50 tests ... OK`。报告中可附测试模块覆盖表和终端截图。

### 9.4 在线链路验证

单独记录一次真实演示：Demo 指标/日志 → Agent → FreeAiOps 事件 `published`/`retrieved` → 根因分析 → `use_model=true` 的 LLM 响应 → 网页结果。在线验证应记录时间、服务状态和响应耗时，但不能把一次演示当成统计意义上的准确率。

<span style="color:red">【待补充素材：一次完整在线链路的请求时间、FreeAiOps 状态、事件编号、模型名称、响应耗时和网页结果截图。】</span>

### 9.5 结果分析与讨论

- 故障检测场景：固定案例中的正常和异常标签均被正确识别，说明当前阈值规则和日志证据提取逻辑能够满足演示数据的判定需求；
- 根因分析场景：异常结果会保留指标值、阈值、日志消息和证据引用，规则分析可以在模型不可用时继续给出可解释建议；
- 性能方面：规则路径耗时很低，适合高频采集；LLM 调用耗时受网络和模型服务影响，应单独记录，不与离线规则耗时混合；
- 局限方面：案例数量和故障类型仍有限，100% 准确率只代表当前测试集，不能直接推断生产环境效果。

<span style="color:red">【待填写：根据你录制的真实运行结果补充在线模型耗时、异常持续时间和页面观察结论。】</span>

## 第十章 典型故障演示与运行结果

按视频顺序写成可复现实验：

1. 一键启动 Docker、MySQL、WSL2 FreeAiOps 和 Agent；
2. 访问 Demo `/health`、`/metrics`；
3. 调用 Demo `/error` 或等待异常日志；
4. 展示异常检测信号和指标红条；
5. 展示 FreeAiOps 事件已写入并取回；
6. 在 AI 助手选择历史记录并提问；
7. 生成自定义历史窗口的诊断书；
8. 展示“自动修复：禁止”。

每一步配一张截图或终端证据，并在图注写明时间、接口和预期结果。演示讲稿可直接参考 `PRESENTATION_SCRIPT.md`。

## 第十一章 问题、局限与改进方向

### 11.1 当前问题与解决记录

建议用“困难—原因—解决过程—验证结果”的表格描述，不要只罗列结论：

| 遇到的困难 | 原因分析 | 解决过程 | 验证结果 |
|---|---|---|---|
| Docker Desktop/WSL2 启动差异 | PowerShell 与 Bash 环境变量语法不同 | 使用 `scripts/run_freeaiops_wsl.sh`，在 Bash 内设置配置并切换 Go 模块目录 | FreeAiOps 可完成迁移并通过健康检查 |
| FreeAiOps 没有专用告警 API | 当前版本公开接口以通用 app 资源为主 | 使用 `aiops-event:<event_id>` 兼容事件信封，不修改框架源码 | 异常事件可写入、查询和取回 |
| 高频采集产生重复事件 | 每秒采集会重复提交同一异常 | 按异常指纹去重，并在页面显示 `deduplicated` | 持续异常不会无限创建事件 |
| Windows 部分指标不可用 | 操作系统不提供统一负载接口 | 使用 `null` 和 `unavailable_metrics` 明确表示缺失 | 分析流程仍能安全运行 |
| 模型返回格式不稳定 | LLM 可能返回非 JSON 或不完整字段 | 解析、字段校验、危险建议过滤，失败时规则回退 | 始终返回合法分析结构 |

<span style="color:red">【待补充素材：每个困难对应的原始报错截图、修复前后命令输出或 CHANGELOG 记录。】</span>

### 11.2 尚未解决或不应夸大的局限

- 20 个案例规模较小，案例分布和阈值仍由人工设计；
- 规则阈值不是动态基线，无法替代生产级时序异常检测；
- FreeAiOps 目前用于事件管理/查询，不包含本项目的异常检测和根因推理；
- LLM 响应受网络、配额和模型稳定性影响，需要人工审核；
- 当前禁止自动修复，未形成闭环执行器。

### 11.3 后续改进

- 增加更多服务和历史数据，按服务建立动态基线；
- 引入 Prometheus/OpenTelemetry 等标准采集；
- 增加事件生命周期、确认和人工反馈；
- 对模型输出做更严格的结构化校验和离线评测；
- 在隔离沙箱中设计需人工批准的安全处置流程。

### 11.4 困难解决过程总结

用一段 200～300 字总结排查方法：先通过健康检查和最小接口验证定位问题，再分别检查容器、WSL2、Agent API 和网页请求；对无法确认的框架能力不做假设，通过只读接口和测试确定边界；最后用自动化测试和真实 HTTP 请求复核修复结果。

<span style="color:red">【待填写：结合你的实际操作顺序，补充最有代表性的一个问题从发现到解决的全过程。】</span>

## 第十二章 总结

总结应回扣课程要求：项目已完成本地 Python、Docker、MySQL、FreeAiOps、LLM 兼容接口和网页控制台的组合；实现了 Metrics+Logs 故障检测、根因分析、建议输出、事件管理和诊断展示；20 个案例和 50 项自动化测试提供了可复核证据。最后再次说明系统定位是“可解释、可降级、禁止自动修复”的教学型 AIOps Agent。

## 参考文献

建议至少包括：

1. 课程设计 PDF《大数据与信息服务方向综合课程设计题目及要求》；
2. FreeAiOps 官方 GitHub 仓库和使用文档（写明访问日期）；
3. FastAPI、Uvicorn、psutil、Docker Compose、MySQL 官方文档；
4. 所使用 OpenAI-compatible/DeepSeek API 文档；
5. 与 AIOps、根因分析或日志异常检测相关的教材/论文。

## 附录

### 附录 A：目录与关键文件

列出 `src/`、`demo_service/`、`web/`、`eval/`、`tests/`、`scripts/`、`framework/FreeAiOps` 的作用，并附项目目录树。

### 附录 B：运行命令

收录一键启动、单独启动 API、运行数据校验/检测/分析/评估、运行测试和访问网页的命令。命令中的路径使用实际项目路径，API Key 用占位符。

### 附录 C：接口与输出样例

附 `POST /api/collect-now`、`POST /api/fault-detection`、`POST /api/diagnostic-report` 的脱敏请求/响应；响应只保留关键字段，完整 JSON 可作为电子附件。

### 附录 D：截图清单

- Python、Docker、Git、WSL2 检查；
- Docker Demo `/health`、`/metrics` 和 MySQL 健康状态；
- FreeAiOps `/health` 与事件查询；
- Agent API 文档和网页实时监控；
- 异常指标、日志证据、事件 `published/retrieved`；
- AI 助手回答和历史诊断书；
- 20 案例评估结果、`metrics.json` 和 50 项测试通过；
- 安全状态“自动修复：禁止”。

### 附录 E：交付前核对

- [ ] 报告中的端口、路径、测试数量和评测数字与最新运行结果一致；
- [ ] 所有截图已遮挡 API Key、个人路径中不必要的隐私信息；
- [ ] 报告、源码、测试数据和 MP4 视频均在提交目录；
- [ ] `TASKS.md` 中报告、演示视频和最终提交状态按实际完成情况更新；
- [ ] 未声称 FreeAiOps 执行了本项目的异常检测/根因分析，也未声称 Agent 已自动修复故障。

<span style="color:red">【阈值说明：当前版本将内存使用率异常阈值设为 95%，以适应本机长期约 90% 的正常运行状态；若实验环境变化，应重新运行评估并更新报告中的相关截图和结果。】</span>

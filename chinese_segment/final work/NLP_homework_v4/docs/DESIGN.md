# 文献综述 Agent —— 详细设计文档

> 中文信息处理课程大作业 · 项目总体设计 + 逐文件说明

本文档面向想看清"代码每一行都在做什么"的读者（包括课程评审、二次开发者、未来的你）。
快速使用请看 [`README.md`](../README.md)。

---

## 一、项目定位

### 1.1 一句话目标

输入一个研究主题（如「大语言模型 中文命名实体识别」），系统自动跑完
**检索 → 中文信息抽取 → 主题聚类 → 综述生成** 的完整流水线，并在网页上把结果可视化。

### 1.2 课程映射

| 课程要求 | 项目对应 |
|---------|---------|
| 中文分词与词典构建 | jieba 分词 + 三套自建术语词典（方法/数据集/指标） |
| 信息抽取 | 规则法和 LLM 法两路并存，字段完全对齐，可量化对比 |
| 命名实体识别 | 词典匹配 + 正则，识别技术名词、数据集、评测指标 |
| 关键词抽取 | jieba TF-IDF |
| 文本聚类 | TF-IDF + KMeans |
| 文本生成 | DeepSeek 综述生成，带可追溯引用号 |
| 评估方法 | P / R / F1，自建标注集 |

### 1.3 不做的事（避坑）

- **不爬中文文献库**（CNKI/万方等）—— 反爬合规风险高，一周做不完
- **不解析扫描版 PDF** —— 用摘要文本足够
- **不做引用关系图谱** —— 时间成本高，对核心模块加分有限
- **不做完整 agent 任务规划** —— 用固定流水线就够称为 "agent 雏形"，报告里讨论扩展即可

---

## 二、总体架构

### 2.1 数据流

```
┌──────────────┐
│  用户输入主题  │  "大语言模型 思维链推理"
└──────┬───────┘
       │
       ▼
┌────────────────────────────────┐
│  Step 1：查询翻译 (translator)  │  中文检测 → DeepSeek 翻译 → "large language model chain of thought"
└──────┬─────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────┐
│  Step 2：双源检索 (retrieval)                    │
│   ├─ arXiv API（用英文查询）                     │
│   └─ Semantic Scholar API（中英文各一次）        │
│   → 按标题归一化跨源去重                          │
│   → S2 结果按 influentialCitationCount 排序      │
└──────┬─────────────────────────────────────────┘
       │ List[Paper]
       ▼
┌────────────────────────────────────────────────┐
│  Step 3：中文信息抽取 (extraction)              │
│   ├─ 规则法：jieba + 自建词典 + 正则             │
│   └─ LLM 法：DeepSeek 结构化 JSON               │
│   两者输出完全相同的 StructuredRecord            │
└──────┬─────────────────────────────────────────┘
       │ List[StructuredRecord]
       ▼
┌────────────────────────────────────────────────┐
│  Step 4：主题聚类 (clustering)                  │
│   jieba 分词 → TF-IDF → KMeans → 自动选 k       │
│   每簇用高权重词 + 高频 methods 当主题标签        │
└──────┬─────────────────────────────────────────┘
       │ clusters / year_trend / keyword_cloud
       ▼
┌────────────────────────────────────────────────┐
│  Step 5：综述生成 (review)                       │
│   把结构化记录喂给 DeepSeek，强制只能引用给定编号  │
│   输出后正则扫描 [n]，超范围的标为幻觉             │
│   LLM 不可用时退到规则拼接版                      │
└──────┬─────────────────────────────────────────┘
       │ review.text + citations_used + hallucinated
       ▼
┌────────────────┐
│  Flask 返回 JSON │  前端用 Chart.js / wordcloud2.js / marked 渲染
└────────────────┘
```

### 2.2 "Agent 雏形" 在哪里

`src/pipeline.py` 的 `run_full_pipeline` 函数串起以上五步，每步打时间戳日志。
这条固定 pipeline 就是作业思路文档里说的「基于固定流程的 agent 雏形」。

写报告时可以这样讨论扩展：
- 让 LLM 决定是否扩大检索范围（当前固定 max_results）
- 让 LLM 决定是否走 LLM 抽取还是规则法（根据论文摘要语言）
- 让 LLM 在综述阶段反向请求补充检索（发现某类方法缺失时）

### 2.3 关键设计选择与理由

| 选择 | 理由 |
|------|------|
| 规则法 + LLM 法并存 | 课程评分核心是中文信息处理基本功，jieba 路径不能砍；LLM 路径用于对比拿加分 |
| 字段完全对齐 | 让 `eval/compare.py` 能直接做 P/R/F1 对比，否则写"对比实验"会很尴尬 |
| TF-IDF 而非 sentence-transformers | sentence-transformers 会拉 torch 2GB+，一周作业不值；TF-IDF 对短摘要够用 |
| Flask + 原生 JS 而非 Streamlit | 团队选定，留出后端可扩展空间，前端用 CDN 库压缩代码量 |
| 默认绕过本地代理 | 国内学术 API 公网可达；用户机器上常驻的 V2ray/Clash 反而拦截 arXiv |
| 中文主题自动翻译 | arXiv 99% 是英文论文，中文检索词命中率几乎 0；翻译后命中率提升一个数量级 |
| 引用号强制可追溯 | 综述幻觉是大模型的老问题，主动校验是评分加分点 |
| 并发数据抓取与防封 | 使用 `ThreadPoolExecutor` 爬取 Hugging Face 和 GitHub 仓库。触发 GitHub 限制时启动 HTML 网页正则表达式兜底，保证星标提取成功 |
| 按需局部精读 | 不默认请求全量全文字段（太慢且耗 token）。提供“✨精读分析”按钮，从 arXiv HTML 或 PDF 解析（利用 PyPDF2）截取前 4 万字符深度剖析 |
| LLM 不可用降级 | 让 demo 永远能跑，避免老师演示时 key 用完翻车 |

---

## 三、文件逐个走读

### 3.1 顶层文件

#### `app.py`（Flask 入口）

- `GET  /`：渲染前端首页
- `GET  /api/status`：返回 `{llm_available: bool}`，给前端判断要不要显示橙色提示
- `POST /api/pipeline`：**一键全流程**，最常用。body 接 `{topic, year_from, year_to, max_results, method}`
- `POST /api/retrieve` / `/api/extract` / `/api/cluster` / `/api/review`：分步骤接口，留给未来分步前端用

启用了 `flask-cors`，方便用 Postman 直连调试。

#### `config.py`（配置）

只做一件事：用 `python-dotenv` 加载 `.env`，导出常量。提供一个 `llm_available()` 函数让其他模块判断要不要走 LLM 路径。

#### `requirements.txt`

故意保持精简——不装 sentence-transformers / torch / pandas / openai SDK 等大依赖。

#### `.env.example`

环境变量模板。**用法是 `cp .env.example .env`，不要直接编辑 `.env.example`**，否则 `config.py` 找不到。

---

### 3.2 数据结构层：`src/models.py`

整个项目只有两个核心数据类：

```python
@dataclass
class Paper:
    """检索阶段拿到的原始论文。"""
    paper_id: str          # 形如 "arxiv:2401.01234" 或 "s2:abc123"
    title: str
    abstract: str
    authors: List[str]
    year: Optional[int]
    venue: str             # 期刊/会议名，S2 会带引用数后缀
    url: str               # 跳转链接
    source: str            # "arxiv" 或 "semantic_scholar"

@dataclass
class StructuredRecord:
    """信息抽取后的结构化记录。两种抽取方法都输出这个结构。"""
    paper_id: str
    title: str
    year: Optional[int]
    authors: List[str]
    keywords: List[str]
    methods: List[str]
    datasets: List[str]
    metrics: List[str]
    conclusion: str
    extracted_by: str      # "rule_based" 或 "llm_deepseek"
```

**为什么字段完全对齐**：对比实验的前提是输出可比。如果 LLM 多吐一个 `motivation` 字段，规则法没有，这两个就没法做集合 P/R/F1。

---

### 3.3 LLM 层：`src/llm/deepseek_client.py`

只包两个函数：

- `chat(messages, ...) -> str`：普通对话
- `chat_json(messages, ...) -> dict`：强制 JSON 输出

为什么不直接用 OpenAI SDK？DeepSeek 接口确实兼容 OpenAI 格式，但引 SDK 就要装 `openai` 包并担心版本兼容。一个 50 行的 `requests.post` 直接搞定，更轻。

错误处理：HTTP 非 200 抛 `DeepSeekError`；JSON 解析失败也抛同类异常。调用方决定怎么降级。

---

### 3.4 检索层：`src/retrieval/`

#### `arxiv_client.py`

调用 arXiv API（返回 Atom XML，用 `feedparser` 解析）。
关键细节：

- 默认绕过 HTTP_PROXY/HTTPS_PROXY 环境变量（设 `proxies={"http":"", "https":""}`）。原因见 README 常见问题。
- 客户端层不去重，去重在 pipeline 统一做。
- `year_from / year_to` 在客户端做过滤而非 API query string，因为 arXiv API 不支持年份过滤参数。

#### `semantic_scholar_client.py`

调用 S2 Graph API。增强点：

- 请求字段含 `citationCount` 和 `influentialCitationCount`，用于排序
- `limit` 取 `max_results * 4`（最多 100），多拿一些再按引用挑高质量
- 排序按 `influentialCitationCount` 降序，次序按 `citationCount`
- 支持 `min_citations` 参数过滤低质量
- `429`（限流）静默返回空列表，不让上游崩
- 同样默认绕过代理

#### `translator.py`

中文主题 → 英文检索词。流程：

1. 没中文字符 → 原样返回
2. 有中文 + LLM 可用 → DeepSeek 翻译，prompt 强制只输出 2-6 个小写英文词，无标点无解释
3. 有中文 + LLM 不可用 → 退回到 25 个常见 NLP 术语的内置映射表

**为什么不预先全部用映射表**：术语长尾太长，写不全；LLM 翻译能处理任意输入。映射表只做兜底。

#### `dedup.py`

按归一化标题去重：小写化 + 去掉所有非字母数字字符。简单粗暴，但对学术论文够用——同一篇论文在 arXiv 和 S2 的标题除了空格大小写基本一致。

#### `enricher.py` (超额拓展)

在 `run_full_pipeline` 中调用：
1. `fetch_code_url`: 并发请求 Hugging Face Papers API 与 PapersWithCode，截获 GitHub 仓库链接与 Stars 数量。如果触发 Github 403 限流，自动转用浏览器 UA 去直刮 Github 网页，用正则提取星星总数。
2. `fetch_image_url`: 抓取 arXiv HTML 页面中的核心插图用于海报生成。
3. `fetch_full_text`: 当请求精读时，抓取 arXiv HTML，去除所有干扰项 `<script> <style> <math>`。如果网页版不可用，退化到 `fetch_pdf_text` 下载原 PDF 用 `PyPDF2` 解析并拼成纯文本。

---

### 3.5 抽取层：`src/extraction/`

#### `base.py`

```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, paper: Paper) -> StructuredRecord: ...
    def extract_batch(self, papers) -> List[StructuredRecord]: ...
```

抽象接口让规则法和 LLM 法可以互换，pipeline 调用方不用关心实现。

#### `rule_based.py`（评分核心）

```
text = title + abstract
  ├─ methods   = 词典匹配（兼容中英文，大小写归一化）
  ├─ datasets  = 词典匹配
  ├─ metrics   = 词典匹配 + 正则 "数字%? + accuracy/F1/..." 补数值
  ├─ keywords  = jieba TF-IDF（中文）or 词频统计（英文）
  └─ conclusion = 切句后找触发词（中文"实验表明/我们提出"，英文"we propose/achieve"）
```

启动时把所有词典词汇 `jieba.add_word()` 进去，避免「自注意力」被切成「自/注意力」。

#### `llm_based.py`

DeepSeek 结构化抽取，prompt 详见源码。关键点：

- 强制 JSON 模式
- 即使输入是英文摘要，要求 `conclusion` 输出中文（便于评审阅读）
- 自动把提取的 methods/datasets/metrics 翻译对齐为统一规范的英文术语。
- 失败时返回**空字段但 paper_id 保留**的 StructuredRecord，不让 pipeline 崩
- 提供 `deep_read_paper` 增强接口，传入提取好的超长 Full Text，深度挖掘诸如“硬件环境、具体性能、模型结构和局限性”并渲染详评 markdown。

---

### 3.6 聚类层：`src/clustering/topic_cluster.py`

`cluster_papers(papers, records)`：

1. 文本预处理：每篇论文 `title + abstract` 经 jieba（中文）或空格切（英文）
2. TF-IDF 向量化（max_features=2000）
3. KMeans 聚类（k 按论文数自适应：<4 不聚，<8 聚 2，<15 聚 3，<30 聚 4，否则 5）
4. 每簇取**簇中心 top-6 特征词** + **records 里 methods/keywords 的高频词**作为主题标签
5. 输出 `{clusters: [...], assignments: {paper_id: idx}}`

`year_trend(papers)`：简单 Counter，按年份计数。

---

### 3.7 综述层：`src/review/generator.py`

`generate_review(records, clusters)` 关键逻辑：

```
1. 把每条 record 编号 [1] [2] ... 放进 prompt
2. system prompt 硬性要求：所有 [n] 必须取自给定编号，不得编造
3. 要求生成一段 `mermaid` 演进路线图，附带高度包容的正则提取器。
4. DeepSeek 输出后，正则 \[(\d+)\] 扫所有引用号
5. 超出 [1..N] 范围的标为 hallucinated_citations
6. 返回 {text, mermaid_code, citations_used, hallucinated_citations, fallback}
```

降级版（`_fallback_review`）：LLM 不可用时按规则拼一个五段式草稿，统计 methods 出现频次，把高频方法的引用按编号列出。不能算真综述，但保证前端永远有内容显示。

---

### 3.8 流水线编排：`src/pipeline.py`

三个核心函数：

- `retrieve(topic, ...)`：调用翻译 → arXiv + S2 → 去重
- `extract_all(papers, method)`：选规则法或 LLM 法，逐篇抽取
- `run_full_pipeline(topic, ...)`：完整五步，每步 stage 日志附带时间戳

`run_full_pipeline` 的返回结构正是前端要的所有数据：papers / records / clusters / year_trend / keyword_cloud / review / log。

---

### 3.9 前端：`templates/index.html` + `static/`

#### `index.html`

单页面，DOM 结构：

- 顶部：主题、年份、最多、抽取方法 4 个表单 + 「一键运行」按钮
- 流水线日志：黑底窗口，运行时实时滚动
- 结果区（默认隐藏，跑完显示）：
  - grid 左右：词云 canvas / 年份折线 canvas
  - 主题聚类：每簇一张小卡片
  - 文献列表：表格，带有 Github 链接和 ✨精读分析按钮
  - 综述草稿与海报按钮：marked.js 渲染 markdown，`[n]` 引用号高亮。生成学术海报可点击打印。
- 模态框 (Modal)：学术海报排版窗 (带 Mermaid 图表与首图) 与 论文详评深挖窗。

CDN 引入：`chart.js`、`wordcloud2.js`、`marked`、`mermaid`。无需 npm 构建。

#### `app.js`

事件流：

```
点击运行 → POST /api/pipeline → 拿到 JSON
       → renderPapers / renderClusters / renderWordcloud / renderYearChart / renderReview
```

幻觉引用渲染：把 `[99]` 这种超范围编号加 `class="warn"` 标红。

#### `style.css`

普通卡片+网格布局。蓝色主题，方法/数据集/指标用不同色 tag 区分。

---

### 3.10 评估：`eval/`

#### `labeled.json`

12 条人工标注样本，涵盖中英文混合的 NLP 论文（BERT、RAG、LoRA、CoT、中文 NER、对比学习、扩散模型、RLHF…）。每条结构：

```json
{
  "paper_id": "eval:1",
  "title": "...",
  "year": 2019,
  "abstract": "...",
  "gold": {
    "methods": [...],
    "datasets": [...],
    "metrics": [...],
    "conclusion_keywords": ["..."]
  }
}
```

#### `compare.py`

- 集合归一化（小写 + 去空格去连字符），然后算 set-level P/R/F1
- conclusion 走"关键词命中率"：gold 给 2-3 个关键词，看模型产出的 conclusion 是否包含
- 输出按字段分行打印，再打印 LLM 相对规则法的 ΔF1

---

### 3.11 词典：`data/dict/`

- `methods.txt`：约 80 条，涵盖经典方法（BERT/LSTM/CRF）、中文术语（自注意力/对比学习）、最新方法（RAG/LoRA/CoT）
- `datasets.txt`：约 55 条，国内外主流（GLUE/SQuAD/CLUE/MSRA NER/THUCNews）
- `metrics.txt`：约 35 条，覆盖分类 / 生成 / 检索 / 翻译指标

**扩展方法**：直接追加行即可，每行一个术语。规则法启动时会自动 `jieba.add_word()`。

---

### 3.12 调试脚本：`scripts/`

- `check_net.py`：诊断 arXiv / S2 网络可达性，打印代理设置
- `check_net2.py`：对比走代理 vs 直连的差异（写报告时可以截图佐证）
- `test_retrieval.py`：测翻译 + 检索全链路
- `show_pipeline.py`：把 `/api/pipeline` 的 JSON 响应美化打印

---

## 四、典型一次运行的耗时分布

以"大语言模型 思维链推理"主题、`max_results=10`、LLM 抽取为例：

| 阶段 | 时间 |
|------|------|
| 翻译 | 0.5–1.5 s（1 次 DeepSeek 调用） |
| arXiv 检索 | 2–4 s |
| S2 检索 | 1–3 s（或 0 ms 限流） |
| 去重 | <10 ms |
| LLM 抽取 | 10–20 s（10 篇，每篇 1–2 s） |
| 聚类 | <100 ms |
| 综述生成 | 8–15 s（1 次 DeepSeek 长输出） |
| **总计** | **20–40 s** |

规则法抽取替换 LLM 法可以省掉 10–20s，但牺牲细粒度。

---

## 五、可量化的评分点对照

| 评分点 | 对应实现 | 验证方式 |
|--------|---------|---------|
| 中文分词与词典 | `src/extraction/rule_based.py` + `data/dict/*.txt` | 跑 `eval/compare.py` 看规则法 F1 |
| 信息抽取对比 | 规则法 vs LLM 法字段对齐 | `eval/compare.py --llm` 出 ΔF1 表 |
| 命名实体识别 | 方法/数据集/指标三类实体抽取 | 同上 |
| 主题归纳 | TF-IDF + KMeans + 自动打标签 | 前端"主题聚类"卡片 |
| 综述生成 | DeepSeek + 引用校验 + 演进图提取 | 前端综述区右上角徽标"幻觉引用 N 个"，底部展示 Mermaid 流程图 |
| 可视化 | 词云 / 年份折线 / 聚类 / 综述 / 学术海报 | 前端页面 |
| Agent 编排 | `run_full_pipeline` 五步链 + 时间戳日志 | 前端"流水线日志"窗口 |
| (加分点) 全文提取 | `PyPDF2` + `re` 标签剔除 HTML 抓取 | 体验"✨精读分析"功能 |

---

## 六、扩展开发指南

### 加一个新数据源（如 PubMed）

1. 在 `src/retrieval/` 新建 `pubmed_client.py`，函数签名仿 `search_arxiv`
2. 返回 `List[Paper]`，注意 `paper_id` 用唯一前缀如 `pubmed:`
3. 在 `src/retrieval/__init__.py` 导出
4. 在 `src/pipeline.py.retrieve()` 加调用

### 加一个新抽取字段（如 "贡献点"）

1. `src/models.py` 的 `StructuredRecord` 加字段
2. `src/extraction/rule_based.py` 在 `extract()` 里加抽取逻辑
3. `src/extraction/llm_based.py` 在 prompt 里加字段说明
4. `eval/labeled.json` 给 gold 加该字段
5. `eval/compare.py` 加该字段的评估
6. 前端 `static/app.js` 的 `renderPapers` 表格加列

### 把 KMeans 换成语义嵌入

`pip install sentence-transformers`，改 `src/clustering/topic_cluster.py`：

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("shibing624/text2vec-base-chinese")
X = model.encode([f"{p.title} {p.abstract}" for p in papers])
```

KMeans 那段不动。

### 升级为真正的决策型 agent

把 `src/pipeline.py.run_full_pipeline` 改成一个循环：每步结束后让 LLM 看当前状态，决定下一步动作（继续抽取/扩大检索/直接生成综述）。这是开放性扩展，时间够的话可以做。

---

## 七、已知限制

1. **中文核心论文偏少**：arXiv 没多少中文论文，S2 中文内容覆盖也有限。想找中文综述类工作，建议指定具体子方向或加期刊关键词。
2. **S2 无 key 限流严重**：免费 key 申请审批快，建议申请后填到 `.env`。
3. **TF-IDF 聚类质量受语料影响**：论文数 <8 时聚类基本只剩一类，是预期行为。
4. **规则法依赖词典完备性**：领域偏移时（如非 NLP 主题）召回率会下降，扩展 `data/dict/*.txt` 即可。
5. **综述长度受 max_tokens 限制**：默认 2000 token，最长约 1200 字中文。需要更长可改 `src/review/generator.py`。

---

## 八、参考

- 原始设计：[`../作业思路.md`](../作业思路.md)
- 仓库导览（给 Claude Code 用）：[`../CLAUDE.md`](../CLAUDE.md)
- DeepSeek API 文档：https://api-docs.deepseek.com
- arXiv API 文档：https://info.arxiv.org/help/api/index.html
- Semantic Scholar API 文档：https://api.semanticscholar.org

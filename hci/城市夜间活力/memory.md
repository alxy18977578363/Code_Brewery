# 项目工作记录（2026-04-14）

## 项目主题
城市夜间活力与消费热度 —— 上海夜间消费数据探索性分析与可视化
课程：探索性数据分析与可视化技术（期末大作业，占总成绩 60%）

---

## 今日完成事项

### 1. 建立五个项目阶段 Skills
位于 `C:/Users/12900/.claude/commands/`，对应五个阶段：

| 命令 | 文件 | 用途 |
|------|------|------|
| `/crawl` | crawl.md | 数据爬取与合成数据验证 |
| `/preprocess` | preprocess.md | 清洗、缺失值/异常值处理、特征工程 |
| `/analyze` | analyze.md | EDA 描述性统计与深度分析 |
| `/dashboard` | dashboard.md | ECharts HTML 可视化大屏 |
| `/insight` | insight.md | 数据洞察与报告结论提炼 |

### 2. 上海夜间消费数据集
- 文件：`data/synthetic/shanghai_night_orders.csv`
- 规模：**129,560 条**订单，**340 个 POI**，**10 个区**，时间跨度 2026-04-01 至 2026-05-01（31天）
- 字段：order_id, poi_id, poi_name, category_lv1, category_lv2, city, district, lng, lat, order_time, order_amount, payment_type, rating
- 品类（category_lv1）：餐饮、娱乐、零售
- 区县：黄浦区、静安区、徐汇区、长宁区、普陀区、虹口区、杨浦区、闵行区、松江区、宝山区（共10个）
- 数值列含随机小数，非平整，具备真实感

### 3. 描述性统计分析脚本
- 文件：`scripts/eda_descriptive.py`
- 运行：`python scripts/eda_descriptive.py`
- 依赖：pandas, matplotlib, seaborn, scipy, tabulate

#### 关键统计数字
| 指标 | 数值 |
|------|------|
| 订单总量 | 129,560 条 |
| 订单金额均值 | 96.65 元 |
| 订单金额中位数 | 73.43 元 |
| 订单金额标准差 | 106.31 元 |
| 99% 分位 | 510.91 元 |
| 最大值 | 2441.54 元（极端值） |

### 4. 生成图表（共10张，300dpi，位于 `data/synthetic/figs/`）

| 编号 | 文件名 | 内容 |
|------|--------|------|
| 图1 | fig01_amount_distribution.png | 订单金额直方图+KDE+分品类箱线图 |
| 图2 | fig02_hourly_trend.png | 夜间时段订单量与客单价双轴折线 |
| 图3 | fig03_category_hourly.png | 分品类（餐饮/娱乐/零售）时段走势对比 |
| 图4 | fig04_district_revenue.png | 各区30日消费总额排名（横向条形） |
| 图5 | fig05_weekday_vs_weekend.png | 工作日 vs 周末各时段订单量对比 |
| 图6 | fig06_payment.png | 支付方式占比饼图+分品类支付偏好 |
| 图7 | fig07_rating_distribution.png | 评分频率直方图+分品类小提琴图 |
| 图8 | fig08_category2_rank.png | 各二级品类订单量排行（含客单价标注） |
| 图9 | fig09_daily_trend.png | 30天日订单量与消费额走势（标记周末） |
| 图10 | fig10_rating_vs_amount.png | 评分×金额散点图+分品类回归线 |

### 5. 附属数据文件
- `data/synthetic/eda_descriptive_report.md` — 统计摘要文字报告（含各区/品类统计表）
- `data/synthetic/district_hourly_revenue.csv` — 各区逐小时消费额时间序列（供大屏使用）
- `data/synthetic/poi_name_word_freq.csv` — POI名称词频统计

---

## 待完成事项

- [ ] `/dashboard`：基于上述10张图表 + district_hourly_revenue.csv 制作 ECharts HTML 大屏（`dashboard/index.html`）
- [ ] `/preprocess`：输出清洗后标准数据 `night_economy_clean.csv`，含 is_night/is_weekend 等派生字段
- [ ] `/analyze`：深度分析（相关性、空间热度、异常检测）
- [ ] `/insight`：提炼 3-5 条有数据支撑的结论，对应报告第4-5章

---

## 项目文件结构

```
c:/Users/12900/Desktop/code/
├── 作业要求.txt
├── night_economy_framework.md       # 数据框架设计
├── memory.md                        # 本文件
├── scraper/
│   ├── crawler.py                   # Playwright 爬虫
│   └── config.json
├── scripts/
│   ├── generate_synthetic_night_economy.py
│   └── eda_descriptive.py           # 描述性统计分析（今日完成）
├── data/
│   ├── raw/poi_raw.csv
│   └── synthetic/
│       ├── shanghai_night_orders.csv       # 主数据集（12.9万条）
│       ├── district_hourly_revenue.csv     # 各区逐小时消费
│       ├── poi_name_word_freq.csv          # POI词频
│       ├── eda_descriptive_report.md
│       └── figs/                           # 10张统计图表（300dpi）
└── dashboard/                       # 待建
```

---

## 颜色规范（后续大屏/图表复用）
- 餐饮：`#F4845F`（暖橙）
- 娱乐：`#7B68EE`（紫蓝）
- 零售：`#5BA4CF`（冷蓝）
- 大屏背景：`#0d1117`，主色：`#58a6ff`，辅色：`#f0883e`

---

## 近期补充工作记录

### 1. 资产与可视化资源
- 下载示例 JSON 资源并保存到 `data/asset/` 与 `data/assets/`，文件名：`data-1555851394070-aGGRVy22M.json`。
- 迭代完成流动可视化页面 `dashboard/flow.html`：数据源切换（远程 JSON -> 本地 JSON -> CSV -> 出租车轨迹 JSON）、启用 `roam` 与缩放、蓝色系 `visualMap`、增加轨迹抖动/克隆以提升密度。

### 2. 脚本与数据处理
- 新建 `scripts/normalize_grid_flow_datetime.py`：将 CSV 中 `datetime` 统一到同一天，保留时分秒。
- 新建 `scripts/generate_taxi_flow_json.py`：从 `data/Taxi_070220` 目录提取 20:00–02:00 轨迹并生成线数据 JSON。
- 已抽样检查 `data/synthetic/grid_flow.csv` 与 `data/Taxi_070220` 内样本文件格式。

### 3. 进度说明
- 尝试运行轨迹生成脚本但中途取消，`shanghai_taxi_flow_2000_0200.json` 输出未确认生成完成。
- 已提供并行/流向图的数据结构与聚合方式说明（用于后续图表扩展）。

### 4. 新增可视化页面
- `dashboard/solution.html`：夜间活力平行坐标图，新增“各属性特征 Top1”表格，`score` 列显示该街道的 `Y_night_vitality` 综合评分。

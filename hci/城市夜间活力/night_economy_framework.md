# 城市夜间活力与消费热度：项目框架

### 夜间消费热度（核心）
- 数据源：外卖/到店/本地生活公开数据集
- 主表字段（建议命名）
  - order_id：订单唯一编号。
  - poi_id：商家/门店（POI，Point of Interest）唯一编号。
  - poi_name：商家/门店名称。
  - category_lv1：一级品类（大类）。
  - category_lv2：二级品类（细分）。
  - city：所在城市。
  - district：所在区县。
  - lng：经度（地理坐标）。
  - lat：纬度（地理坐标）。
  - order_time：下单时间（时间戳或标准时间）。
  - order_amount：订单金额（单位通常为元）。
  - payment_type：支付方式（如线上/线下、具体渠道）。
  - rating：用户评分（如 1–5 星）。

### 夜间活力人流（辅助）
- 数据源：移动热力公开数据、夜间灯光数据（夜光遥感）、或出租车/网约车订单
- 主表字段
  - grid_id
  - city
  - district
  - lng
  - lat
  - datetime
  - flow_in
  - flow_out
  - stay_duration
  - heat_index

### 性（解释变量）
- 数据源：POI 点数据、地铁/公交站、道路路网密度
- 主表字段
  - poi_id
  - category_lv1
  - category_lv2
  - lng
  - lat
  - density_1km
  - transit_access
  - road_density

### 评论与情感（体验层）
- 数据源：点评类评论、社媒公开文本或公开评论数据集
- 主表字段
  - review_id
  - poi_id
  - poi_name
  - city
  - district
  - category_lv1
  - category_lv2
  - review_time
  - rating
  - review_text
  - like_count
  - user_level

## 2 数据预处理（清洗与特征工程）
- 字段规范化
  - order_time 统一为时间戳
  - 派生字段：hour, date, weekday, is_weekend, is_night（22:00–06:00）
- 缺失值处理
  - 关键列缺失（lng/lat, order_time）剔除
  - 数值列（order_amount, flow_in/out）分区中位数填补
- 异常值处理
  - order_amount 用分位数裁剪（1%–99%）
  - flow_in/out 用 IQR 或 Z-score 标记异常
- 文本与情感
  - review_text 去噪（表情、URL、无意义符号）
  - 情感打分产出 sentiment_score, sentiment_label
- 空间统一
  - 坐标统一为 WGS84
  - 以 500m 或 1km 网格聚合，生成 grid_id
- 输出与记录
  - 清洗前后统计表：缺失率、均值、中位数、标准差
  - 处理日志：缺失规则、异常阈值

## 3) EDA 分析（浅层 + 深度）

### 浅层分析（描述性）
- 夜间消费总体规模：订单量、消费额、客单价
- 夜间时段分布：按小时的订单曲线（22–06）
- 空间热度：区县/网格热度排行
- 类别结构：category_lv1 的夜间占比、夜间消费 TOP 类目
- 情感分布：正/中/负占比，夜间 vs 白天对比

### 深度关系挖掘
- 时间 × 空间耦合：网格在不同时段的热度变化（时空热力图）
- 人流与消费的关系：heat_index 与 order_amount 的相关性、滞后相关
- 城市功能结构解释：POI 密度、交通可达性与夜间消费强度的关系
- 夜间消费类型差异：不同类别的活跃窗口对比
- 异常日识别：节假日 vs 工作日的结构变化与异常热点
- 情感与消费强度：sentiment_score 与 order_amount 的关系
- 负面原因提取：夜间负面关键词共现（如排队、噪音、安全）

## 4) 可视化大屏设计（布局与图表）

### 布局建议（大屏）
- 左上：城市夜间热力地图（网格热度，可切换时段）
- 右上：夜间时序走势（小时曲线 + 工作日/周末对比）
- 中部：类别结构雷达或堆叠条形（夜间消费结构）
- 左下：人流 vs 消费关系散点（含回归线）
- 右下：异常日/事件标记（日历热度或异常列表）
- 备选：情感分布堆叠条形（夜间 vs 白天）或情感-时段热力图

### 可视化要求
- 地图必须有图例与强对比配色
- 每张图标注单位（元、人次、订单量）
- 不做纯装饰图，所有图有明确结论

## 5) 报告结构对齐课程要求
- 选题背景与意义：夜间经济的重要性 + 城市治理需求
- 相关方法：统计分析、时空分析、相关性/回归、异常检测
- 具体方法介绍：预处理细节 + 变量构造 + 统计指标
- 分析展示：图表 + 结论解读
- 总结：3–5 条结论 + 局限性（数据覆盖偏差、时间跨度不足）

## 附：示例数据表说明 — `shanghai_night_vitality_streets.csv`

描述：该 CSV 为街道/街区级别的合成夜间活力样本表（用于示例分析与可视化），每行表示一个街道的多维指标与预计算活力得分 `Y_night_vitality`。表中字段含义如下：

- `street`：街道名称（文本）。
- `district`：行政区（文本）。
- `footfall_density`：人流密度归一化得分（0–1，越大表示人流越密集）。
- `avg_dwell_minutes`：平均停留时长归一化得分
- `peak_signal`：客流峰值强度归一化得分
- `weekend_ratio`：周末占比（0–1，表示周末活动相对活跃度）。
- `night_transit_coverage`：夜间公共交通覆盖或可达性得分
- `taxi_availability`：出租车可用性/接驳便利性
- `walk_bike_access`：步行/骑行可达性得分
- `night_spend`：夜间人均消费或消费强度归一化得分
- `night_orders`：夜间订单量归一化得分
- `night_shop_density`：夜间营业商户密度得分
- `entertainment_ratio`：娱乐业态占比
- `night_events`：夜间活动/事件数量归一化得分
- `culture_events`：文化类活动密度得分
- `event_duration`：活动平均持续时长归一化得分
- `street_connectivity`：街道连通性（路网指标归一化，0–1）。
- `walkability`：步行友好度得分
- `public_space_area`：公共空间面积归一化得分
- `lighting_level`：夜间照明充足度得分
- `crime_rate`：犯罪率（原表为归一值或相对风险指标，越高表示风险越高）。
- `noise_complaints`：噪音投诉率或归一化值
- `sanitation_complaints`：卫生投诉率或归一化值
- `resident_density`：常住人口密度归一化得分
- `job_housing_mix`：居住-就业混合度（0–1，越高表示混合越均衡）。
- `night_pop_ratio`：夜间人口占比
- `rent_level`：租金水平归一化得分（0–1，作为经济承载力 proxy）。
- `consumption_threshold`：消费门槛/人群支付能力指标
- `competitor_density`：同类商户密度或竞争强度
- `Y_night_vitality`：合成的夜间活力得分，可作为直接用于可视化的排序字段。

使用建议与示例操作：

- 导入到 MySQL 的表结构建议（字段类型为 `VARCHAR` / `FLOAT` / `DOUBLE`）：

```sql
CREATE TABLE shanghai_night_vitality_streets (
  street VARCHAR(128),
  district VARCHAR(64),
  footfall_density DOUBLE,
  avg_dwell_minutes DOUBLE,
  -- ... 其余指标 ...
  competitor_density DOUBLE,
  Y_night_vitality DOUBLE,
  PRIMARY KEY (street)
);
```

- 使用 `pandas` 读取并进行简单归一化 / 缺失检查的示例（Python）：

```python
import pandas as pd
df = pd.read_csv('data/synthetic/shanghai_night_vitality_streets.csv')
# 简单检查
print(df.info())
print(df.describe())

# 若需要按列重新归一化（0-1）
cols = [c for c in df.columns if c not in ['street','district','Y_night_vitality']]
for c in cols:
    mn, mx = df[c].min(), df[c].max()
    if mx > mn:
        df[c + '_norm'] = (df[c] - mn) / (mx - mn)

# 将表写入 MySQL（需配置连接与库）
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://user:pwd@host:3306/dbname?charset=utf8mb4')
df.to_sql('shanghai_night_vitality_streets', engine, if_exists='replace', index=False)
```

- 计算或重现 `Y_night_vitality` 的示例公式（伪代码，权重可配置）：

```sql
-- 假设已存在归一化字段 prefixed with _norm
SELECT
  street,
  0.25 * footfall_density +
  0.20 * night_spend +
  0.15 * night_shop_density +
  0.10 * night_events +
  0.10 * walkability -
  0.10 * crime_rate AS computed_score
FROM shanghai_night_vitality_streets;
```

注意事项：
- 表中某些字段（如 `crime_rate`、`noise_complaints`）为“负向指标”，在合成活力得分时需进行反向处理或给予负权重。 
- `Y_night_vitality` 为示例合成分数，实战中建议保留原始指标并在分析层（analysis layer）动态计算可调权重版本，便于可解释性与灵活调参。
- 对于可视化，推荐直接使用 `Y_night_vitality` 做排序/热力渲染，同时在交互细节中允许展开查看构成项（分解得分）。

数据来源与合规：本表为合成增强样本，用于示例与算法验证；若替换为真实采集数据，应记录来源、采集时间与合规许可。

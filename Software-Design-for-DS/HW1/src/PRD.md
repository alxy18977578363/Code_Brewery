# 数据科学中的质量工程实践 PRD（产品需求文档）

## 一、项目背景
在数据驱动和模型驱动的软件开发中，数据质量直接影响模型效果和业务决策。大规模数据集常见缺陷包括缺失值、重复、分布偏差、类型不一致、泄露、文件损坏等。为此，需对 OK-VQA 数据集进行系统性质量验证。

## 二、目标与范围
- 对 OK-VQA 数据集进行结构化、存储、探索、分析与质量验证
- 产出数据集质量报告（≤5页，PDF）
- 形成可复用的自动化验证流程

## 三、功能需求
### Step 1：数据结构化与存储
- 下载 OK-VQA 数据集
- 将原始数据转换为 Parquet 格式，命名为 data_clean.parquet
- 建立至少一个结构化索引表（如主键索引）
- 编写 schema 说明文档，详细说明字段含义与类型

### Step 2：数据探索与统计分析
- 使用 DuckDB 对 Parquet 数据进行分析，包括：
  - 总行数统计
  - 缺失值统计
  - 数值字段范围
  - 类别字段分布
  - 唯一性检查
- 输出分析脚本和结果截图

### Step 3：设计数据质量规则
- 使用 Great Expectations 编写至少 5 条数据质量规则，包括但不限于：
  - 非空检查
  - 数值范围约束
  - 唯一性约束
  - 类别分布约束
  - 类型一致性检查
- 输出 expectation 配置文件截图


question_id： 非空检查，唯一性检查，类型检查(转为int查看是否合适)，唯一性（Unique），数值范围（要大于0）
image：非空检查，字节长度合理性检查，图像是图片类型检查（jpg/jpeg等等）
question：非空检查，正则表达式检查（是否以“？”结尾），文本长度检查（1~300）
answers: 非空检查，答案数量检查(一般在1~10之间)，每个词非空检查(单个答案不能是空的)
question_type：非空检查，类型检查（"Brands, Companies and Products",
			"Cooking and Food",
			"Geography, History, Language and Culture",
			"Objects, Material and Clothing",
			"Other",
			"People and Everyday life",
			"Plants and Animals",
			"Science and Technology",
			"Sports and Recreation",
			"Vehicles and Transportation",
			"Weather and Climate"）
answer_type： 非空检查，类别检查(只能是other)




### Step 4：自动化验证流程
- 构建一键运行的验证脚本，实现：
  - 自动加载数据
  - 执行质量规则
  - 生成质量报告（如 HTML）

## 四、非功能需求
- 代码结构清晰，易于复用
- 结果可视化，报告美观
- 支持数据规模扩展

## 五、交付物
- data_clean.parquet
- schema 说明文档（schema.md）
- DuckDB 分析脚本与结果截图
- Great Expectations 配置文件截图
- 自动化验证脚本与质量报告
- 质量报告 PDF（≤5页）

## 六、验收标准
- 数据成功转换为 Parquet 并有结构化索引
- 分析脚本可复现统计结果
- 至少 5 条质量规则生效
- 验证脚本可一键生成报告
- 报告内容完整，结论清晰

---
如需详细技术方案、代码实现或模板，请进一步说明。
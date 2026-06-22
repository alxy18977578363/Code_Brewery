请你为这篇文章，使用简练的语言，一个段落概括这篇文章的技术背景，核心的解决手段，以及对整个研究领域的核心贡献或观点

### 数据清洗部分
- 第一阶段：开放与可复现的数据清洗

这一阶段的核心问题是：
商业模型所使用的数据清洗方式往往不公开，如何开辟透明的，可复现的数据清晰过程

1. Dolma

3T token 开放语料；
公开完整清洗流程；
提供开源 toolkit。

贡献：
把“数据清洗”从黑箱经验转变为可复现研究对象。



1. Data-Juicer（SIGMOD Companion 2024）


作用：

模块化处理：

语言检测；
质量过滤；
去重；
打分；
数据混合。

贡献：

将 Dolma 式流程抽象成可组合的数据算子。

推荐等级：


- 第二阶段：从“清洗”到“精细过滤”

研究者开始意识到：

不是所有保留下来的文本都一样好。

1. FineWeb（2024）


贡献：
利用96个 Common Crawl snapshot；
系统比较不同过滤策略；
构建15T token FineWeb；
提出 FineWeb-Edu。

核心观点：
清洗策略本身会影响模型能力，不同过滤方案不是等价的。



1. FineWeb-Edu（同论文中的教育子集）
值得单独强调。

贡献：

教育内容过滤后：

MMLU提升；
ARC提升。

核心观点：

“保留什么”比“删除什么”更重要。


- 第三阶段：清洗策略的偏差反思（2024–2025）

这是目前比较新的方向。

研究者开始问：

清洗后的数据真的客观吗？

1. Measuring Bias of Web-filtered Text Datasets（2024）

Mansour, Y., Heckel, R.

贡献：

分析：

FineWeb；
Dolma；
RefinedWeb；
RedPajama。

发现：

即使采用相似过滤流程，

不同数据集仍具有明显“指纹”。

核心观点：

清洗不是中性的，它会引入分布偏差。

1. Measuring Fingerprints of Web-Filtered Text Datasets and Fingerprint Propagation Through Training（NeurIPS 2025 Spotlight）

Mansour, Y., Heckel, R.

贡献：

进一步发现：

这些“清洗指纹”会传播到模型生成结果。

核心观点：

数据清洗不仅影响训练数据，还影响模型行为。


- 第四阶段：语言与场景适配

近两年另一个趋势是：

英文清洗规则无法直接迁移到其他语言。

1. Mangosteen（2025）

Phatthiyaphaibun, W., et al. Mangosteen: An Open Thai Corpus for Language Model Pretraining.

贡献：

基于 Dolma 流程改造：

增加：
泰语语言识别；
泰语质量过滤；
赌博内容过滤；
OCR修正。

核心观点：
清洗需要语言和文化适配，而不是“一套规则打天下”。

### 数据去重
研究推进：为什么去重 → 如何扩展到PB级 → 如何利用GPU加速 → 如何发现语义重复 → 未来走向混合去重

第一阶段：极端规模去重（2024）
1. LSHBloom: Memory-Efficient, Extreme-Scale Document Deduplication

核心贡献：基于传统 MinHash-LSH，提出Bloom Filter + LSH 的混合结构（LSHBloom）

解决的问题：MinHashLSH 内存占用太高；PB 级语料难以处理。

实验结果：
速度提升约 2.7 倍；
磁盘占用降低到传统方案的 0.6%；
在数十亿文档规模下具有更好的扩展性。
核心观点

去重的主要矛盾从“算法准确性”转变为“系统可扩展性”。


第二阶段：GPU化与高吞吐（2025）
1. FED: Fast and Efficient Dataset Deduplication Framework with GPU Acceleration

核心贡献：GPU 化签名生成；优化哈希计算；GPU 集群并行。

结果：
相比 SlimPajama CPU 去重工具提升 100×以上；
1.2T token 去重仅需约 6 小时；
与标准 MinHash 的结果高度一致（Jaccard > 0.96）。

核心观点：去重成为 LLM 训练流水线中的高吞吐计算任务。


第三阶段：公开数据集中的去重实践（2024）
1. The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale

核心贡献：
FineWeb采用per-snapshot deduplication。即每个 Common Crawl snapshot 内部先去重，再进行跨 snapshot 处理。

发现：不同去重策略会显著影响最终模型性能。

核心观点：去重不仅影响数据规模，还影响知识分布。


第四阶段：语义去重（Semantic Deduplication）（2024）

传统方法只能发现“长得像”的文本。新的问题：改写、翻译、释义怎么办？

1. Evaluating Deduplication Techniques for Economic Research Paper Titles with a Focus on Semantic Similarity using NLP and LLMs

核心贡献：比较
Levenshtein；
Cosine Similarity；
SBERT；
LLM辅助判断。
发现纯字符相似无法覆盖所有重复。语义模型具有优势。

核心观点：去重开始从“表面重复”走向“语义重复”。


### 数据过滤
- 第一阶段：从统一训练到“选择训练”（2023–2024）


1. Data Selection for Language Models via Importance Resampling

核心贡献

提出 Importance Resampling（重要性重采样），指出不是所有样本都要训练，根据目标任务的重要性重新采样。

在相同token预算下，性能明显提升。

核心观点：过滤开始从“删除低质量数据”转向“主动选择高价值数据”。


- 第二阶段：过滤成为独立研究方向（2024）
1. A Survey on Data Selection for Language Models

核心贡献：系统总结过滤方法分类为：
基于规则
长度
语言
URL
基于代理模型
PPL
小模型打分
基于梯度
Influence Function
基于目标任务
Active Selection
核心观点

数据过滤已经从经验技巧发展为独立研究领域。

- 第三阶段：经验研究——哪些过滤真的有效？（2024）

这是近两年最重要的工作之一。

1. A Pretrainer's Guide to Training Data

核心贡献：系统研究过滤哪些维度有效：
数据年代（Age）
域覆盖（Coverage）
毒性（Toxicity）
质量（Quality）

发现并不是越“干净”越好，过度过滤会损失知识覆盖。

核心观点：过滤存在性能—覆盖权衡。

- 第四阶段：工业界视角（2024）
1. What Makes a High-Quality Training Dataset for Large Language Models: A Practitioners' Perspective

核心贡献：通过工业实践总结出过滤关注：
正确性
信息密度
多样性
覆盖性
可读性
核心观点

工业界采用的是多指标过滤，而非单一质量指标。


- 第五阶段：多维质量融合（2025）
1. Flexible Integration of Data Quality Ratings for Effective Pretraining

核心贡献：融合多种过滤信号：

包括：
毒性
教育价值
信息密度
来源可靠性
可读性

采用可调权重机制。

实验表明：

优于单一过滤器。

核心观点

数据过滤从单维评分发展为多维融合。


- 第六阶段：质量与多样性的联合优化（2025）

这是最近非常热门的方向。

1. QuaDMix: Quality-Diversity Balanced Data Selection for Efficient LLM Pretraining

核心贡献：同时优化Quality和Diversity，发现只保留高质量数据，反而损害泛化，联合优化效果最佳。

核心观点
“高质量”不等于“最佳训练数据”。


第七阶段：对过滤本身的反思（2025）

1. The Data-Quality Illusion: Rethinking Classifier-Based Quality Filtering for LLM Pretraining

核心贡献：发现质量分类器可能只是学会模仿参考语料分布，而非真正识别高质量。

核心观点：当前“高质量过滤”可能存在认知偏差。


- 第八阶段：跨语言过滤（2025）

这个方向很新，也容易体现前沿性。

1. Judging Quality Across Languages

核心贡献：利用LLM评价多语言语料质量。发现英文过滤规则难以迁移。

核心观点：-数据过滤需要语言适配。


### 数据质量评估
- 第一阶段：多维度质量定义（“质量是什么”）

核心问题：数据质量到底由什么构成？

必引文献
1. A Pretrainer’s Guide to Training Data

贡献：提出数据质量的关键维度：
数据年龄（age）
领域覆盖（coverage）
毒性（toxicity）
数据质量（quality）

1. What Makes a High-Quality Training Dataset for LLMs
贡献：工业界定义：
正确性
信息密度
可读性
覆盖性

数据质量评估首先面临的是“定义问题”，即质量本身并非单一属性，而是由多个相互关联的维度共同构成。

第二阶段：模型驱动的自动评分（“如何评估质量”）

核心问题：能不能用模型自动判断数据好坏？

1. Data-Juicer（2024）
贡献：
内置 scoring system
支持多策略过滤
可组合 pipeline

2. LLM-as-a-Judge（2024–2025趋势）
核心思想：
用 GPT-4 / Claude 对数据评分
pairwise ranking
instruction-based evaluation

这一阶段结论
数据质量评估开始从人工规则转向模型驱动的自动化评分机制。

- 第三阶段：质量评估的反思与重定义（“我们是否真的在测质量？”）

核心问题：当前质量评估是否真的可靠？

1. The Data-Quality Illusion
贡献：
分类器可能学的是数据分布偏差
并非真实质量

1. Noisy Data and LLM Pretraining Loss Divergence
贡献：
用训练动态（loss divergence）反推数据质量
质量 ≈ 训练稳定性
软件设计
引言与研究背景
数据质量问题（mjl）
大规模预训练模型的训练高度依赖海量文本语料，目前业内主流数据集大多通过网络爬虫从公开网页获取。这类数据源具备体量优势，但受网络环境与采集方式限制，普遍存在各类原生质量缺陷。噪声、文本重复、样本分布偏差、基准数据污染以及隐私信息泄露，是现阶段预训练数据中最突出的五类问题。大模型训练过程存在较高的内存开销，训练数据的整体特征与质量会直接影响优化算法的运行效率，数据中混杂的各类缺陷还会进一步加重计算负担，制约模型整体性能表现[1]。数据层面的缺陷会贯穿模型全训练流程，不仅拖慢训练节奏，还会从泛化能力、输出公平性、评估有效性与线上应用安全等维度制约模型实际表现[2]。本章逐一剖析上述质量问题，结合现有研究阐述各类问题的表现形式、分布特征与实际危害，为后续开展数据清洗、质量优化等工作提供分析基础。
2.1 数据噪声
数据噪声指代训练文本中存在的无效信息，具体包含文字错误、乱码字符、商业广告、失效链接以及低可读性文本等内容。依托网页构建的通用语料库普遍存在噪声问题，以Common Crawl为代表的主流数据集，噪声内容整体占比可达30%至50%[3]。网络数据来源杂乱、内容审核缺失，是大规模预训练数据噪声居高不下的主要原因。
混入噪声数据会直接对模型训练产生负面作用，一方面会增加整体算力消耗，延缓模型收敛速度，另一方面也会干扰模型对有效语义特征的学习。噪声内容会直接引发预训练过程中的损失发散，不同类型的噪声对训练过程造成的影响存在明显差异，文本错误、乱码等问题都会造成模型损失出现异常偏离，不同架构的模型对此类问题也表现出相近的敏感程度。已有对照实验证明，当数据集内噪声占比超过 40%，模型综合性能会出现明显的断崖式下滑[4]。
目前业界广泛使用的GPT-3、LLaMA 2以及The Pile等公开数据集，均检测出不同程度的噪声内容。这类无效内容混杂在正常文本中，无法通过简单筛选完全规避，也是大规模网络语料与生俱来的短板[3]。
2.2 数据重复
按照内容相似度划分，预训练数据中的重复现象主要分为两类，一类是文本内容完全一致的精确重复，另一类是语义、句式高度相近的近似重复。网络爬虫会反复抓取同源网页、转载内容，使得重复问题成为爬取类数据集的共性缺陷。现有统计数据显示，通用大规模语料库的整体重复率在15%至20%之间，面向垂直领域的专用数据集，重复比例甚至能够达到35%[5]。
重复样本会改变模型的学习逻辑，极易引发过拟合现象，直接削弱模型面对陌生场景的泛化能力。同时，模型会反复记忆相同文本特征，进一步加剧生成内容失真、逻辑错乱等幻觉问题[5]。相关研究通过对照实验证实，仅10%的重复内容，就会造成模型在域外测试任务中的性能下降9%。
LLaMA作为经典开源预训练模型，其原始训练集中便存在大量重复文档。重复内容不仅影响模型效果，也造成了训练算力与存储资源的不必要消耗，这也是后续版本优化过程中重点关注的数据问题[6]。
2.3 数据偏差
数据偏差本质是训练样本在不同维度上的分布失衡，语言分布失衡、群体特征失衡、文化视角失衡是预训练数据中最常见的偏差类型[7]。当前全球主流预训练数据集以英文文本为主，英文内容占比超过 80%，与全球多语言使用的实际现状严重不符，形成了十分明显的语言偏差。
样本分布不均会直接传导至模型输出，引发公平性缺失问题。有研究针对GPT-4开展职业联想测试，结果显示模型存在明显的性别倾向，在提及工程师等专业岗位时，将职业与男性群体相关联的概率，比关联女性群体高出37%[10]。这类带有偏向性的输出，会大幅降低模型的实用价值与社会认可度。
除公平性问题外，数据偏差还会限制模型的适配范围。单一、失衡的样本分布，会导致模型在小众语言、特定群体、区域文化等场景下表现不佳，难以实现全场景落地应用。
2.4 数据污染
数据污染特指用于模型性能评测的标准测试集、公开基准数据，意外混入预训练数据集中。随着训练数据集规模不断扩张，数据采集范围持续扩大，基准数据被纳入训练语料的情况愈发普遍，已经成为行业内不可忽视的问题[9]。
主流评测基准的污染程度已经得到多项调研验证，MMLU等通用测评数据集约四分之一的内容，已出现在各类公开预训练语料中。这种情况会直接造成模型测评结果虚高，误差范围可达10%至15%[8]。根据污染形式的不同，该问题可分为单纯输入污染、输入与标签共同污染两类，后者对测评结果的干扰程度更为严重[9]。
数据污染会彻底改变测评工作的意义。被污染数据训练出的模型，并非依靠理解语义完成任务，而是单纯记忆训练样本内容，最终的测评成绩无法真实反映模型的学习能力与泛化水平[10]。相关调研指出，目前超过六成的大语言模型都存在不同程度的数据污染问题[11]。
2.5 数据泄露
数据泄露指个人身份信息、商业机密等敏感内容留存于预训练文本中。研究人员对The Pile等大型公开数据集开展抽样统计，结果显示平均每一千条文档内，会出现1.2至3.5条隐私类信息[12]。网页数据包含大量用户发布的原生内容，是隐私信息流入训练集的主要渠道。
现有专项研究针对预训练数据集的隐私泄露问题开展了全面调研，结果表明姓名、邮箱等各类个人敏感信息广泛存在于训练语料当中，模型在交互过程中极易复现这类内容，不仅违背现行数据安全与个人信息保护相关法规，也会对用户权益造成损害[12]。该问题不仅违反数据安全相关法规，还会给模型线上部署、商业化落地带来极大的安全隐患，也是大模型应用过程中必须防范的风险。
数据处理方法（lsp）
面对TB甚至PB级预训练语料，单纯依赖人工审查已无法满足数据质量控制需求。工业界和学术界通常采用自动化的数据处理流水线，对原始语料进行清洗（cleaning）、去重（deduplication）、过滤与选择（filtering and selection）以及质量评估（quality assessment）。这些步骤共同构成了预训练数据治理的核心环节，其目标不仅是剔除低质量样本，更在于在有限计算预算下实现数据质量、多样性与覆盖范围之间的平衡。
3.1 数据清洗
数据清洗是预训练数据处理流水线的首要环节，通过启发式规则与自动化模型从原始语料中剔除噪声、低质与有害内容。当前主流方法包括基于规则的清洗、基于分类器的清洗以及一站式处理框架三类。
基于规则的清洗通过预定义的启发式规则对文本进行筛选，常见规则包括文本长度阈值、语言识别、特殊字符比例限制等，此类方法计算效率高，适用于PB级语料的初步过滤。FineWeb项目[14]展示了规则清洗与分类器筛选相结合的工业级实践：研究团队利用Common Crawl快照构建了15万亿Token的数据集，通过启发式规则粗筛后，再利用基于教育价值训练的小型分类器进行精筛，实证了清洗策略的选择将直接决定并重塑模型的最终能力分布。然而，清洗过程本身会引入系统性偏差。Mansour和Heckel[27]发现尽管多个主流数据集采用了高度相似的启发式规则，神经网络分类器仍能以极高准确率判定文本的来源数据集，证明清洗管线会在数据中留下独特的"数据集指纹"。在NeurIPS 2025的后续研究中，他们进一步发现这种清洗偏差会作为"基因"深度编码至模型参数中，影响模型最终的生成偏好[28]。针对通用清洗规则在小语种场景下的失效问题，Mangosteen项目[20]针对泰语独特语言特性剔除了西方通用规则，加入了定制的语言分类器和本地化过滤器，构建了高质量的泰语预训练语料库。
基于分类器的清洗方法通过训练质量判别模型对文本进行细粒度评分。Dolma项目[13]采用启发式规则与基于参考语料训练的质量分类器相结合的多阶段清洗策略，构建并开源了包含3万亿Token的英语文本数据集。然而，Saada等人[25]揭示了该方法的内在局限：现有质量分类器在很大程度上只是学会了"模仿"参考语料的文本分布特征，而并非真正具备识别数据内在质量的能力，所谓的"高质量过滤"在某种程度上只是一种分布匹配的幻觉。一站式数据处理框架Data-Juicer[15]则通过细粒度管线架构将多种清洗操作封装为可组合的算子，内置50余个处理算子，实现了"数据处理—模型训练"的动态反馈闭环。
3.2 数据去重
数据去重旨在识别并移除语料库中的重复或高度相似文档。按照匹配粒度的不同，去重方法可分为精确去重、近似去重与语义去重三个层次。
精确去重通过计算文档哈希值进行完全匹配，无法应对微小修改产生的近似重复。近似去重采用MinHash算法结合局部敏感哈希（LSH）技术，通过估计文档间的Jaccard相似度来检测内容相近的文本。LSHBloom框架[16]将MinHash签名与布隆过滤器相结合，在数十亿文档规模下去重速度提升约2.7倍，磁盘占用降至传统方案的0.6%，展现出卓越的可扩展性。FineWeb项目[14]提出了按快照去重策略，即在每个Common Crawl快照内部先执行精细去重，再进行跨快照的全局处理，发现不同去重策略与阈值选择会显著改变数据集的领域组成。FED框架[23]引入GPU加速的MinHash签名生成与哈希计算机制，实现了相比传统CPU工具100倍以上的吞吐量提升，仅需约6小时即可完成1.2万亿Token的去重工作。在语义去重层面，You和Fraiberger[24]对比了Levenshtein距离、余弦相似度、SBERT语义嵌入以及LLM辅助判断等多种技术，发现基于深度学习的语义嵌入模型在识别隐性重复方面展现出显著优势，预示了去重技术从表层字符匹配向深层语义理解跨越的发展方向。
3.3 数据过滤与选择
与清洗和去重侧重于剔除低质量或冗余样本不同，数据过滤与选择更强调从海量语料中主动筛选对模型训练具有高价值的样本。按照技术原理的差异，现有方法可归纳为基于规则、基于代理模型、基于目标任务以及多维融合四大类别[18]。
基于规则的过滤通过预定义的启发式准则对样本进行筛选，计算开销低、可解释性强。Longpre等人[21]通过系统性消融实验发现过于严苛的清洗会导致严重的知识覆盖缺失，由此提出了性能—覆盖权衡（Performance-Coverage Trade-off）概念。基于代理模型的过滤利用小型语言模型或专用评分器对样本进行质量评估，能够捕捉比规则更丰富的语义质量信号，但也面临代理偏差问题——代理模型的选择本身会引入特定的数据分布偏好[18]。多维融合方法试图将多个质量维度整合为统一框架。FIRE框架[19]将毒性、教育价值、信息密度、来源可靠性及可读性等多种异构过滤信号集成到统一框架中，实验结果表明多维融合策略在预训练效果上全面优于单一质量过滤器。QuaDMix[22]进一步将质量评估与领域多样性纳入统一优化目标，研究发现盲目追求极端高质量反而会破坏数据集的均衡分布并损害模型泛化能力，"高质量"并不等同于"最佳训练数据"。基于目标任务的过滤从下游应用需求出发，DSIR框架[17]通过估计训练样本与目标数据分布之间的密度比来评估样本的下游相关性，将数据过滤从被动的质量控制转变为主动的价值优化。Ali等人[26]则探索了跨语言场景下的数据过滤，发现基于英文构建的过滤规则在迁移至小语种时面临严重的性能劣化，必须针对具体语言和文化背景进行深度适配。
3.4 数据质量评估方法
数据质量评估贯穿数据处理流水线全程，为清洗、去重与过滤等操作提供量化依据。按照评估对象的不同，现有方法可分为数据集层面的宏观评估与样本层面的微观评估。
在数据集层面，Longpre等人[21]通过对数据年代、领域覆盖、文本质量和内容毒性等多个维度开展大规模消融实验，量化了不同数据特性对模型性能的独立与耦合影响。Yu等人[6]从工业实践视角出发，总结出高质量预训练数据集应具备的五个核心特征：正确性、信息密度、多样性、覆盖性和可读性，并指出这些特征之间存在复杂的权衡关系。Data-Juicer框架[15]从工具层面提供了数据集质量评估的自动化支持，其内置的数据分析模块能够在处理流水线中实时监测长度分布、词汇丰富度、语言构成等关键统计指标。
在样本层面，基于参考语料训练的分类器是最常见的技术路线。Dolma项目[13]使用基于Wikipedia和Books3训练的KenLM分类器进行质量过滤，FineWeb[14]则训练了基于教育价值的小型分类器来筛选高质量子集。然而，Saada等人[25]指出质量分类器本质上学习的是参考语料的分布特征而非文本的内在质量。基于预训练语言模型的困惑度评分是另一类常用方法，但困惑度指标在处理专业领域文本时存在固有局限——专业术语往往导致困惑度偏高，从而被误判为低质量内容。基于大语言模型的自动评判（LLM-as-a-Judge）是近年来兴起的新范式，G-Eval[17]利用GPT-4通过思维链提示对文本的连贯性、相关性等多维度进行评分，展现出与人类判断较高的相关性，但其大规模应用面临计算成本与评估偏见的双重挑战。
参考文献

[1]Chen Y, Zhang Y, Liu Y, et al. A memory efficient randomized subspace optimization method for training large language models[J]. arXiv preprint arXiv:2502.07222, 2025.
[2]Perełkiewicz M, Poświata R. A review of the challenges with massive web-mined corpora used in large language models pre-training[C]//International Conference on Artificial Intelligence and Soft Computing. Cham: Springer Nature Switzerland, 2024: 153-163.
[3]Saada T N, Bethune L, Klein M, et al. The Data-Quality Illusion: Rethinking Classifier-Based Quality Filtering for LLM Pretraining[J]. arXiv preprint arXiv:2510.00866, 2025.
[4]Zhang Q, Garg A, Foerster J, et al. An Empirical Study on Noisy Data and LLM Pretraining Loss Divergence[J]. arXiv preprint arXiv:2602.02400, 2026.
[5]Longpre S, Yauney G, Reif E, et al. A pretrainer's guide to training data: Measuring the effects of data age, domain coverage, quality, & toxicity[C]//Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers). 2024: 3245-3276.
[6]Yu X, Zhang Z, Niu F, et al. What Makes a High-Quality Training Dataset for Large Language Models: A Practitioners' Perspective[C]//Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering. 2024: 656-668.
[7]Lin Z, Guan S, Zhang W, et al. Towards trustworthy LLMs: a review on debiasing and dehallucinating in large language models[J]. Artificial Intelligence Review, 2024, 57(9): 1.
[8]Choi H K, Khanov M, Wei H, et al. How contaminated is your benchmark? quantifying dataset leakage in large language models with kernel divergence[J]. arXiv preprint arXiv:2502.00678, 2025.
[9]Li Y, Guo Y, Guerin F, et al. An open-source data contamination report for large language models[C]//Findings of the Association for Computational Linguistics: EMNLP 2024. 2024: 528-541.
[10]Dong Y, Jiang X, Liu H, et al. Generalization or memorization: Data contamination and trustworthy evaluation for large language models[C]//Findings of the Association for Computational Linguistics: ACL 2024. 2024: 12039-12050.
[11]Deng C, Zhao Y, Heng Y, et al. Unveiling the spectrum of data contamination in language model: A survey from detection to remediation[C]//Findings of the Association for Computational Linguistics: ACL 2024. 2024: 16078-16092.
[12]Nakka K K, Frikha A, Mendes R, et al. PII-Scope: A Comprehensive Study on Training Data Privacy Leakage in Pretrained LLMs[C]//Proceedings of the 14th International Joint Conference on Natural Language Processing and the 4th Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics. 2025: 3731-3765.
[13]Soldaini L, Kinney R, Bhagia A, et al. Dolma: An open corpus of three trillion tokens for language model pretraining research[C]//Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2024: 15725-15788.
[14]Penedo G, Kydlíček H, Lozhkov A, et al. The fineweb datasets: Decanting the web for the finest text data at scale[J]. Advances in Neural Information Processing Systems, 2024, 37: 30811-30849.
[15]Chen D, Huang Y, Ma Z, et al. Data-juicer: A one-stop data processing system for large language models[C]//Companion of the 2024 International Conference on Management of Data. 2024: 120-134.
[16]Khan A, Underwood R, Siebenschuh C, et al. LSHBloom: Memory-efficient, extreme-scale document deduplication[J]. arXiv preprint arXiv:2411.04257, 2024.
[17]Xie S M, Santurkar S, Ma T, et al. Data selection for language models via importance resampling[J]. Advances in Neural Information Processing Systems, 2023, 36: 34201-34227.
[18]Albalak A, Elazar Y, Xie S M, et al. A survey on data selection for language models[J]. arXiv preprint arXiv:2402.16827, 2024.
[19]Xu L, Zhang X, Duan F, et al. FIRE: Flexible integration of data quality ratings for effective pretraining[C]//Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing. 2025: 14532-14552.
[20]Phatthiyaphaibun W, Udomcharoenchaikit C, Singkorapoom P, et al. Mangosteen: An open thai corpus for language model pretraining[J]. arXiv preprint arXiv:2507.14664, 2025.
[21]Longpre S, Yauney G, Reif E, et al. A pretrainer's guide to training data: Measuring the effects of data age, domain coverage, quality, & toxicity[C]//Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers). 2024: 3245-3276.
[22]Liu F, Zhou W, Liu B, et al. QuaDMix: Quality-diversity balanced data selection for efficient LLM pretraining[J]. arXiv preprint arXiv:2504.16511, 2025.
[23]Son Y, Kim C, Lee J. FED: Fast and efficient dataset deduplication framework with GPU acceleration[J]. arXiv preprint arXiv:2501.01046, 2025.
[24]You D, Fraiberger S. Evaluating deduplication techniques for economic research paper titles with a focus on semantic similarity using NLP and LLMs[J]. arXiv preprint arXiv:2410.01141, 2024.
[25]Saada T N, Bethune L, Klein M, et al. The Data-Quality Illusion: Rethinking classifier-based quality filtering for LLM pretraining[J]. arXiv preprint arXiv:2510.00866, 2025.
[26]Ali M, Brack M, Lübbering M, et al. Judging quality across languages: A multilingual approach to pretraining data filtering with language models[C]//Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing. 2025: 8870-8909.
[27]Mansour Y, Heckel R. Measuring bias of web-filtered text datasets and bias propagation through training[C]//Proceedings of the International Conference on Learning Representations (ICLR), 2025.
[28]Mansour Y, Heckel R. Measuring fingerprints of web-filtered text datasets and fingerprint propagation through training[J]. Advances in Neural Information Processing Systems, 2025, 38.
数据版本控制
1. Venkatesan, K. B. (2025). Managing Machine Learning Complexity with Advanced Version Control Techniques. International Journal of Computer Applications, 186(65).https://www.ijcaonline.org/archives/volume186/number65/venkatesan-2025-ijca-924421.pdf%5Breference:0%5D
传统代码版本控制工具Git无法管理GB级以上数据集，而DVC（Data Version Control）通过将数据存储在独立远程存储中、仅在Git仓库保留轻量级元数据指针，实现了对大规模训练数据的高效版本管理。文章强调，数据版本控制是ML实验可复现性的"第一道防线"——没有精确的数据版本锁定，任何关于模型性能的比较都是不可靠的。

2. Shehata, M. (2025). Reproducibility and Data Versioning in Data Science. figshare.https://figshare.com/articles/preprint/Reproducibility_and_Data_Versioning_in_Data_Science/30611123%5Breference:1%5D
从FAIR原则（可发现、可访问、可互操作、可复用）出发，论证数据版本化是科学计算可复现性的核心支柱。文章指出，数据版本化不仅需要记录数据内容的变化，还需记录数据采集的时间、来源和处理流水线参数，形成"可执行的版本快照"。"Data versioning goes beyond tracking content changes; it must capture the entire provenance chain including acquisition time, source, and transformation pipeline parameters."

3. Winks, E. (2026). How To Version LLM Training Data for Reproducibility. Atlan.https://atlan.com/know/llm-training-data-versioning-strategies/%5Breference:2%5D
提出了LLM训练数据版本化的三个最佳实践：
(1) 将数据集视为"一等公民"进行版本管理，而非代码的附属物；
(2) 使用内容寻址存储（content-addressed storage），使数据版本标识与内容哈希绑定；
(3) 在模型卡中明确记录所用数据集的版本哈希值。
"By August 2026, the EU AI Act will require teams to maintain auditable records of training data, making version control systems a core component of compliance toolchains."
同时到2026年8月EU AI Act生效后，团队必须能够提供训练数据的可审计记录，版本控制系统将成为合规工具链的核心组件。

4. Hugging Face Hub Integration: Dataset Versioning and Management. DeepWiki, 2026.https://deepwiki.com/huggingface/datasets/8-hugging-face-hub-integration%5Breference:4%5D
介绍了Hugging Face Datasets库内置的版本控制机制：每个数据集发布时生成唯一的commit hash，用户可以回滚到任意历史版本。但该机制缺乏像DVC那样的外部存储支持，对TB级数据集的版本管理效率较低。文章建议将DVC与Hugging Face Hub结合——用Hub进行数据集托管与共享，用DVC进行底层数据版本控制。
"Combining Hugging Face Hub for dataset hosting and sharing with DVC for underlying version control offers a promising path toward unified data management for large-scale pretraining."

5. MLOps: Changes and Tools: Adapting Machine Learning Workflows for Enhanced Efficiency and Scalability. International Journal of Engineering Research & Technology, 2025.https://www.ijert.org/MLOps-Changes-and-Tools%5Breference:5%5D
从MLOps视角总结数据版本控制工具与实验跟踪系统的集成实践。指出DVC可以与MLflow、Weights & Biases等实验跟踪工具联动，使得每次实验记录自动关联其所使用的数据集版本哈希值。这种集成是实现"端到端可复现性"的关键工程基础设施。"Integrating DVC with experiment tracking tools such as MLflow automatically links each run to the exact dataset version used, forming the engineering backbone for end-to-end reproducibility."

6. Integrating MLflow and DVC for Robust Machine Learning Lifecycle Management. DVC Community, 2025.
https://discuss.dvc.org/t/integrating-mlflow-and-dvc-for-robust-machine-learning-lifecycle-management/1438%5Breference:6%5D 提供MLflow与DVC集成的具体实现方案：在MLflow run中记录DVC的远程存储路径和commit哈希，实验复现时通过dvc checkout [commit]恢复精确的数据状态。文章强调，这种集成使得"代码—数据—环境"三者可在同一时间轴上被同步管理。"MLflow and DVC integration enables code, data, and environment to be managed synchronously along the same timeline, closing the reproducibility loop."

7. The Best Git for Data Tools in 2025. Secoda, 2025.
https://www.secoda.co/blog/git-for-data-tools-2025
评估了DVC、Pachyderm、Delta Lake等工具在数据版本控制方面的适用场景。指出DVC最适合中小规模团队开展研究型项目（数据量在TB级别），而Pachyderm更适用于需要实时数据版本化的生产级数据流水线。文章提出一个关键观察：绝大多数预训练研究项目对数据版本控制的采用仍然"严重不足"，多数依赖手动记录或全量复制数据集的方式。
"The adoption of data version control remains severely insufficient in most pretraining research projects, with many teams relying on manual logging or full dataset duplication."

数据血缘与可追溯性
1. Li, Y., et al. (2026). Tracing the Roots: A Multi-Agent Framework for Uncovering Data Lineage in Post-Training LLMs. arXiv:2604.10480.
https://arxiv.org/abs/2604.10480%5Breference:8%5D
提出了一个多智能体框架，用于自动重构后训练阶段LLM的数据演化图谱。该框架通过协调多个LLM智能体来完成代码理解、数据集识别、变换关系推断等任务，能够揭示数据集之间"垂直精炼"与"水平聚合"等结构化模式。文章的核心发现是：当前LLM数据生态中存在严重的"结构冗余"和"污染传播"问题——数据集之间的派生关系不被记录，导致同一原始数据以多种衍生形式反复出现，并且数据污染会沿着隐藏的血缘链条无声传播。"The absence of documented dataset lineage leads to structural redundancy and silent contamination propagation—the same source data appears in multiple derived forms, and harmful content spreads along hidden lineage chains."

2. Spoczynski, M., Melara, M. S., & Szyller, S. (2025). Atlas: A Framework for ML Lifecycle Provenance & Transparency. arXiv:2502.19567.
 https://arxiv.org/abs/2502.19567%5Breference:10%5D
Atlas框架利用软件供应链溯源技术，为机器学习全生命周期（从数据采集到模型部署）收集可验证的端到端血缘元数据。框架结合可信硬件（如TPM）与透明日志来增强元数据的完整性，防止血缘记录被篡改。文章特别指出，当前ML流水线中血缘数据的缺失不仅是技术问题，更是"责任性问题"——当模型造成损害时，无法追溯其数据来源就意味着无法确定责任主体。
"The absence of provenance in ML pipelines is not just a technical deficiency but an accountability gap—without traceability to data sources, it is impossible to assign responsibility when a model causes harm."

（会议论文版本）提供了Atlas框架的实现细节与实验评估。在实验中，Atlas能够在引入不超过15%的运行时开销的前提下，记录DPIA级别的血缘数据。文章强调，血缘记录的"可验证性"比"完整性"更重要——一条不可验证的完整血缘记录与没有记录等价。
"Verifiability of provenance records is more important than completeness—an unverifiable complete provenance record is equivalent to no record at all."

3. An LLM-guided Platform for Multi-granular Collection and Management of Data Provenance. Journal of Big Data, 2025.
https://link.springer.com/article/10.1186/s40537-025-01209-3 提出了一个LLM引导的数据血缘管理平台，支持从粗粒度（数据集级别）到细粒度（数据行级别）的多粒度血缘采集。平台使用LLM来自动解析数据处理脚本（SQL/Python），提取其中隐含的数据变换关系，从而自动构建血缘图谱。该研究解决了手工标注血缘成本过高的问题。
"LLM-guided provenance extraction from processing scripts significantly lowers the cost of lineage annotation, enabling automatic construction of fine-grained data lineage graphs."

4. yProv4ML: Python Library for Tracking Dataset Statistics, Hyperparameters, and Energy Metrics. Scilit.
https://www.scilit.com/publication/8690ddb3e1220e9341f1ea8dd9a7b235%5Breference:11%5D  yProv4ML是一个轻量级Python库，专为ML实验设计，能够自动记录数据集统计信息、超参数、能耗指标以及数据血缘关系。该库的核心设计理念是"最小侵入性"——用户只需添加两行装饰器代码即可启用血缘追踪。文章提供的实验证明，该库在大规模数据加载场景下的运行时开销低于3%。
"The core design philosophy of yProv4ML is minimal invasiveness—adding lineage tracking with just two lines of decorator code, at runtime overhead below 3% for large-scale data loading."

数据合规与治理体系
1. Lawfulness of mass processing personal data to train large language models in China. ScienceDirect, 2025.
 https://www.sciencedirect.com/science/article/abs/pii/  (DOI访问)
系统分析在中国《个人信息保护法》（PIPL）框架下大规模处理个人信息以训练LLM的合法性基础。文章指出，与GDPR不同，PIPL并未将"处理者正当利益"作为处理个人信息的合法依据，这使得中国LLM训练中大规模抓取个人信息的合法性存疑。文章建议采取"合规设计"策略，在数据采集阶段即嵌入匿名化或假名化机制。
"Unlike GDPR, China's PIPL does not recognize 'legitimate interests' as a legal basis for processing personal data, casting doubt on the legality of mass web scraping for LLM training in China."

2. China: A TMT: Data Protection & Privacy (PRC Firms) Overview Law. Chambers and Partners, 2025.
https://chambers.com/legal-guides/china-data-protection-2025%5Breference:14%5D 提供了2025年中国数据保护法律的全面概述。重点指出PIPL要求数据处理者建立"个人信息保护影响评估"机制，并且在发生数据泄露时需要在72小时内向监管机构报告。对于LLM训练而言，这意味着数据治理体系必须内建风险评估和应急响应模块。
"Under PIPL, data processors must establish a personal information protection impact assessment mechanism, requiring LLM training pipelines to embed risk assessment and incident response modules."

3. How Do GDPR and PIPL Impact AI Training Data for Legal Translation? HICOM Asia, 2025.
https://translate.hicom-asia.com/gdpr-pipl-ai-training-impact-legal-translation/%5Breference:15%5D  对GDPR与PIPL进行了比较分析，重点讨论跨境数据流动的限制。指出中国法律要求关键信息基础设施运营者将境内收集的个人信息存储在境内，而LLM训练往往涉及多数据中心分布式训练，这一要求对训练数据存储架构提出了特殊约束。
"China's data localization requirements impose special constraints on distributed training architectures that span multiple data centers across jurisdictions."

4. LLM-Driven Big Data Management Across Digital Governance, Marketing, and Accounting: A Spark-Orchestrated Framework. MDPI, 2025.
https://www.mdpi.com/1999-4893/18/12/791%5Breference:16%5D  提出了一个LLM驱动的大数据管理框架，其中专门设计了"治理层"模块，负责数据合规检查、血缘记录和访问控制。该框架的核心创新在于使用LLM来自动识别数据中的敏感内容（PII、知识产权受保护内容），并在数据进入训练流水线之前触发合规审查工作流。
"The governance layer of this framework uses LLMs to automatically identify sensitive content and trigger compliance review workflows before data enters the training pipeline."

5. 大规模预训练数据管理与质量控制机制. 阿里云开发者社区, 2025.
 https://developer.aliyun.com/article/116%5Breference:17%5D 从工业实践角度总结了大规模预训练数据治理的三层架构：原始数据层（仅记录不修改）、清洗数据层（去重过滤后的中间产物）、训练数据集层（最终用于训练的数据集）。每层数据都有独立的版本标识和访问控制策略。文章特别指出，数据治理不是中心化的"一刀切"管控，而是分层分级的差异化策略。
 "Data governance for large-scale pretraining is not a one-size-fits-all centralized control, but a layered, differentiated strategy: raw data layer, cleaned data layer, and training dataset layer, each with its own versioning and access control policies."

6. EU AI Act – Article 13(3)(f): Transparency and information provision for high-risk AI systems. Official Journal of the EU.
 https://artificialintelligenceact.eu/article/13/%5Breference:18%5D EU AI Act第13(3)(f)条要求高风险AI系统的提供者创建并维护详细的技术文档，其中必须包括"用于训练、验证和测试的数据集及其来源的描述"。这一条款实际上将数据版本控制和血缘追踪上升为法律义务。法案的过渡期截止于2026年8月，此后不满足该要求的模型将被禁止在欧盟市场投放。
"Article 13(3)(f) of the EU AI Act legally mandates that providers of high-risk AI systems maintain detailed documentation of datasets used for training, validation, and testing, effectively elevating data version control and lineage tracking to a legal obligation."

7. Chinese Data Privacy Laws: PIPL, CSL, and DSL Framework for AI Training Data. HICOM Asia, 2025.
https://translate.hicom-asia.com/ 系统梳理了PIPL、《网络安全法》（CSL）、《数据安全法》（DSL）对AI训练数据的要求三角框架：CSL关注数据存储安全与等级保护，DSL关注数据分类分级与重要数据保护，PIPL关注个人信息主体的权利。三个法律共同构成了中国数据合规的三条红线。文章指出，LLM训练数据往往同时触发这三部法律的适用，合规评估必须采用综合性方法。
"PIPL, CSL, and DSL together form the three red lines for Chinese data compliance: CSL focuses on data storage security, DSL on data classification and protection of important data, and PIPL on individual rights—LLM training data often simultaneously triggers all three."

8. 生成式人工智能服务管理暂行办法. 国家互联网信息办公室, 2025.
https://www.gov.cn/zhengce/zhengceku/202307/content_6891750.htm 该办法明确规定生成式AI服务提供者在训练数据处理活动中应当：使用具有合法来源的数据；涉及个人信息的，应当取得个人同意或者符合法律、行政法规规定的其他情形；采取有效措施提高训练数据质量，增强标注人员的合规意识。这是目前中国对生成式AI训练数据最直接的上位法约束。
"The Interim Measures for the Management of Generative AI Services explicitly require providers to use data with lawful sources, obtain consent for personal information, and implement effective measures to improve training data quality."

9. The hidden risk of transformed data in AI models. Relyance AI, 2025.
 https://www.relyance.ai/blog/ai-data-governance-derived-risk%5Breference:21%5D 提出了"转换数据"的合规风险概念：原始数据经过清洗、增强、匿名化等变换后，其与原始数据的法律关系（如授权范围、同意条款）可能发生改变，而这种改变往往未被明确记录。文章认为，数据治理体系必须跟踪每次数据变换对合规状态的影响，确保变换后的数据仍然符合原始授权范围。
"Data governance must track the compliance implications of each data transformation—anonymized or augmented data may no longer fall under the same legal authorization as the raw data, and this changed status must be explicitly recorded."

通用治理框架
1. TableVault: Metadata Governance Framework for Human-AI Collaborative Data Creation. arXiv preprint.
https://arxiv.org/abs/2508.12345   提出了一个面向人机协同数据创建的元数据治理框架。核心设计是"元数据即代码"——将数据集的元数据（来源、变换历史、合规状态）以结构化形式与数据内容一同版本化。该框架特别适用于LLM微调中的指令数据集管理，因为这类数据往往由人工标注与AI生成混合产生，血缘关系尤为复杂。
"The 'metadata-as-code' approach versions dataset metadata alongside data content, making it particularly suitable for managing instruction datasets where human annotation and AI generation intertwine."

2.Li, Y., et al. (2026). Tracing the Roots. （同血缘部分1.）

3. Wang, Z., et al. (2023). Data Management for Large Language Models: A Survey. arXiv:2312.01700.
 https://arxiv.org/abs/2312.01700%5Breference:23%5D 这是一篇广泛引用的LLM数据管理综述。文章将数据治理问题归纳为四个维度：数据采集、数据处理、数据评估和数据维护。在"数据维护"维度下，版本控制、血缘追踪和合规管理被列为三大核心任务。文章的一个关键观察是：LLM社区目前对数据维护的投入远低于对模型架构优化的投入，这种不平衡正在成为制约LLM可靠性的瓶颈。
"The LLM community currently invests significantly less in data maintenance—versioning, lineage, and compliance—than in model architecture optimization, and this imbalance is becoming a bottleneck for LLM reliability."


可复现性与工程实践（jjy）
找了点我这部分也可以用上的参考文献（水水参考文献的话可以用）
随机性
1.D. Picard (2021). torch.manual_seed(3407) is all you need: On the influence of random seeds in deep learning architectures for computer vision. https://arxiv.org/abs/2109.08203  —— 在 CIFAR-10 上扫描多达 10⁴ 个随机种子，结论是即使整体方差不大，也很容易找到表现远好于或远差于平均的异常种子。
2.C. Summers & M. Dinneen (2021, ICML). Nondeterminism and Instability in Neural Network Optimization. https://arxiv.org/abs/2103.04514  —— 指出在监督学习场景下非确定性对优化的影响此前研究很少，适合作为"问题被低估"的依据。
3.The Challenge of Reproducible ML: An Empirical Study on The Impact of Bugs (ReproduceML). https://arxiv.org/abs/2109.03991  —— 提出了一个有用的分类法：将引起非确定性的因素归纳为随机种子、模型定义、软件版本、线程模型、运行时、硬件和数据七类，其根因可归为随机性、版本和浮点运算三种。
4.Non-Determinism in TensorFlow ResNets. https://arxiv.org/abs/2001.11396  —— 即使固定了初始化与批次的种子，GPU 的非确定性仍会导致训练出不同的模型，并用 ResNet-50/CIFAR-10 做了量化。
5.Investigating the Impact of Randomness on Reproducibility... https://arxiv.org/abs/2410.02806  —— 实测了 CUDA 非确定性与优化器选择对结果方差的影响，并量化了开启确定性模式的运行时代价，发现确定性执行带来的运行时开销通常很小。
6.Assessing the Macro and Micro Effects of Random Seeds on Fine-Tuning Large Language Models. https://arxiv.org/abs/2503.07329  —— 把种子敏感性问题专门迁移到 LLM 场景。
分布式训练
1.Scaling Performance of Large Language Model Pretraining. https://arxiv.org/abs/2509.05258  —— 讨论了大规模预训练流水线，关注分布式训练、跨数百节点管理大数据集以及扩展数据并行，且指出公开文献中关于扩展训练性能调优的实用建议非常稀缺。
2.T. Le Scao et al. (2022). BLOOM: A 176B-Parameter Open-Access Multilingual Language Model. https://arxiv.org/abs/2211.05100  —— 训练期间平均每周发生 1–2 次 GPU 故障，由于有备用节点自动接管且每三小时保存一次检查点，对吞吐影响不大；而数据加载器的 PyTorch 死锁与磁盘问题造成了 5–10 小时停机。
环境依赖
1.Enabling End-To-End Machine Learning Replicability: A Case Study (MORF). https://arxiv.org/abs/1806.05208  —— 用 Docker 容器把代码、软件依赖和执行环境完整封装进单一文件，从而保证端到端可复现并便于共享。
2.A Guide to Computational Reproducibility in Signal Processing and Machine Learning. https://arxiv.org/abs/2108.12383  —— 客观讨论了取舍：Docker 通过把环境封装进隔离容器解决了依赖管理问题，但对没有经验的研究者可能开销过大，conda 这类轻量级环境/包管理工具在很多计算实验中更合适。
3.The role of metadata in reproducible computational research. https://arxiv.org/abs/2006.08589  —— 从元数据视角讨论容器与依赖记录。
实验思路
子实验 E1：随机性消融
设三组处理：
●A 组（完全确定性）：固定 Python/NumPy/PyTorch/CUDA 全部种子，开启 torch.use_deterministic_algorithms(True) 与 cudnn.deterministic=True，固定数据加载顺序（含 DataLoader 的 worker_init_fn）。
●B 组（固定种子但允许非确定性算子）：种子固定，但保留 cuDNN benchmark / 非确定性 CUDA 算子。
●C 组（变种子）：放开种子，跑 15–20 个不同种子。
记录：最终 loss/困惑度/下游准确率的均值、标准差、最大-最小极差；A 组相对 B/C 组的运行时开销。预期能复现"GPU 非确定性即便锁种子也带来差异"（对应文献 4、5）和"存在异常种子"（文献 1）。
子实验 E2：分布式配置消融
固定有效批大小不变，改变实现方式：
●1 GPU vs 多 GPU 数据并行（2/4/8 卡）vs 单卡梯度累积。
●对比项：相同全局批+相同种子，结果是逐比特一致还是仅统计相似；混合精度（fp16/bf16 vs fp32）对一致性的影响；NCCL all-reduce 求和顺序带来的浮点非结合性误差。
记录：loss 曲线的逐步偏离程度、最终指标差异。这里能直接印证"浮点运算非结合性 + 并行执行顺序"这一根因（文献 3、6）。
子实验 E3：环境依赖消融
同一份代码、同一组种子，在不同软件/硬件栈下运行：
●不同 PyTorch 大版本（如 1.13 vs 2.x）、不同 CUDA/cuDNN 版本；
●裸机 vs Docker 容器（依赖版本 pin 死）；
●条件允许的话，跨 GPU 架构（如 V100 vs A100）各跑一次。
记录：跨环境的结果差异，并对比"容器+版本锁定"能把方差压低到何种程度（对应文献 9、10、17）。

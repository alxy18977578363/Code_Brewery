1.Soldaini, L., Kinney, R., Bhagia, A., Schwenk, D., Atkinson, D., Authur, R., ... & Lo, K. (2024, August). Dolma: An open corpus of three trillion tokens for language model pretraining research. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) (pp. 15725-15788).
https://arxiv.org/abs/2402.00159 
鉴于当前商业大模型和部分开源模型对其预训练数据配方与清洗细节讳莫如深，严重阻碍了关于训练数据如何影响模型能力和局限性的学术研究，艾伦人工智能研究所等机构推出了开源预训练语料库 Dolma 。研究团队通过融合网页、论文、代码和图书等多源数据，构建并清洗出包含3万亿Token的英语文本数据集，并同步开源了高性能、可扩展的清洗工具包（Dolma Toolkit）。该项目通过完全的透明与开放，不仅实现了大模型实验的可复现性，更为AI学术界探究模型偏见、记忆效应及优化大规模数据管理奠定了“科学基石”。

2.Chen, D., Huang, Y., Ma, Z., Chen, H., Pan, X., Ge, C., ... & Zhou, J. (2024, June). Data-juicer: A one-stop data processing system for large language models. In Companion of the 2024 International Conference on Management of Data (pp. 120-134).
https://arxiv.org/abs/2309.02033 
针对大语言模型数据处理中缺乏抽象、管线复杂且反馈昂贵等挑战，Data-Juicer 通过抽象出细粒度的管线架构，内置50多个可自由组合的算子并集成可视化分析与自动评估，实现了高效的“数据处理-模型训练”动态反馈闭环。文章强调，大模型的表现极大程度上取决于“数据配方”，而 Data-Juicer 通过系统化算子设计与超参数优化，能够自动且高效地生成更优的数据混合方案，为大模型研究向“以数据为中心”转型提供了关键的基础设施支撑。

3.Penedo, G., Kydlíček, H., Lozhkov, A., Mitchell, M., Raffel, C., Von Werra, L., & Wolf, T. (2024). The fineweb datasets: Decanting the web for the finest text data at scale. Advances in Neural Information Processing Systems, 37, 30811-30849.
https://arxiv.org/abs/2406.17557 
FineWeb 标志着数据清洗逻辑从早期的“粗暴去噪”向“精准留存”的深刻转变。该研究利用海量快照构建了大规模的预训练数据集，并创新性地利用小型分类器筛选出高质量的教育子集，实证了预训练数据的核心逻辑已不再是单纯删除垃圾内容，而是如何通过精细化筛选来精准保留高质量内容，因为不同的过滤方案不可等价替代，数据质量将直接决定并重塑模型的最终能力分布。

4.Mansour, Y., & Heckel, R. (2024). Measuring bias of web-filtered text datasets and bias propagation through training.
https://openreview.net/forum?id=FDhAngvHuf 
数据清洗和过滤绝不是绝对客观或中性的，它不可避免地会在数据中注入独特的分布偏差。在关于 Web 过滤文本数据集偏见测量的研究中（ICLR 2025），研究人员对包含 FineWeb 在内的多个主流开源预训练数据集进行了跨数据集偏见实证。实验表明，尽管这些数据集采用了高度相似的启发式规则与去重流程，神经网络分类器依然能以极高的准确率判定某条特定文本属于哪个数据集，这种远超人类辨别高精度可分性证明了清洗管线会留下独特的数据集指纹与清洗偏差。

5.Mansour, Y., & Heckel, R. (2026). Measuring Fingerprints of Web-filtered Text Datasets and Fingerprint Propagation Through Training. Advances in Neural Information Processing Systems, 38.
https://proceedings.neurips.cc/paper_files/paper/2025/hash/181f409676bf93986ecdb61e6af254a1-Abstract-Datasets_and_Benchmarks_Track.html 
这种清洗指纹的影响并不仅停留在数据阶段，还会作为“基因”深度隐性传播至模型内部，决定模型最终的生成偏好与行为特征。在 NeurIPS 2025 Spotlight 的后续研究中，研究人员进一步追踪了偏见传播链。实验发现，使用在原始数据集上训练的分类器去识别由不同数据集训练出来的语言模型所随机生成的文本时，分类准确率依然极高，这表明模型生成随机序列时的领域倾向高度印证了其预训练阶段的数据集混合比例，数据清洗不仅改变了数据分布，更污染并决定了最终模型的行为表现。

6.Phatthiyaphaibun, W., Udomcharoenchaikit, C., Singkorapoom, P., Pipatanakul, K., Chuangsuwanich, E., Limkonchotiwat, P., & Nutanong, S. (2025). Mangosteen: An open thai corpus for language model pretraining. arXiv preprint arXiv:2507.14664.
https://arxiv.org/abs/2507.14664 
随着数据清洗从通用去噪走向对清洗偏见的反思，Mangosteen（2025）的研究则进一步将这一领域推向了本土化与场景适配的新高度，彻底破除了“英文中心主义”。该研究针对泰语没有空格分词、不使用句末标点等独特的语言特性，剔除了西方通用清洗管线中不适用的规则，加入了定制的泰语字符比例分类器和针对本地网络赌博、色情内容的过滤器，通过极致脱水打造了高质量的泰语预训练语料库。这一实践深刻表明，预训练数据的清洗必须进行语言与文化的深度适配，单纯依赖西方主导的、语言无关的通用清洗规则，根本无法处理小语种的语言特性与本地特有的有害信息。

去重
1.Khan, A., Underwood, R., Siebenschuh, C., Babuji, Y., Ajith, A., Hippe, K., ... & Foster, I. (2024). Lshbloom: Memory-efficient, extreme-scale document deduplication. arXiv preprint arXiv:2411.04257.
https://arxiv.org/html/2411.04257v3 
针对大规模语料在去重过程中面临的内存瓶颈，LSHBloom 通过将传统 MinHash-LSH 算法与 Bloom Filter 结合，成功克服了传统方案内存占用过高的问题，实现了对 PB 级语料的极端规模文本去重。该框架不仅将去重速度提升了约 2.7 倍，更将磁盘占用骤降至传统方案的 0.6%，在数十亿文档规模下展现出卓越的扩展性。文章的核心观点指出，在大数据时代，去重的主要矛盾已经从单纯的“算法准确性”彻底转变为“系统可扩展性”。

2.Son, Y., Kim, C., & Lee, J. (2025). Fed: Fast and efficient dataset deduplication framework with gpu acceleration. arXiv preprint arXiv:2501.01046.
https://arxiv.org/html/2501.01046v1 
随着数据量向万亿级飙升，去重任务已演变为大模型训练流水线中的高吞吐计算任务，FED 框架为此引入了 GPU 加速机制。该框架通过 GPU 化的签名生成、优化的哈希计算以及 GPU 集群的高效并行设计，实现了相比传统 SlimPajama CPU 去重工具 100 倍以上的吞吐量提升，仅需约 6 小时即可完成 1.2T token 的去重工作，且与标准 MinHash 的去重结果高度一致。文章强调，通过硬件加速提升吞吐量，是解决海量数据预处理效率瓶颈的关键。

3.Penedo, G., Kydlíček, H., Lozhkov, A., Mitchell, M., Raffel, C., Von Werra, L., & Wolf, T. (2024). The fineweb datasets: Decanting the web for the finest text data at scale. Advances in Neural Information Processing Systems, 37, 30811-30849.
https://arxiv.org/abs/2406.17557 
在公开数据集的工业级去重实践中，FineWeb 团队提出了按快照去重（per-snapshot deduplication）的策略，即在每个 Common Crawl 快照内部先进行精细去重，然后再进行跨快照的全局处理。研究团队在构建 15T 数据集的过程中发现，不同的去重策略和阈值选择会显著改变数据的最终组成，进而对训练出模型的性能产生深远影响。文章的核心观点在于，去重不仅是一个缩减数据规模的过程，它还会直接干预并重新塑造模型内部的知识分布。

4.You, D., & Fraiberger, S. (2024). Evaluating deduplication techniques for economic research paper titles with a focus on semantic similarity using nlp and llms. arXiv preprint arXiv:2410.01141.
https://arxiv.org/abs/2410.01141 
传统的字符匹配方法无法识别改写、翻译或释义等深层重复，对此，关于经济学论文题目语义相似度去重的研究，系统地对比了 Levenshtein 距离、余弦相似度、SBERT 语义嵌入以及 LLM 辅助判断等多种技术的表现。实验结果表明，纯字符相似度在面对表达差异时具有局限性，而基于深度学习的语义模型在识别隐性重复上展现出显著优势。文章的核心观点宣示了去重技术的未来走向：文本去重正在加速从浅层的“表面重复”跨越到深层的“语义重复”。

过滤
1.Xie, S. M., Santurkar, S., Ma, T., & Liang, P. S. (2023). Data selection for language models via importance resampling. Advances in Neural Information Processing Systems, 36, 34201-34227.
https://arxiv.org/abs/2302.03169 
Data Selection via Importance Resampling (DSIR) 针对大语言模型训练数据中存在大量冗余与低价值样本的挑战，创新性地提出了“重要性重采样”方法，通过评估数据与目标任务的关联度来动态调整样本权重。在相同的Token预算下，该方法显著提升了模型的最终性能。文章的核心观点在于，数据过滤不应只是被动地“删除低质量数据”，而应演变为根据下游任务需求“主动选择高价值数据”。


2.Albalak, A., Elazar, Y., Xie, S. M., Longpre, S., Lambert, N., Wang, X., ... & Wang, W. Y. (2024). A survey on data selection for language models. arXiv preprint arXiv:2402.16827.
https://arxiv.org/abs/2402.16827 
随着数据选择逐渐成为独立的研究方向，A Survey on Data Selection for Language Models 系统性地梳理了该领域的演进脉络，将过滤方法归纳为基于规则（如长度、语言、URL）、基于代理模型（如困惑度PPL、小模型打分）、基于梯度（如影响函数）以及基于目标任务（如主动选择）四大核心类别。文章的核心贡献在于，论证了数据过滤已正式脱离早期的经验技巧，发展成为一个具备完善理论与方法论支撑的独立研究领域。


3.Jiang, L., & Zhu, Y. (2024). Data Smoothing Filling Method based on ScRNA-Seq Data Zero-Value Identification. arXiv preprint arXiv:2402.09755.
https://arxiv.org/abs/2402.09755 
在探讨具体维度有效性的经验研究中，A Pretrainer's Guide to Training Data 对数据年代、领域覆盖、毒性和质量等多个过滤维度进行了系统性实验，结果发现过于严苛的清洗并不能持续带来性能增益，甚至会因过度过滤而导致模型面临严重的知识覆盖缺失。文章由此提出了关键的性能—覆盖权衡（Performance-Coverage Trade-off）观点，警示研究者盲目追求数据“干净”可能带来的负面效应。


4.Yu, X., Zhang, Z., Niu, F., Hu, X., Xia, X., & Grundy, J. (2024, October). What Makes a High-Quality Training Dataset for Large Language Models: A Practitioners' Perspective. In Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering (pp. 656-668).
https://dl.acm.org/doi/abs/10.1145/3691620.3695061 
从工业界实践视角出发，What Makes a High-Quality Training Dataset for Large Language Models 总结出了一套更具落地指导意义的过滤框架，指出在真实生产环境中，高质量的数据集应当具备正确性、信息密度、多样性、覆盖性和可读性等多个维度的特征。文章的核心观点强调，工业界落地的数据清洗不可能依赖单一的质量指标，而必须采用多指标、多维度的协同过滤。


5.Liangyu, X., Zhang, X., Duan, F., Wang, S., Weng, R., Wang, J., & Cai, X. (2025, November). FIRE: Flexible Integration of Data Quality Ratings for Effective Pretraining. In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (pp. 14532-14552).
https://aclanthology.org/2025.emnlp-main.735/ 
为了解决单指标过滤的局限性，Flexible Integration of Data Quality Ratings for Effective Pretraining 提出了一种创新的多维质量融合方案，将毒性、教育价值、信息密度、来源可靠性及可读性等多种异构的过滤信号集成到统一的框架中，并引入了可调权重机制。实验结果表明，这种融合策略在模型预训练效果上全面优于单一的质量过滤器，揭示了数据过滤从单维评分迈向多维动态融合的必然趋势。

6.Liu, F., Zhou, W., Liu, B., Yu, Z., Zhang, Y., Lin, H., ... & Cao, Y. (2025). Quadmix: Quality-diversity balanced data selection for efficient llm pretraining. arXiv preprint arXiv:2504.16511.
https://arxiv.org/abs/2504.16511 
针对长期以来质量与多样性被割裂优化的痛点，QuaDMix 框架引入了统一的参数化数据采样函数，将多维质量评估与领域分类相结合，实现了质量与多样性的联合优化方案。研究发现，若在固定预算内盲目追求极端的高质量，反而会破坏数据集原有的均衡分布并损害模型的泛化能力。文章的核心观点一针见血地指出，“高质量”并不等同于“最佳训练数据”，只有协同好质量与多样性之间的固有权衡，才能实现最优的预训练效率。  

7.Saada, T. N., Bethune, L., Klein, M., Grangier, D., Cuturi, M., & Ablin, P. (2025). The Data-Quality Illusion: Rethinking Classifier-Based Quality Filtering for LLM Pretraining. arXiv preprint arXiv:2510.00866.
https://arxiv.org/abs/2510.00866 
随着过滤技术的普及，The Data-Quality Illusion 开始对底层机制进行深刻反思，指出当前广泛使用的基于分类器的数据过滤可能存在严重的认知偏差。研究表明，现有的质量分类器在很大程度上只是学会了“模仿”参考语料（如维基百科）的文本分布，而并非真正具备识别数据内在质量的能力。文章的核心观点揭示了所谓的“高质量过滤”在某种程度上只是一种分布匹配的幻觉，呼吁业界重新审视现行的数据评估标准。

8.Ali, M., Brack, M., Lübbering, M., Wendt, E., Khan, A. G., Rutmann, R., ... & Kersting, K. (2025, November). Judging Quality Across Languages: A Multilingual Approach to Pretraining Data Filtering with Language Models. In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (pp. 8870-8909).
https://aclanthology.org/2025.emnlp-main.449/ 
在跨语言场景中，Judging Quality Across Languages 聚焦于多语言预训练语料的清洗困境，探索利用大语言模型（LLM）来跨语言评价文本质量。研究表明，由于文化差异、语法结构以及有害信息定义的系统性不同，传统基于英文构建的过滤规则和分类器在迁移至小语种时会面临严重的性能劣化。文章的核心观点强调，数据过滤绝不能一成不变，必须针对具体的语言和文化背景进行深度适配。

质量评估方法
1.Longpre, S., Yauney, G., Reif, E., Lee, K., Roberts, A., Zoph, B., ... & Ippolito, D. A Pretrainer’s Guide to Training Data.
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://gyauney.github.io/papers/a-pretrainers-slides.pdf

2.Yu, X., Zhang, Z., Niu, F., Hu, X., Xia, X., & Grundy, J. (2024, October). What Makes a High-Quality Training Dataset for Large Language Models: A Practitioners' Perspective. In Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering (pp. 656-668).
https://dl.acm.org/doi/abs/10.1145/3691620.3695061 

3.Chen, D., Huang, Y., Ma, Z., Chen, H., Pan, X., Ge, C., ... & Zhou, J. (2024, June). Data-juicer: A one-stop data processing system for large language models. In Companion of the 2024 International Conference on Management of Data (pp. 120-134).
https://dl.acm.org/doi/abs/10.1145/3626246.3653385 


4.Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-eval: Nlg evaluation using gpt-4 with better human alignment, 2023. arXiv preprint arXiv:2303.16634, 12, 1.
https://arxiv.org/abs/2303.16634 

5.Saada, T. N., Bethune, L., Klein, M., Grangier, D., Cuturi, M., & Ablin, P. (2025). The Data-Quality Illusion: Rethinking Classifier-Based Quality Filtering for LLM Pretraining. arXiv preprint arXiv:2510.00866.
https://arxiv.org/abs/2510.00866 

6.Zhang, Q., Garg, A., Foerster, J., Chatterji, N., Malik, K., & Lewis, M. (2026). An Empirical Study on Noisy Data and LLM Pretraining Loss Divergence. arXiv preprint arXiv:2602.02400.
https://arxiv.org/abs/2602.02400 

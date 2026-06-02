# 中文分词（CRF - NumPy 实现）

简要说明
----------------
这是一个基于线性链条件随机场（CRF）的中文分词课程项目实现，完整流水线包含：数据预处理（dataloader）、特征抽取、基于 NumPy 的 CRF 模型、训练脚本与预测脚本。目标是提供可复现的最小可运行实现，便于学习算法细节。

目录结构（主要文件）
----------------
- `data/`：原始与处理后数据（示例：`data/train/msr_training.utf8`、`data/train/msr_training_processed.utf8`）
- `model/`：训练生成的模型参数（默认：`model/W.npy`, `model/T.npy`, `model/feat2id.txt`）
- `src/dataloader.py`：处理 MSR 格式并生成 BMES 字符级标签文件
- `src/extract_features.py`：基于位置的原子特征（P/C/N），构建 feature->id 映射
- `src/crf_model.py`：NumPy 实现的线性链 CRF（前向/后向、边/点级边际、Viterbi、梯度）
- `src/train.py`：训练入口脚本，负责构建特征、训练并保存模型
- `src/predict.py`：预测入口，加载模型并对输入句子输出分词结果

环境与依赖
----------------
- Python 3.8+

```bash
pip install numpy
```

数据格式
----------------
- 原始 MSR 文件为词语空格分隔（如 `data/train/msr_training.utf8`），`src/dataloader.py` 会：
  - 去除行首多余引号、按标点断句；
  - 将每个词转为字符级 BMES 标签（每行：一个字 空格 标签）；
  - 句子间用空行分隔，输出文件示例：`data/train/msr_training_processed.utf8`。

运行说明
----------------
训练（示例）：

```bash
python src/train.py --epochs 20 --lr 0.5 --max-sents 200000 --model-dir model
```

训练输出会把模型参数保存到 `model/`：`W.npy`, `T.npy`, `feat2id.txt`。

预测（示例）：

```bash
python src/predict.py "我爱自然语言处理"
# 或者交互式/命令行传入句子
```

模型与特征说明
----------------
- 标签集：4 类标注（B, M, E, S）。
- 特征：当前位置的三个原子特征——前一个字 `P=<prev>`，当前字 `C=<curr>`，下一个字 `N=<next>`（含 `<BOS>`/`<EOS>` 边界标记）。
- 发射分数：将当前位置所有 feature 对应的权重向量相加得到每个标签的发射分数。
- 转移矩阵 `T`：4x4 可学习的标签转移分数矩阵。

评估建议
----------------
- 训练日志中常见的指标为负对数似然（NLL），建议按 token 或按句子归一化以便比较（即 NLL/词数）。
- 对齐分词质量请使用分词 F1（基于预测与真值的词边界匹配）。

已知限制与改进方向
----------------
- 当前训练为逐句 SGD（无小批次、简单学习率），可改进为 mini-batch、Adam/Adagrad、学习率调度。
- 预测时对未见特征采用丢弃策略，建议增设 `<UNK>` 特征或使用特征哈希处理稀疏项。
- 增加验证集与早停、保存最佳模型可改善泛化与实验可重复性。

如何进一步使用我能帮忙的内容
----------------
- 我可以：
  - 把 `src/train.py` 改为包含验证集并输出归一化 NLL 与 F1；
  - 增加 `<UNK>` 特征或特征哈希实现；
  - 编写评测脚本用于计算分词 F1（给出 test 文件即可）。

如果需要我现在做其中某项，请告诉我你优先的下一步。

---
项目目录中 README 已添加。如需把 README 调整为课程报告格式或加入实验结果截图，请指示。

打包为 Windows 可执行文件 (EXE)
----------------
本仓库已提供一个演示型 CLI 入口 `src/cli.py`，和便捷的打包脚本 `build_exe.bat`。打包步骤（在 Windows 下）：

1. 安装依赖：

```powershell
pip install -r requirements.txt
```

2. 运行打包脚本（会安装 PyInstaller 并生成单文件 exe）：

```powershell
.\build_exe.bat
```

3. 打包结果：
- 可执行文件位于 `dist\crf_segmenter.exe`，数据目录 `data\` 与模型目录 `model\` 会被一并包含到 exe 的搜索路径中（PyInstaller 打包细节请参阅 PyInstaller 文档）。

注意事项：
- 若希望手动控制打包选项，可直接运行：

```powershell
pyinstaller --onefile --add-data "data;data" --add-data "model;model" --name crf_segmenter src\cli.py
```
- 打包过程可能需要联网安装 PyInstaller，如网络受限请先在本地准备好环境或手动安装 `pyinstaller`。

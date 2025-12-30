# 机器学习Lab3 - 聚类实验

## 实验概述
本实验使用 **Mall Customers (购物中心客户)** 数据集，对比分析两种聚类算法：
- **K-Means**: 经典的基于距离的聚类算法
- **DBSCAN**: 基于密度的聚类算法

## 实验流程
1. **Data Prepare** - 加载购物中心客户数据
2. **Data Preprocess** - 数据清洗、标准化、降维可视化
3. **Model Construct** - 构建K-Means和DBSCAN模型
4. **Train & Test** - 执行聚类并评估性能
5. **Plot Result** - 多角度可视化聚类结果
6. **Optimize & Review** - 参数优化与算法对比分析

## 数据集特征
- **Age**: 客户年龄
- **Annual_Income_k**: 年收入（千美元）
- **Spending_Score**: 消费评分（1-100）

## 运行方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行实验
```bash
python clustering_experiment.py
```

### 3. 查看结果
实验完成后会生成以下可视化文件：
- `01_data_distribution.png` - 原始数据分布（PCA降维）
- `02_optimal_k_selection.png` - K值选择（肘部法则 + 轮廓系数）
- `03_clustering_results.png` - 聚类结果对比
- `04_customer_feature_analysis.png` - 客户特征多维度分析

## 评估指标
- **轮廓系数 (Silhouette Score)**: 衡量簇内紧密度和簇间分离度，范围[-1, 1]，越接近1越好
- **Calinski-Harabasz指数**: 簇间离散度与簇内离散度的比值，越大越好
- **Davies-Bouldin指数**: 簇内距离与簇间距离的平均比值，越小越好

## 算法对比

### K-Means
**优点**:
- 计算效率高，适合大规模数据
- 结果稳定，易于理解
- 适合发现球形簇

**缺点**:
- 需要预设簇数量K
- 对异常值敏感
- 只能发现凸形簇

### DBSCAN
**优点**:
- 无需预设簇数量
- 可发现任意形状的簇
- 能识别噪声点
- 对异常值鲁棒

**缺点**:
- 参数选择较困难（eps, min_samples）
- 密度不均匀时效果不佳
- 高维数据性能下降

## 商业应用
通过聚类分析可识别不同客户群体：
1. **高价值客户**: 高收入 + 高消费 → 提供VIP服务
2. **潜力客户**: 高收入 + 低消费 → 重点营销转化
3. **培养客户**: 低收入 + 低消费 → 培养品牌忠诚度

## 参数调优建议
- **K-Means**: 使用肘部法则或轮廓系数确定最优K值
- **DBSCAN**: 
  - `eps`: 建议先用K距离图确定，本实验使用0.5
  - `min_samples`: 通常设为数据维度+1，本实验使用5

## 技术栈
- Python 3.8+
- NumPy, Pandas: 数据处理
- Scikit-learn: 聚类算法
- Matplotlib, Seaborn: 数据可视化

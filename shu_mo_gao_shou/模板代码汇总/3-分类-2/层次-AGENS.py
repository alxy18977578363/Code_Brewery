import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 使用 AGENS 聚类法进行分类
agens = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=10, random_state=42)
agens.fit(X)
y_agens = pairwise_distances_argmin(X, agens.cluster_centers_, metric='euclidean')

# 可视化输出
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_agens, cmap='viridis')  # 绘制聚类结果
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('AGENS Clustering on Iris Dataset')
plt.show()
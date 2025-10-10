import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 使用 k-PROTOTYPE 聚类法进行分类
kprototype = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=10, random_state=42)
kprototype.fit(X)
y_kprototype = pairwise_distances_argmin(X, kprototype.cluster_centers_, metric='euclidean')

# 可视化输出
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_kprototype, cmap='viridis')  # 绘制聚类结果
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('k-PROTOTYPE Clustering on Iris Dataset')
plt.show()
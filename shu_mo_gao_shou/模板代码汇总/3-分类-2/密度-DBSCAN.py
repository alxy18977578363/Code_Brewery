import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 使用 DBSCAN 聚类法进行分类
dbscan = DBSCAN(eps=0.5, min_samples=5)
dbscan.fit(X)
y_dbscan = dbscan.labels_

# 可视化输出
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_dbscan, cmap='viridis')  # 绘制聚类结果
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('DBSCAN Clustering on Iris Dataset')
plt.show()
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# 加载鸢尾花数据集  
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 将数据集分为训练集和测试集  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 使用K-means++算法进行聚类  
kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=10)
kmeans.fit(X_train)

# 对测试集进行预测  
y_pred = kmeans.predict(X_test)

# 可视化结果  
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')  # 原始数据点  
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_pred, cmap='viridis', alpha=0.5)  # 聚类结果  
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('K-means++ Clustering on Iris Dataset')
plt.show()
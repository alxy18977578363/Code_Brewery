import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris

# 加载鸢尾花数据集  
iris = load_iris()
X = iris.data
y = iris.target

# 使用K-means聚类算法进行分类  
kmeans = KMeans(n_clusters=3)
kmeans.fit(X)
y_kmeans = kmeans.predict(X)

# 创建颜色列表，每个颜色对应于一个类别  
colors = ['red', 'blue', 'green']

# 绘制聚类结果  
for i, color in zip(range(3), colors):
    plt.scatter(X[y_kmeans == i, 0], X[y_kmeans == i, 1], c=color, label=iris.target_names[i])

plt.legend()
plt.show()
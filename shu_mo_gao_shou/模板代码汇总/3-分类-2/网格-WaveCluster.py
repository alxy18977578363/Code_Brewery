import pandas as pd
from sklearn.cluster import SpectralClustering
import matplotlib.pyplot as plt

data = pd.read_csv(r"C:\Users\Administrator\Desktop\鸢尾花数据集.csv")
X = data[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']].values
y = data['species'].values

# 使用 SpectralClustering 进行聚类
spectral_clf = SpectralClustering(n_clusters=3, affinity='nearest_neighbors', n_init=10)
spectral_clf.fit(X)
y_spectral = spectral_clf.labels_

# 可视化输出
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=y_spectral, cmap='viridis')  # 绘制聚类结果
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Spectral Clustering on Local Dataset')
plt.show()
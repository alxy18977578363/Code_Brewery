import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.mixture import BayesianGaussianMixture
import matplotlib.pyplot as plt

# 加载鸢尾花数据集
data=pd.read_csv(r"C:\Users\Administrator\Desktop\演示数据\a08a1080b88344b0c8a7-0e7a9b0a5d22642a06d3d5b9bcbad9890c8ee534\鸢尾花数据集.csv")
X = data[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']].values
y = data['species'].values


# 使用贝叶斯判别法进行分类
bgm = BayesianGaussianMixture(n_components=3)  # 假设有3个类别
bgm.fit(X, y)
predicted_labels = bgm.predict(X)

# 可视化分类结果
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=predicted_labels, cmap='viridis')  # 绘制分类后的数据点
plt.xlabel('Sepal Length')
plt.ylabel('Sepal Width')
plt.title('Bayesian Gaussian Mixture on Iris Dataset')
plt.show()
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import matplotlib.pyplot as plt

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data
y = iris.target

# 使用Fisher判别法进行降维和分类
lda = LinearDiscriminantAnalysis()
X_lda = lda.fit_transform(X, y)

# 可视化降维后的数据
plt.figure(figsize=(8, 6))
plt.scatter(X_lda[:, 0], X_lda[:, 1], c=y, cmap='viridis')  # 绘制降维后的数据点
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Fisher Discriminant Analysis on Iris Dataset')
plt.show()
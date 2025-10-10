import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# 定义房屋特征数据
area = [120, 90, 100, 80, 110]
rooms = [3, 2, 2, 1, 3]
distance = [10, 5, 8, 6, 12]

# 创建特征矩阵
X = np.array([area, rooms, distance]).T

# 执行主成分分析
pca = PCA()
principal_components = pca.fit_transform(X)

# 提取特征权重系数
feature_names = ['Area', 'Rooms', 'Distance']
weights = pca.components_

# 绘制权重系数条形图
plt.bar(feature_names, weights[0], alpha=0.5, label='PC1')
plt.bar(feature_names, weights[1], alpha=0.5, label='PC2')
plt.xlabel('Features')
plt.ylabel('Weight Coefficients')
plt.title('PCA - Feature Weights')
plt.legend()
plt.show()
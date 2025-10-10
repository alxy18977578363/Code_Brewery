import numpy as np
import matplotlib.pyplot as plt

# 构建AHP矩阵
ahp_matrix = np.array([[1, 3, 5, 7],
                      [1/3, 1, 3, 5],
                      [1/5, 1/3, 1, 3],
                      [1/7, 1/5, 1/3, 1]])

# 计算权重向量
eigenvalues, eigenvectors = np.linalg.eig(ahp_matrix.T)
max_eigenvalue_index = np.argmax(eigenvalues)
weights = eigenvectors[:, max_eigenvalue_index]
weights = weights / sum(weights)

# 旅游目的地列表
destinations = ['Destination A', 'Destination B', 'Destination C', 'Destination D']

# 可视化输出
plt.bar(destinations, weights)
plt.xlabel('Destinations')
plt.ylabel('Weights')
plt.title('Weight Distribution of Destinations')
plt.show()
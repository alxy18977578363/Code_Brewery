import numpy as np
import matplotlib.pyplot as plt

# 构建AHP矩阵
ahp_matrix = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                      [1/2, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                      [1/3, 1/2, 1, 2, 3, 4, 5, 6, 7, 8],
                      [1/4, 1/3, 1/2, 1, 2, 3, 4, 5, 6, 7],
                      [1/5, 1/4, 1/3, 1/2, 1, 2, 3, 4, 5, 6],
                      [1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 3, 4, 5],
                      [1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 3, 4],
                      [1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 3],
                      [1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1, 2],
                      [1/10, 1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1]])

# 计算权重向量
eigenvalues, eigenvectors = np.linalg.eig(ahp_matrix.T)
max_eigenvalue_index = np.argmax(eigenvalues)
weights = eigenvectors[:, max_eigenvalue_index]
weights = weights / sum(weights)

# 生成目的地列表
destinations = ['Destination {}'.format(i) for i in range(1, 11)]

# 可视化输出
plt.bar(destinations, weights)
plt.xlabel('Destinations')
plt.ylabel('Weights')
plt.title('Weight Distribution of Destinations')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
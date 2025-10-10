import numpy as np
import matplotlib.pyplot as plt

def pca(data, num_components):
    # 数据标准化
    mean = np.mean(data, axis=0)
    centered_data = data - mean

    # 计算协方差矩阵
    covariance_matrix = np.cov(centered_data, rowvar=False)

    # 计算特征值和特征向量
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    # 对特征向量按特征值降序排序
    sorted_indices = np.argsort(eigenvalues)[::-1]
    sorted_eigenvalues = eigenvalues[sorted_indices]
    sorted_eigenvectors = eigenvectors[:, sorted_indices]

    # 选择前num_components个主成分
    selected_eigenvectors = sorted_eigenvectors[:, :num_components]

    # 计算投影后的数据
    projected_data = np.dot(centered_data, selected_eigenvectors)

    # 返回主成分和投影后的数据
    return selected_eigenvectors, projected_data

def plot_weight_coefficients(eigenvectors, feature_names):
    num_components, num_features = eigenvectors.shape

    # 绘制权重系数图
    plt.figure(figsize=(10, 6))
    for i in range(num_components):
        plt.arrow(0, 0, eigenvectors[i, 0], eigenvectors[i, 1], head_width=0.02, head_length=0.03, color='r')
        for j in range(num_features):
            plt.text(eigenvectors[i, 0] + 0.05, eigenvectors[i, 1] + 0.05, feature_names[j])
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.grid(True)
    plt.show()

# 数据
data = np.array([[100000, 4.5, 8, 9],
                 [80000, 3.2, 6, 7],
                 [120000, 4.8, 9, 9.5],
                 [95000, 3.9, 7.5, 8],
                 [110000, 4.2, 8.5, 9]])

feature_names = ['Sales', 'Customer Satisfaction', 'Efficiency', 'Teamwork']

# 执行主成分分析
num_components = 2
eigenvectors, projected_data = pca(data, num_components)

# 绘制权重系数图
plot_weight_coefficients(eigenvectors, feature_names)
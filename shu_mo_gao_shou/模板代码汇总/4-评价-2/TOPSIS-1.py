import numpy as np
import matplotlib.pyplot as plt

def topsis(data, weights):
    # 归一化处理
    normalized_data = data / np.sqrt(np.sum(data**2, axis=0))

    # 加权归一化数据
    weighted_normalized_data = normalized_data * weights

    # 理想解和负理想解
    ideal_solution = np.max(weighted_normalized_data, axis=0)
    negative_ideal_solution = np.min(weighted_normalized_data, axis=0)

    # 计算每个评价对象到理想解和负理想解的距离
    distance_to_ideal = np.sqrt(np.sum((weighted_normalized_data - ideal_solution)**2, axis=1))
    distance_to_negative_ideal = np.sqrt(np.sum((weighted_normalized_data - negative_ideal_solution)**2, axis=1))

    # 计算接近程度
    similarity = distance_to_negative_ideal / (distance_to_ideal + distance_to_negative_ideal)

    return similarity

# 示例数据
data = np.array([[1080, 2.4, 20],
                 [1440, 2.8, 16],
                 [720, 2.2, 24],
                 [1080, 2.6, 18],
                 [1440, 2.5, 22]])

# 权重
weights = np.array([0.4, 0.4, 0.2])

# 执行TOPSIS方法
similarity = topsis(data, weights)

# 绘制权重系数图
feature_names = ['Screen Resolution', 'Processor Speed', 'Battery Life']
plt.bar(feature_names, weights)
plt.xlabel('Feature')
plt.ylabel('Weight')
plt.title('Weight Coefficients')
plt.grid(True)
plt.show()

print('Similarity:', similarity)
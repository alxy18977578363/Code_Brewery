import numpy as np
import matplotlib.pyplot as plt

# 原始数据
reference_sequence = np.array([80, 75, 90, 85, 70])
sequences = np.array([[75, 70, 80, 80, 65],
                      [65, 80, 70, 75, 80],
                      [70, 75, 85, 70, 75]])

# 归一化处理
normalized_reference = (reference_sequence - np.min(reference_sequence)) / (np.max(reference_sequence) - np.min(reference_sequence))
normalized_sequences = (sequences - np.min(sequences, axis=1).reshape(-1, 1)) / (np.max(sequences, axis=1).reshape(-1, 1) - np.min(sequences, axis=1).reshape(-1, 1))

# 计算关联矩阵
correlation_matrix = np.zeros((len(sequences), len(reference_sequence)))
for i in range(len(sequences)):
    for j in range(len(reference_sequence)):
        correlation_matrix[i, j] = np.min([np.abs(normalized_reference[j] - normalized_sequences[i, j]),
                                          np.abs(normalized_reference[j] - np.max(normalized_sequences[i, :j+1])),
                                          np.abs(normalized_reference[j] - np.min(normalized_sequences[i, j:]))])

# 计算关联度指数
correlation_coefficients = np.mean(correlation_matrix, axis=1)

# 可视化输出
plt.figure(figsize=(8, 6))
plt.plot(reference_sequence, label='Reference Sequence')
for i, seq in enumerate(sequences):
    plt.plot(seq, label='Sequence {}'.format(i+1))
plt.xlabel('Time')
plt.ylabel('Environmental Quality')
plt.title('Environmental Quality Comparison')
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 6))
plt.bar(range(len(correlation_coefficients)), correlation_coefficients)
plt.xlabel('Sequence index')
plt.ylabel('Correlation Coefficient')
plt.title('Correlation Coefficient Comparison')
plt.xticks(range(len(correlation_coefficients)), ['Sequence {}'.format(i+1) for i in range(len(correlation_coefficients))])
plt.tight_layout()
plt.show()
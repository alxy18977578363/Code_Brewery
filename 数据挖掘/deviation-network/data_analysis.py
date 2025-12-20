import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# 加载数据集
data = np.load('phase1_gdata.npz')

print("=== 数据集基本信息 ===")
print(f"数据集包含的keys: {list(data.keys())}")
print()

# 节点特征分析
x = data['x']
print(f"节点特征矩阵形状: {x.shape}")
print(f"节点数量: {x.shape[0]}")
print(f"特征维度: {x.shape[1]}")
print(f"特征值范围: [{x.min():.4f}, {x.max():.4f}]")
print(f"是否包含缺失值: {np.isnan(x).any()}")
print()

# 标签分析
y = data['y']
print(f"标签数组形状: {y.shape}")
# 如果y是二维数组，将其扁平化
if y.ndim > 1:
    y = y.flatten()
    print(f"扁平化后标签数组形状: {y.shape}")

label_counts = Counter(y)
print(f"标签分布: {dict(label_counts)}")
# 计算各类别比例（排除测试样本-100）
train_labels = y[y != -100]
train_label_counts = Counter(train_labels)
print(f"训练集标签分布: {dict(train_label_counts)}")
print(f"测试样本数量: {(y == -100).sum()}")
print()

# 边信息分析
edge_index = data['edge_index']
edge_type = data['edge_type']
edge_timestamp = data['edge_timestamp']

print(f"边索引矩阵形状: {edge_index.shape}")
print(f"边数量: {edge_index.shape[0]}")
print(f"边类型数组形状: {edge_type.shape}")

# 如果edge_type是二维数组，将其扁平化
if edge_type.ndim > 1:
    edge_type = edge_type.flatten()
    print(f"扁平化后边类型数组形状: {edge_type.shape}")

# 如果edge_timestamp是二维数组，将其扁平化
if edge_timestamp.ndim > 1:
    edge_timestamp = edge_timestamp.flatten()
    print(f"扁平化后边时间戳数组形状: {edge_timestamp.shape}")

print(f"边类型分布: {dict(Counter(edge_type))}")
print(f"边时间戳范围: [{edge_timestamp.min()}, {edge_timestamp.max()}]")
print()

# 训练/测试掩码分析
train_mask = data['train_mask']
test_mask = data['test_mask']
print(f"训练样本数量: {len(train_mask)}")
print(f"测试样本数量: {len(test_mask)}")
print(f"训练样本占比: {len(train_mask) / x.shape[0]:.2%}")
print(f"测试样本占比: {len(test_mask) / x.shape[0]:.2%}")
print()

# 图结构分析
print("=== 图结构分析 ===")
# 计算节点度数
degrees = np.bincount(edge_index.flatten(), minlength=x.shape[0])
print(f"平均度数: {degrees.mean():.2f}")
print(f"最大度数: {degrees.max()}")
print(f"最小度数: {degrees.min()}")
print(f"度数标准差: {degrees.std():.2f}")

# 计算入度和出度
in_degrees = np.bincount(edge_index[:, 1], minlength=x.shape[0])
out_degrees = np.bincount(edge_index[:, 0], minlength=x.shape[0])
print(f"平均入度: {in_degrees.mean():.2f}")
print(f"平均出度: {out_degrees.mean():.2f}")
print()

# 检查数据一致性
print("=== 数据一致性检查 ===")
print(f"边索引最大值是否小于节点数: {edge_index.max() < x.shape[0]}")
print(f"训练掩码最大值是否小于节点数: {train_mask.max() < x.shape[0]}")
print(f"测试掩码最大值是否小于节点数: {test_mask.max() < x.shape[0]}")
print(f"训练掩码和测试掩码是否有重叠: {len(set(train_mask) & set(test_mask)) > 0}")

# 可视化数据分布
plt.figure(figsize=(15, 10))

# 1. 标签分布
plt.subplot(2, 3, 1)
labels = list(train_label_counts.keys())
counts = list(train_label_counts.values())
plt.bar(labels, counts)
plt.title('训练集标签分布')
plt.xlabel('标签类别')
plt.ylabel('数量')

# 2. 边类型分布
plt.subplot(2, 3, 2)
edge_types = list(Counter(edge_type).keys())
edge_counts = list(Counter(edge_type).values())
plt.bar(edge_types, edge_counts)
plt.title('边类型分布')
plt.xlabel('边类型')
plt.ylabel('数量')

# 3. 度数分布
plt.subplot(2, 3, 3)
plt.hist(degrees, bins=50, alpha=0.7)
plt.title('节点度数分布')
plt.xlabel('度数')
plt.ylabel('频次')
plt.yscale('log')

# 4. 边时间戳分布
plt.subplot(2, 3, 4)
plt.hist(edge_timestamp, bins=50, alpha=0.7)
plt.title('边时间戳分布')
plt.xlabel('时间戳(天)')
plt.ylabel('频次')

# 5. 特征统计
plt.subplot(2, 3, 5)
feature_means = x.mean(axis=0)
plt.bar(range(len(feature_means)), feature_means)
plt.title('各特征维度均值')
plt.xlabel('特征索引')
plt.ylabel('均值')

# 6. 入度vs出度散点图
plt.subplot(2, 3, 6)
plt.scatter(in_degrees, out_degrees, alpha=0.5, s=1)
plt.xlabel('入度')
plt.ylabel('出度')
plt.title('入度vs出度关系')

plt.tight_layout()
plt.savefig('data_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("数据分析完成！可视化图表已保存为 data_analysis.png")
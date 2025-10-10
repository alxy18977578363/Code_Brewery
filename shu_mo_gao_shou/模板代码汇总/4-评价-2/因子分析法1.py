import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from factor_analyzer import FactorAnalyzer

# 数据
data = np.array([[1, 2, 3, 4, 5],
                 [5, 4, 3, 2, 1],
                 [2, 1, 3, 5, 4],
                 [4, 5, 1, 3, 2],
                 [3, 2, 4, 1, 5]])

# 将数据转换为DataFrame格式
df = pd.DataFrame(data, columns=['Product1', 'Product2', 'Product3', 'Product4', 'Product5'])

# 使用因子分析进行因子提取
n_factors = df.shape[1]  # 与数据集的列数相同
fa = FactorAnalyzer(n_factors=n_factors, rotation=None)
fa.fit(df)

# 计算因子载荷矩阵
loadings = fa.loadings_

# 绘制权重系数图
fig, ax = plt.subplots()
ax.imshow(loadings, cmap='hot', interpolation='none')
ax.set_xticks(range(loadings.shape[1]))
ax.set_yticks(range(loadings.shape[0]))
ax.set_xticklabels(df.columns)
ax.set_yticklabels([f"Factor {i+1}" for i in range(loadings.shape[0])])
plt.colorbar(ax.imshow(loadings, cmap='hot', interpolation='none'), ax=ax)
plt.title('Factor Loadings')
plt.show()
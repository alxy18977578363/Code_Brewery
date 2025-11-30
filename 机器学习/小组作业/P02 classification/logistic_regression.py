import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.examples.tutorials.mnist import input_data
import pickle
import time

'''
逻辑回归模型: 最简单的线性分类器
预期效果: 准确率约 92-93%
优点: 训练速度快,可解释性强
缺点: 对非线性特征学习能力弱
'''

print("="*80)
print("逻辑回归模型 - MNIST 手写数字识别")
print("="*80)

# 加载数据
data_dir = './MNIST_DATA'
mnist = input_data.read_data_sets(data_dir, one_hot=False)

# 准备训练数据
X_train = mnist.train.images  # (55000, 784)
y_train = mnist.train.labels  # (55000,)
X_test = mnist.test.images    # (10000, 784)
y_test = mnist.test.labels    # (10000,)

print(f"\n训练集大小: {X_train.shape}")
print(f"测试集大小: {X_test.shape}")

# 创建逻辑回归模型
print("\n开始训练逻辑回归模型...")
start_time = time.time()

model = LogisticRegression(
    max_iter=100,           # 最大迭代次数
    solver='lbfgs',         # 优化算法
    multi_class='multinomial',  # 多分类策略
    verbose=1,              # 显示训练过程
    n_jobs=-1               # 使用所有CPU核心
)

model.fit(X_train, y_train)

train_time = time.time() - start_time
print(f"训练完成! 耗时: {train_time:.2f} 秒")

# 预测
print("\n在测试集上评估...")
y_pred = model.predict(X_test)

# 计算准确率
accuracy = accuracy_score(y_test, y_pred)
print(f"\n测试集准确率: {accuracy:.4f} ({accuracy*100:.2f}%)")

# 详细分类报告
print("\n分类报告:")
print(classification_report(y_test, y_pred, digits=4))

# 混淆矩阵
print("\n混淆矩阵:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# 保存模型
model_path = './models/logistic_regression.pkl'
import os
os.makedirs('./models', exist_ok=True)
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\n模型已保存到: {model_path}")

print("\n" + "="*80)
print("逻辑回归模型训练完成!")
print("="*80)
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from tensorflow.examples.tutorials.mnist import input_data
import pickle
import time

'''
支持向量机模型: 经典的分类算法
预期效果: 准确率约 94-95%
优点: 对小样本效果好,泛化能力强
缺点: 训练速度较慢,内存占用大
'''

print("="*80)
print("支持向量机 (SVM) - MNIST 手写数字识别")
print("="*80)

# 加载数据
data_dir = './MNIST_DATA'
mnist = input_data.read_data_sets(data_dir, one_hot=False)

# 为了加快训练速度,使用部分数据
sample_size = 10000  # 使用 10000 个训练样本
X_train = mnist.train.images[:sample_size]
y_train = mnist.train.labels[:sample_size]
X_test = mnist.test.images
y_test = mnist.test.labels

print(f"\n训练集大小: {X_train.shape}")
print(f"测试集大小: {X_test.shape}")

# 创建 SVM 模型
print("\n开始训练 SVM 模型...")
print("注意: SVM 训练较慢,请耐心等待...")
start_time = time.time()

model = SVC(
    kernel='rbf',      # 径向基核函数
    C=5.0,             # 正则化参数
    gamma='scale',     # 核函数系数
    verbose=True       # 显示训练过程
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

# 保存模型
model_path = './models/svm.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\n模型已保存到: {model_path}")

print("\n" + "="*80)
print("SVM 模型训练完成!")
print("="*80)